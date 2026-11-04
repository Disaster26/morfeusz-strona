<?php
/* Formularz kontaktowy Zakładu Pogrzebowego MORFEUSZ - wysyłka z serwera strony (zamiast FormSubmit).
   Wzór: Wylinka/strona/public/wyslij.php (bez załączników - formularz ich nie ma).
   mail() BEZ parametru -f (serwery odrzucają nadawcę koperty bez skrzynki); From = adres w domenie strony.

   Przyjmuje POST z /kontakt/ (application/x-www-form-urlencoded albo multipart/form-data):
   z JS (nagłówek Accept: application/json albo X-Requested-With) -> odpowiedź JSON {"success":true|false,...},
   bez JS -> prosta strona HTML. Wysyła powiadomienie do ODBIORCA i - jeśli wolno - neutralne potwierdzenie do klienta.

   Zabezpieczenia (kolejność):
   1. tylko POST (i GET ?znacznik=1), inne metody -> 405; za duże żądanie -> 413;
   2. Origin, jeśli jest, musi wskazywać https://zpmorfeusz.czest.pl (w trybie testowym także localhost) -> inaczej 403;
   3. znacznik czasu _z (HMAC z sieci klienta, GET wyslij.php?znacznik=1): z JS ZAWSZE wymagany, wiek ZNACZNIK_MIN..ZNACZNIK_MAX s;
      bez JS - wymagany, gdy brak Origin; znacznik jednorazowy (zuzyte.json);
   4. honeypot (_honey), walidacja pól, limit z jednej sieci (IPv6 /64), łączny limit powiadomień na godzinę i dobę;
   5. potwierdzenie do klienta tylko przy poprawnym znaczniku, bez cytowania czegokolwiek, co wpisał nadawca,
      max 1 na adres e-mail na dobę i LIMIT_POTWIERDZEN na godzinę łącznie.

   Sekret HMAC: plik _limity/_sekret_morfeusz.php (wgrywany razem ze stroną, katalog zablokowany w .htaccess, poza repozytorium)
   albo ../_sekret_morfeusz.php nad webrootem; gdy brak obu - losowy, tworzony przy pierwszym uruchomieniu.
   Limity: pliki JSON (flock) w ../_limity, ./_limity albo katalogu tymczasowym - tylko skróty HMAC i godziny.

   Tryb testowy: zmienna środowiskowa MORFEUSZ_MAIL_DO_PLIKU=<katalog> -> zamiast mail() zapis .eml do katalogu
   i dopuszczony Origin http://localhost; opcjonalnie MORFEUSZ_KATALOG_LIMITOW=<katalog>. Na serwerze tych zmiennych nie ma.
   Skrypt nie wymaga rozszerzenia mbstring. */

const ODBIORCA      = 'zpmorfeusz@onet.eu';               // tu przychodzą zgłoszenia
const NADAWCA       = 'formularz@zpmorfeusz.czest.pl';    // From obu maili (domena strony)
const NADAWCA_NAZWA = 'Zakład Pogrzebowy MORFEUSZ';
const LIMIT = 3;                    // zgłoszeń z jednej sieci klienta na OKNO
const OKNO = 3600;
const LIMIT_BEZ_JS = 2;             // wysyłka bez znacznika (bez JS) - na godzinę
const LIMIT_GLOBALNY_H = 20;        // powiadomień łącznie na godzinę
const LIMIT_GLOBALNY_D = 60;        // ... i na dobę
const LIMIT_POTWIERDZEN = 5;        // potwierdzeń do klientów na godzinę łącznie
const POTW_NA_ADRES = 86400;        // jedno potwierdzenie na adres e-mail na dobę
const MAX_ZADANIA = 64 * 1024;      // formularz tekstowy - całe żądanie
const DOMENY = '#^https://(www\.)?zpmorfeusz\.czest\.pl(/|$)#';
const SEKRET_PLIK = '_sekret_morfeusz.php';
const ZNACZNIK_MIN = 3;
const ZNACZNIK_MAX = 7200;
const TELEFON = '601 460 964';
const TELEFON_HREF = 'tel:+48601460964';

date_default_timezone_set('Europe/Warsaw');
header('X-Robots-Tag: noindex');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');
header('Referrer-Policy: strict-origin-when-cross-origin');
header_remove('X-Powered-By');
$DEV = (string) getenv('MORFEUSZ_MAIL_DO_PLIKU');
$METODA = $_SERVER['REQUEST_METHOD'] ?? '';
$JSON = stripos($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json') !== false || !empty($_SERVER['HTTP_X_REQUESTED_WITH']);

function h($s) { return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8'); }
function dziennik($s) { error_log('morfeusz formularz: ' . $s); }   // bez danych osobowych
function dlugosc($s) { return (int) preg_match_all('/./us', (string) $s); }
function utnij($s, $max) { return preg_match('/^.{0,' . (int) $max . '}/us', (string) $s, $m) ? $m[0] : ''; }

function odpowiedz($ok, $kod = 200, $extra = []) {
    global $JSON;
    http_response_code($kod);
    if ($kod === 405) header('Allow: GET, POST');
    if ($JSON) {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['success' => $ok] + $extra, JSON_UNESCAPED_UNICODE);
        exit;
    }
    $tel = 'prosimy zadzwonić: ' . TELEFON . ' (całą dobę).';
    if ($ok) {
        $t = 'Dziękujemy, wiadomość została wysłana. Odpowiemy najszybciej, jak to możliwe.'
           . (!empty($extra['potwierdzenie']) ? ' Potwierdzenie wysłaliśmy na podany adres - jeśli go nie widać, prosimy sprawdzić folder SPAM.' : '')
           . ' W pilnej sprawie ' . $tel;
    } else {
        $teksty = [
            422 => 'Coś jest nie tak z danymi w formularzu. Prosimy wrócić i sprawdzić imię, telefon lub e-mail oraz treść wiadomości albo ' . $tel,
            403 => 'Nie udało się przyjąć wiadomości - formularz został wysłany zbyt szybko. Prosimy wrócić, odczekać chwilę i wysłać jeszcze raz albo ' . $tel,
            405 => 'Ten adres przyjmuje tylko wiadomości z formularza kontaktowego.',
            429 => 'Wysłano już kilka wiadomości. Prosimy spróbować później albo ' . $tel,
        ];
        $t = $teksty[$kod] ?? 'Nie udało się wysłać wiadomości. Prosimy ' . $tel;
    }
    header('Content-Type: text/html; charset=utf-8');
    echo '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
       . '<meta name="robots" content="noindex"><title>' . ($ok ? 'Wiadomość wysłana' : 'Nie wysłano') . ' - Zakład Pogrzebowy Morfeusz</title></head>'
       . '<body style="margin:0;padding:40px 16px;background:#f7f5f1;color:#2b2733;font:17px/1.6 Arial,Helvetica,sans-serif">'
       . '<main style="max-width:560px;margin:0 auto;padding:28px 24px;background:#fff;border:1px solid #e3ded4;border-radius:10px">'
       . '<p style="margin:0 0 18px;font-weight:bold">' . h($t) . '</p>'
       . '<p style="margin:0 0 10px"><a href="' . TELEFON_HREF . '" style="color:#37314a;font-weight:bold">Telefon całodobowy ' . TELEFON . '</a></p>'
       . '<p style="margin:0"><a href="/kontakt/" style="color:#37314a">Wróć do strony kontaktu</a> · <a href="/" style="color:#37314a">Strona główna</a></p>'
       . '</main></body></html>';
    exit;
}

function wlasny($p) {
    if (!function_exists('fileowner') || !function_exists('getmyuid')) return true;
    $o = @fileowner($p);
    if ($o === false) return false;
    if ($o === getmyuid()) return true;
    return function_exists('posix_geteuid') && $o === posix_geteuid();
}
// ./_limity: tworzony z 0700 i z .htaccess "Require all denied"; null, gdy nie da się w nim zapisywać
function katalog_w_webroot() {
    $k = __DIR__ . '/_limity';
    if (!is_dir($k) && !@mkdir($k, 0700, true)) return null;
    if (!is_writable($k)) return null;
    $ht = $k . '/.htaccess';
    if (!is_file($ht) && @file_put_contents($ht, "Require all denied\n<IfModule !mod_authz_core.c>\nDeny from all\n</IfModule>\n") === false) {
        dziennik('nie można zapisać _limity/.htaccess');
        return null;
    }
    return $k;
}
// sekret: najpierw plik wgrany ze stroną (./_limity, katalog z blokadą .htaccess - wgrywa go tylko właściciel konta FTP),
// potem nad webrootem (tylko własny plik); brak obu -> nowy losowy (0600), zapis atomowy
function sekret() {
    static $s = null;
    if ($s !== null) return $s;
    $wczytaj = function ($p, $sprawdzWlasciciela) {
        if (!is_file($p) || is_link($p)) return null;
        if ($sprawdzWlasciciela && (!wlasny($p) || !wlasny(dirname($p)))) return null;
        $t = @file_get_contents($p, false, null, 0, 4096);
        return is_string($t) && preg_match("/'klucz'\\s*=>\\s*'([0-9a-f]{64})'/", $t, $m) ? $m[1] : null;
    };
    global $DEV;
    $test = (string) getenv('MORFEUSZ_KATALOG_LIMITOW');
    if ($DEV !== '' && $test !== '') {
        katalog_limitow();
        $kand = [[rtrim($test, '/\\') . '/' . SEKRET_PLIK, true]];
    } else {
        $kand = [[__DIR__ . '/_limity/' . SEKRET_PLIK, false], [dirname(__DIR__) . '/' . SEKRET_PLIK, true]];
    }
    foreach ($kand as [$p, $w]) if (($k = $wczytaj($p, $w)) !== null) return $s = $k;
    if (!($DEV !== '' && $test !== '')) katalog_w_webroot();
    foreach ($kand as [$p, $w]) {
        if (is_file($p) || !is_dir(dirname($p)) || !is_writable(dirname($p))) continue;
        $nowy = bin2hex(random_bytes(32));
        $tmp = $p . '.' . bin2hex(random_bytes(4)) . '.tmp';
        if (@file_put_contents($tmp, "<?php\n// sekret HMAC formularza zpmorfeusz.czest.pl - nie publikować\nreturn ['klucz' => '" . $nowy . "'];\n", LOCK_EX) === false) continue;
        @chmod($tmp, 0600);
        @link($tmp, $p);
        @unlink($tmp);
        if (($k = $wczytaj($p, false)) !== null) return $s = $k;
    }
    dziennik('brak sekretu: nie można odczytać ani zapisać ' . SEKRET_PLIK);
    odpowiedz(false, 500);
}
function siec_klienta() {
    $ip = (string) ($_SERVER['REMOTE_ADDR'] ?? '');
    $bin = @inet_pton($ip);
    if ($bin !== false && strlen($bin) === 16) return bin2hex(substr($bin, 0, 8)) . '/64';
    return $ip;
}
function znacznik_podpis($t) { return hash_hmac('sha256', 'morfeusz-formularz|' . $t . '|' . siec_klienta(), sekret()); }
function znacznik_wiek($z) {
    if (!is_string($z) || !preg_match('/^(\d{10})\.([0-9a-f]{64})$/', $z, $m)) return null;
    if (!hash_equals(znacznik_podpis($m[1]), $m[2])) return null;
    $wiek = time() - (int) $m[1];
    return $wiek < -5 ? null : max(0, $wiek);
}

// ------------------------------------------------------------------ 1. metoda i rozmiar
if ($METODA === 'GET' && isset($_GET['znacznik'])) {
    header('Content-Type: application/json; charset=utf-8');
    $t = (string) time();
    echo json_encode(['z' => $t . '.' . znacznik_podpis($t)]);
    exit;
}
if ($METODA !== 'POST') odpowiedz(false, 405);
if ((int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > MAX_ZADANIA) odpowiedz(false, 413);

// ------------------------------------------------------------------ 2. skąd przyszło (tylko Origin)
$origin = (string) ($_SERVER['HTTP_ORIGIN'] ?? '');
$okSkad = $origin === '' || preg_match(DOMENY, $origin) || ($DEV !== '' && preg_match('#^http://(localhost|127\.0\.0\.1)(:\d+)?(/|$)#', $origin));
if (!$okSkad) odpowiedz(false, 403, ['blad' => 'origin']);

// ------------------------------------------------------------------ 3. znacznik czasu
$wiek = znacznik_wiek($_POST['_z'] ?? null);
$okZnacznik = $wiek !== null && $wiek >= ZNACZNIK_MIN && $wiek <= ZNACZNIK_MAX;
if ($wiek !== null && $wiek < ZNACZNIK_MIN) odpowiedz(false, 403, ['blad' => 'szybko']);
if (($JSON || $origin === '') && !$okZnacznik) odpowiedz(false, 403, ['blad' => 'znacznik']);

$d = $_POST;
if (!is_array($d) || !$d) odpowiedz(false, 400);
// pułapka na boty - udajemy sukces
if (!empty($d['_honey'])) odpowiedz(true, 200, ['potwierdzenie' => false]);

function pole($d, $k, $max = 200) {
    $v = isset($d[$k]) && is_string($d[$k]) ? trim($d[$k]) : '';
    if (!preg_match('//u', $v)) return '';                       // niepoprawne UTF-8
    return utnij(preg_replace('/[\x00-\x09\x0B-\x1F\x7F]/u', '', $v), $max);
}
function jedna_linia($s) { return trim(preg_replace('/[\r\n\t]+/', ' ', $s)); }

$imie    = jedna_linia(pole($d, 'imie', 100));
$telefon = jedna_linia(pole($d, 'telefon', 25));
$email   = jedna_linia(pole($d, 'email', 120));
$tresc   = str_replace("\r\n", "\n", pole($d, 'wiadomosc', 3000));
$skad    = jedna_linia(pole($d, 'skad', 200));
if (!preg_match('#^/[a-z0-9/-]{0,150}$#', $skad)) $skad = '';

// te same zasady co w przeglądarce (app.js)
$cyfry  = preg_replace('/[\s()+.\-]/', '', $telefon);
$okTel  = $telefon !== '' && preg_match('/^\d{9,13}$/', $cyfry) && preg_match('/^[\d\s()+.\-]+$/', $telefon);
$okMail = $email !== '' && filter_var($email, FILTER_VALIDATE_EMAIL) !== false && !preg_match('/[\r\n,;<>"]/', $email);
if (dlugosc($imie) < 2 || ($telefon === '' && $email === '') || ($telefon !== '' && !$okTel) || ($email !== '' && !$okMail) || dlugosc(trim($tresc)) < 5) {
    odpowiedz(false, 422);
}

// ------------------------------------------------------------------ limity (JSON + flock)
function katalog_limitow() {
    global $DEV;
    static $wybrany = false;
    if ($wybrany !== false) return $wybrany;
    $kand = [];
    $test = (string) getenv('MORFEUSZ_KATALOG_LIMITOW');
    if ($DEV !== '' && $test !== '') $kand[] = $test;
    $kand[] = dirname(__DIR__) . '/_limity';
    $kand[] = __DIR__ . '/_limity';
    $kand[] = rtrim(sys_get_temp_dir(), '/\\') . '/morfeusz_limity';
    foreach ($kand as $k) {
        if ($k === __DIR__ . '/_limity') {
            if (katalog_w_webroot() === null) continue;
        } else {
            if (!is_dir($k) && !@mkdir($k, 0700, true)) continue;
            if (!is_writable($k)) continue;
            if (is_link($k) || !wlasny($k)) { dziennik('katalog limitów nie należy do skryptu: ' . basename($k)); continue; }
        }
        return $wybrany = $k;
    }
    dziennik('brak zapisywalnego katalogu na limity');
    return $wybrany = null;
}
function z_limitem($plik, callable $fn) {
    $kat = katalog_limitow();
    if ($kat === null) return null;
    $sciezka = $kat . '/' . $plik;
    if (file_exists($sciezka) && is_link($sciezka)) return null;
    $u = @fopen($sciezka, 'c+');
    if ($u === false) { dziennik('nie można otworzyć pliku limitów ' . $plik); return null; }
    if (!flock($u, LOCK_EX)) { fclose($u); return null; }
    $dane = json_decode((string) stream_get_contents($u), true);
    if (!is_array($dane)) $dane = [];
    $wynik = $fn($dane);
    $json = json_encode($dane);
    $ok = ftruncate($u, 0) && rewind($u) && fwrite($u, $json) === strlen($json) && fflush($u);
    flock($u, LOCK_UN);
    fclose($u);
    if (!$ok) { dziennik('nie można zapisać pliku limitów ' . $plik); return null; }
    return $wynik;
}
function skrot($s) { return hash_hmac('sha256', 'morfeusz-limit|' . $s, sekret()); }

$teraz = time();
$skrotIp = skrot('siec|' . siec_klienta());
$bezJs = !$okZnacznik;
$limIp = $bezJs ? LIMIT_BEZ_JS : LIMIT;
$wolnoIp = z_limitem($bezJs ? 'ip-bez-js.json' : 'ip.json', function (&$dane) use ($teraz, $skrotIp, $limIp) {
    foreach ($dane as $k => $czasy) {
        $dane[$k] = array_values(array_filter((array) $czasy, function ($t) use ($teraz) { return (int) $t > $teraz - OKNO; }));
        if (!$dane[$k]) unset($dane[$k]);
    }
    if (count($dane[$skrotIp] ?? []) >= $limIp) return false;
    $dane[$skrotIp][] = $teraz;
    return true;
});
if ($wolnoIp === false) odpowiedz(false, 429);
// null (zapis się nie udał) - przyjmuję, żeby nie gubić wiadomości

$skrotZ = $okZnacznik ? skrot('znacznik|' . $_POST['_z']) : '';
if ($skrotZ !== '') {
    $wolnyZ = z_limitem('zuzyte.json', function (&$dane) use ($teraz, $skrotZ) {
        $dane = array_filter($dane, function ($t) use ($teraz) { return (int) $t > $teraz - ZNACZNIK_MAX; });
        if (isset($dane[$skrotZ])) return false;
        $dane[$skrotZ] = $teraz;
        return true;
    });
    if ($wolnyZ === false) odpowiedz(false, 403, ['blad' => 'znacznik']);
}
function zwolnij_znacznik($skrotZ) {
    if ($skrotZ !== '') z_limitem('zuzyte.json', function (&$dane) use ($skrotZ) { unset($dane[$skrotZ]); return true; });
}
$wolnoGlob = z_limitem('globalny.json', function (&$dane) use ($teraz) {
    $dane = array_values(array_filter((array) $dane, function ($t) use ($teraz) { return (int) $t > $teraz - 86400; }));
    $godz = count(array_filter($dane, function ($t) use ($teraz) { return (int) $t > $teraz - 3600; }));
    if ($godz >= LIMIT_GLOBALNY_H || count($dane) >= LIMIT_GLOBALNY_D) return false;
    $dane[] = $teraz;
    return true;
});
if ($wolnoGlob === false) { dziennik('łączny limit powiadomień przekroczony'); zwolnij_znacznik($skrotZ); odpowiedz(false, 429, ['blad' => 'globalny']); }

// ------------------------------------------------------------------ MIME
const NL = "\r\n";
function zakoduj($s) {                         // nagłówek UTF-8 (RFC 2047)
    if (!preg_match('/[^\x20-\x7E]/', $s)) return $s;
    $out = []; $kaw = '';
    foreach (preg_split('//u', $s, -1, PREG_SPLIT_NO_EMPTY) as $z) {
        if (strlen($kaw . $z) > 45) { $out[] = '=?UTF-8?B?' . base64_encode($kaw) . '?='; $kaw = ''; }
        $kaw .= $z;
    }
    if ($kaw !== '') $out[] = '=?UTF-8?B?' . base64_encode($kaw) . '?=';
    return implode(' ', $out);
}
function b64($s) { return rtrim(chunk_split(base64_encode($s), 76, NL)) . NL; }
function alternatywa($tekst, $html) {
    $g = '=_mf_' . bin2hex(random_bytes(10));
    return ['Content-Type: multipart/alternative; boundary="' . $g . '"',
        '--' . $g . NL . 'Content-Type: text/plain; charset=UTF-8' . NL . 'Content-Transfer-Encoding: base64' . NL . NL . b64($tekst)
        . '--' . $g . NL . 'Content-Type: text/html; charset=UTF-8' . NL . 'Content-Transfer-Encoding: base64' . NL . NL . b64($html)
        . '--' . $g . '--' . NL];
}
function wyslij($do, $temat, $naglowki, $glowny, $nazwa = NADAWCA_NAZWA) {
    global $DEV;
    $nag = array_merge([
        'From: ' . zakoduj($nazwa) . ' <' . NADAWCA . '>',
        'Date: ' . date('r'),
        'Message-ID: <' . bin2hex(random_bytes(12)) . '@zpmorfeusz.czest.pl>',
        'MIME-Version: 1.0',
    ], $naglowki, [$glowny[0]]);
    $tematZak = zakoduj($temat);
    if ($DEV !== '') {                         // tylko lokalnie: zapis .eml zamiast wysyłki
        if (!is_dir($DEV)) @mkdir($DEV, 0777, true);
        $plik = rtrim($DEV, '/\\') . '/' . date('Ymd-His') . '-' . substr(md5($do . microtime()), 0, 6) . '.eml';
        return (bool) file_put_contents($plik, 'To: ' . $do . NL . 'Subject: ' . $tematZak . NL . implode(NL, $nag) . NL . NL . $glowny[1]);
    }
    return mail($do, $tematZak, $glowny[1], implode(NL, $nag));   // bez -f
}

// ------------------------------------------------------------------ potwierdzenie: czy wolno
$wyslijPotw = false;
$powodPotw = 'nie (klient nie podał e-maila)';
if ($okMail) {
    if (!$okZnacznik) {
        $powodPotw = 'nie (wysłane bez JavaScriptu)';
    } else {
        $skrotMail = skrot(strtolower($email));
        $wynik = z_limitem('potwierdzenia.json', function (&$dane) use ($teraz, $skrotMail) {
            $g = array_values(array_filter((array) ($dane['g'] ?? []), function ($t) use ($teraz) { return (int) $t > $teraz - 3600; }));
            $a = array_filter((array) ($dane['a'] ?? []), function ($t) use ($teraz) { return (int) $t > $teraz - POTW_NA_ADRES; });
            $dane = ['g' => $g, 'a' => $a];
            if (isset($a[$skrotMail])) return 'adres';
            if (count($g) >= LIMIT_POTWIERDZEN) return 'godzina';
            $dane['g'][] = $teraz;
            $dane['a'][$skrotMail] = $teraz;
            return 'ok';
        });
        $wyslijPotw = $wynik === 'ok';
        $powodPotw = $wynik === 'ok' ? 'tak' : ($wynik === 'adres' ? 'nie (już wysłane na ten adres w ciągu doby)'
            : ($wynik === 'godzina' ? 'nie (limit godzinowy)' : 'nie (błąd zapisu limitów)'));
    }
}

// ------------------------------------------------------------------ mail 1: powiadomienie do zakładu
$kiedy = date('d.m.Y, H:i');
$nrTel = $okTel ? preg_replace('/[^\d+]/', '', $telefon) : '';
$brak = '<span style="color:#6b6573;font-weight:normal">nie podano</span>';
$wiersze = [
    'Imię i nazwisko' => h($imie),
    'Telefon' => $okTel ? '<a href="tel:' . h($nrTel) . '" style="color:#2b2733">' . h($telefon) . '</a>' : $brak,
    'E-mail' => $okMail ? '<a href="mailto:' . h($email) . '" style="color:#37314a">' . h($email) . '</a>' : $brak,
    'Wiadomość' => '<span style="font-weight:normal">' . nl2br(h($tresc)) . '</span>',
];
$tab = '';
foreach ($wiersze as $k => $v) {
    $tab .= '<tr><td style="padding:12px 24px;border-bottom:1px solid #e9e5dd;font-family:Arial,Helvetica,sans-serif">'
          . '<div style="font-size:13px;color:#6b6573;margin:0 0 3px">' . h($k) . '</div>'
          . '<div style="font-size:16px;line-height:1.5;color:#2b2733;font-weight:bold;word-break:break-word;overflow-wrap:anywhere">' . $v . '</div></td></tr>';
}
$htmlZ = '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Wiadomość ze strony</title></head>'
    . '<body style="margin:0;padding:0;background:#f1eee8">'
    . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f1eee8"><tr><td align="center" style="padding:16px 8px">'
    . '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;background:#ffffff;border:1px solid #e3ded4;border-radius:10px">'
    . '<tr><td bgcolor="#37314a" style="padding:18px 24px;font:bold 18px/1.3 Arial,Helvetica,sans-serif;color:#ffffff">Wiadomość ze strony zpmorfeusz.czest.pl</td></tr>'
    . $tab
    . '<tr><td style="padding:12px 24px 18px;font:13px/1.5 Arial,Helvetica,sans-serif;color:#6b6573">Wysłano ' . h($kiedy) . ' z podstrony ' . h($skad !== '' ? $skad : '/kontakt/')
    . '. Potwierdzenie do nadawcy: ' . h($powodPotw) . '.' . ($okMail ? ' Aby odpowiedzieć, wystarczy kliknąć Odpowiedz.' : '') . '</td></tr>'
    . '</table></td></tr></table></body></html>';
$tekstZ = "Wiadomość ze strony zpmorfeusz.czest.pl\n\nImię i nazwisko: $imie\nTelefon: " . ($telefon ?: 'nie podano') . "\nE-mail: " . ($email ?: 'nie podano')
    . "\nWiadomość:\n$tresc\n\nWysłano: $kiedy\nZ podstrony: " . ($skad ?: '/kontakt/') . "\nPotwierdzenie do nadawcy: $powodPotw\n";
$nagZ = [];
if ($okMail) $nagZ[] = 'Reply-To: ' . $email;
if (!wyslij(ODBIORCA, 'Wiadomość ze strony zakładu Morfeusz: ' . $imie, $nagZ, alternatywa($tekstZ, $htmlZ), 'Formularz strony Morfeusz')) {
    dziennik('mail() do odbiorcy zwrócił false');
    zwolnij_znacznik($skrotZ);
    odpowiedz(false, 500);
}

// ------------------------------------------------------------------ mail 2: potwierdzenie dla klienta
// nie zawiera niczego, co wpisał nadawca - formularz nie nadaje się do wysyłania treści na cudze adresy
$potwierdzenie = false;
if ($wyslijPotw) {
    $akapity = [
        'Dzień dobry,',
        'dziękujemy za wiadomość - dotarła do Zakładu Pogrzebowego MORFEUSZ. Odpowiemy najszybciej, jak to możliwe.',
        'W pilnej sprawie prosimy dzwonić - telefon całodobowy ' . TELEFON . '.',
    ];
    $p = 'margin:0 0 16px';
    $htmlK = '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dziękujemy za wiadomość</title></head>'
        . '<body style="margin:0;padding:16px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.6;color:#222222;background:#ffffff"><div style="max-width:600px">';
    foreach ($akapity as $a) $htmlK .= '<p style="' . $p . '">' . h($a) . '</p>';
    $htmlK .= '<p style="margin:24px 0 0">Zakład Pogrzebowy MORFEUSZ<br>ul. Górna 30, 42-263 Wrzosowa<br>'
        . '<a href="' . TELEFON_HREF . '" style="color:#222222">' . TELEFON . '</a> (całą dobę)<br><a href="https://zpmorfeusz.czest.pl/" style="color:#222222">zpmorfeusz.czest.pl</a></p>'
        . '<p style="margin:20px 0 0;font-size:13px;color:#666666">Ta wiadomość została wysłana automatycznie po wypełnieniu formularza na stronie zpmorfeusz.czest.pl.</p>'
        . '</div></body></html>';
    $tekstK = implode("\n\n", $akapity) . "\n\nZakład Pogrzebowy MORFEUSZ\nul. Górna 30, 42-263 Wrzosowa\n" . TELEFON . " (całą dobę)\nzpmorfeusz.czest.pl\n\n"
        . "Ta wiadomość została wysłana automatycznie po wypełnieniu formularza na stronie zpmorfeusz.czest.pl.\n";
    $potwierdzenie = wyslij($email, 'Dziękujemy za wiadomość - Zakład Pogrzebowy MORFEUSZ', ['Reply-To: ' . ODBIORCA, 'Auto-Submitted: auto-replied'], alternatywa($tekstK, $htmlK));
    if (!$potwierdzenie) dziennik('mail() z potwierdzeniem zwrócił false');
}

odpowiedz(true, 200, ['potwierdzenie' => $potwierdzenie]);
