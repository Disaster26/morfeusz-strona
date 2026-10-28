# -*- coding: utf-8 -*-
"""Generator stron Zakladu Pogrzebowego Morfeusz.

  python _zrodla/build.py              -> wersja testowa (noindex, formularz na adres testowy, 404 dla GitHub Pages)
  python _zrodla/build.py --produkcja  -> wersja na hosting klienta (indeksowanie wlaczone, formularz na zpmorfeusz@onet.eu)

Folder _zrodla nie jest publikowany (GitHub Pages/Jekyll pomija katalogi z podkresleniem;
na hosting klienta go nie wgrywamy).
"""
import json, os, sys, html

PROD = '--produkcja' in sys.argv
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INFO = json.load(open(os.path.join(os.path.dirname(__file__), 'zdjecia.json'), encoding='utf-8'))

DOMENA = 'https://zpmorfeusz.czest.pl'
FORM_ADRES = 'https://formsubmit.co/ajax/' + ('zpmorfeusz@onet.eu' if PROD else 'stasiu2626@gmail.com')
BASE_404 = '/' if PROD else '/morfeusz-strona/'
WERSJA = '3'

TEL = ('601 460 964', 'tel:+48601460964')
TEL_STACJ = ('34 327 51 06', 'tel:+48343275106')
TEL_KOM = ('603 847 926', 'tel:+48603847926')
MAIL = 'zpmorfeusz@onet.eu'
GMAPS = 'https://www.google.com/maps/search/?api=1&query=Zak%C5%82ad+Pogrzebowy+Morfeusz%2C+G%C3%B3rna+30%2C+42-263+Wrzosowa'
GTRASA = 'https://www.google.com/maps/dir/?api=1&destination=G%C3%B3rna+30%2C+42-263+Wrzosowa'
OSM = 'https://www.openstreetmap.org/?mlat=50.74755&mlon=19.14560#map=17/50.74755/19.14560'

NAV = [('oferta/', 'Oferta'), ('gdy-umrze-bliska-osoba/', 'Gdy umrze bliska osoba'), ('galeria/', 'O zakładzie'), ('kontakt/', 'Kontakt')]


def e(s):
    return html.escape(s, quote=True)


def img(name, alt, sizes, R, eager=False, cls=''):
    v = INFO[name]
    srcset = ', '.join(f'{R}img/{fn} {w}w' for fn, w, h in v)
    mid = [x for x in v if x[1] <= 800] or v[:1]
    fn, w, h = mid[-1]
    W, H = v[-1][1], v[-1][2]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="{R}img/{fn}" srcset="{srcset}" sizes="{sizes}" alt="{e(alt)}" '
            f'width="{W}" height="{H}" {load} decoding="async">')


def najwiekszy(name):
    return INFO[name][-1][0]


def schema_firma():
    return {
        '@context': 'https://schema.org',
        '@type': 'LocalBusiness',
        'additionalType': 'https://www.productontology.org/id/Funeral_home',
        '@id': DOMENA + '/#zaklad',
        'name': 'Zakład Pogrzebowy „MORFEUSZ” Ireneusz Jeziorowski',
        'alternateName': 'Zakład Pogrzebowy Morfeusz',
        'url': DOMENA + '/',
        'image': DOMENA + '/img/' + najwiekszy('namiot-cmentarz'),
        'telephone': '+48601460964',
        'email': MAIL,
        'taxID': '5731706929',
        'address': {'@type': 'PostalAddress', 'streetAddress': 'ul. Górna 30', 'postalCode': '42-263',
                    'addressLocality': 'Wrzosowa', 'addressRegion': 'śląskie', 'addressCountry': 'PL'},
        'geo': {'@type': 'GeoCoordinates', 'latitude': 50.74755, 'longitude': 19.14560},
        'hasMap': GMAPS,
        'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification',
                                       'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                                       'opens': '00:00', 'closes': '23:59'}],
        'contactPoint': [
            {'@type': 'ContactPoint', 'telephone': '+48601460964', 'contactType': 'telefon całodobowy', 'availableLanguage': 'pl',
             'hoursAvailable': {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], 'opens': '00:00', 'closes': '23:59'}},
            {'@type': 'ContactPoint', 'telephone': '+48343275106', 'contactType': 'telefon stacjonarny', 'availableLanguage': 'pl'},
            {'@type': 'ContactPoint', 'telephone': '+48603847926', 'contactType': 'telefon komórkowy', 'availableLanguage': 'pl'},
        ],
        'areaServed': [{'@type': 'Place', 'name': n} for n in ['Wrzosowa', 'Poczesna', 'Częstochowa', 'Kamienica Polska', 'powiat częstochowski']],
    }


def okruszki(sciezka, nazwa):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Strona główna', 'item': DOMENA + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': nazwa, 'item': DOMENA + '/' + sciezka}]}


def strona(sciezka, tytul, opis, tresc, glowna=False, schemy=None, preload='', noindex=False, base=None):
    R = '' if sciezka == '' else '../'
    if base is not None:
        R = base
    robots = '<meta name="robots" content="noindex, nofollow">\n' if (not PROD or noindex) else ''
    nav = ''
    for href, nazwa in NAV:
        cur = ' aria-current="page"' if sciezka == href else ''
        nav += f'      <a href="{R}{href}"{cur}>{nazwa}</a>\n'
    sch = ''
    for s in (schemy or []):
        sch += '<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False, separators=(',', ':')) + '</script>\n'
    canon = '' if base is not None else f'<link rel="canonical" href="{DOMENA}/{sciezka}">\n'
    og_img = DOMENA + '/img/' + INFO['namiot-cmentarz'][2][0]
    body_cls = ' class="strona-glowna"' if glowna else ''
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{robots}<title>{e(tytul)}</title>
<meta name="description" content="{e(opis)}">
{canon}<meta name="theme-color" content="#f7f5f1">
<meta property="og:type" content="website">
<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="Zakład Pogrzebowy „Morfeusz”">
<meta property="og:title" content="{e(tytul)}">
<meta property="og:description" content="{e(opis)}">
<meta property="og:url" content="{DOMENA}/{sciezka}">
<meta property="og:image" content="{og_img}">
<link rel="icon" href="{R}favicon.ico" sizes="32x32">
<link rel="icon" href="{R}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{R}apple-touch-icon.png">
<link rel="preload" href="{R}fonts/source-sans-3.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{R}fonts/cormorant-garamond-600.woff2" as="font" type="font/woff2" crossorigin>
{preload}<link rel="stylesheet" href="{R}style.css?v={WERSJA}">
{sch}</head>
<body{body_cls}>
<a class="skip" href="#tresc">Przejdź do treści</a>
<header class="top">
  <div class="wrap top-in">
    <a class="logo" href="{R if R else './'}" aria-label="Zakład Pogrzebowy Morfeusz - strona główna">
      <span class="logo-n">Morfeusz</span>
      <span class="logo-s">Zakład Pogrzebowy</span>
    </a>
    <nav class="nav" id="nav" aria-label="Menu">
{nav}      <a class="nav-tel" href="{TEL[1]}">Zadzwoń całą dobę: {TEL[0]}</a>
    </nav>
    <a class="top-tel" href="{TEL[1]}" aria-label="Zadzwoń całą dobę: {TEL[0]}">{TEL[0]}</a>
    <button class="burger" id="burger" type="button" aria-label="Otwórz menu" aria-expanded="false" aria-controls="nav"><span></span><span></span></button>
  </div>
</header>

<main id="tresc">
{tresc}
</main>

<footer class="stopka">
  <div class="wrap stopka-in">
    <div>
      <p class="st-n">Zakład Pogrzebowy „Morfeusz”</p>
      <p>Ireneusz Jeziorowski<br>ul. Górna 30<br>42-263 Wrzosowa</p>
    </div>
    <div>
      <p>Całą dobę: <a href="{TEL[1]}">{TEL[0]}</a><br>tel. <a href="{TEL_STACJ[1]}">{TEL_STACJ[0]}</a><br>kom. <a href="{TEL_KOM[1]}">{TEL_KOM[0]}</a><br><a href="mailto:{MAIL}">{MAIL}</a></p>
    </div>
    <ul class="st-nav">
      <li><a href="{R if R else './'}">Strona główna</a></li>
{''.join(f'      <li><a href="{R}{h}">{n}</a></li>{chr(10)}' for h, n in NAV)}    </ul>
    <div>
      <p>Zakład czynny całą dobę w dni powszednie i święta.</p>
      <p style="margin-top:10px">NIP 573-170-69-29<br>REGON 150320820</p>
    </div>
  </div>
  <div class="wrap st-dol">
    <p>© Zakład Pogrzebowy „Morfeusz”, Wrzosowa</p>
    <p><a href="{R}polityka-prywatnosci/">Polityka prywatności</a></p>
  </div>
</footer>

<div class="mob" id="mob">
  <a href="{TEL[1]}"><span>Zadzwoń całą dobę</span> {TEL[0]}</a>
</div>

<script src="{R}app.js?v={WERSJA}" defer></script>
</body>
</html>
'''


def zapisz(sciezka, tekst, plik='index.html'):
    d = os.path.join(ROOT, sciezka)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, plik), 'w', encoding='utf-8', newline='\n') as f:
        f.write(tekst)


def blok_kontakt(R, naglowek='h2'):
    return f'''    <div class="kontakt-tx">
      <{naglowek}>Kontakt</{naglowek}>
      <p class="k-adr">Zakład Pogrzebowy „Morfeusz”<br>ul. Górna 30<br>42-263 Wrzosowa</p>
      <dl class="k-tel">
        <div><dt>Telefon całodobowy</dt><dd><a class="k-main" href="{TEL[1]}">{TEL[0]}</a></dd></div>
        <div><dt>Telefon stacjonarny</dt><dd><a href="{TEL_STACJ[1]}">{TEL_STACJ[0]}</a></dd></div>
        <div><dt>Telefon komórkowy</dt><dd><a href="{TEL_KOM[1]}">{TEL_KOM[0]}</a></dd></div>
        <div><dt>E-mail</dt><dd><a href="mailto:{MAIL}">{MAIL}</a></dd></div>
      </dl>
      <p class="k-czynne">Zakład czynny całą dobę w dni powszednie i święta.</p>
    </div>'''


def blok_mapa(R):
    return f'''    <figure class="mapa">
      <a href="{GMAPS}" target="_blank" rel="noopener" aria-label="Otwórz lokalizację zakładu w Mapach Google (nowa karta)">
        <img src="{R}img/mapa-700.webp" srcset="{R}img/mapa-700.webp 700w, {R}img/mapa-1400.webp 1400w" sizes="(max-width:900px) 100vw, 640px" alt="Mapa: Zakład Pogrzebowy Morfeusz, ul. Górna 30 we Wrzosowej, niedaleko drogi krajowej nr 91" width="1400" height="1000" loading="lazy" decoding="async">
      </a>
      <figcaption><span>ul. Górna 30, Wrzosowa - niedaleko drogi nr 91 (ul. Katowickiej)</span><span>Mapa © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">autorzy OpenStreetMap</a></span></figcaption>
      <div class="mapa-przyc">
        <a href="{GTRASA}" target="_blank" rel="noopener">Wyznacz trasę</a>
        <a href="{OSM}" target="_blank" rel="noopener">Mapa OpenStreetMap</a>
      </div>
    </figure>'''


def ph(h1, lead, R, foto=None, foto_alt='', tel=True):
    tel_html = f'\n      <p class="ph-tel">Telefon całodobowy: <a href="{TEL[1]}">{TEL[0]}</a></p>' if tel else ''
    if foto:
        f = f'\n    <figure class="ph-foto">{img(foto, foto_alt, "(max-width:900px) 100vw, 46vw", R, eager=True)}</figure>'
        cls = 'ph'
    else:
        f = ''
        cls = 'ph ph-bez'
    return f'''<section class="{cls}">
  <div class="wrap ph-in">
    <div>
      <h1>{h1}</h1>
      <p class="ph-lead">{lead}</p>{tel_html}
    </div>{f}
  </div>
</section>'''


def preload_img(name, sizes, R):
    v = INFO[name]
    srcset = ', '.join(f'{R}img/{fn} {w}w' for fn, w, h in v)
    return f'<link rel="preload" as="image" imagesrcset="{srcset}" imagesizes="{sizes}" fetchpriority="high">\n'


# ---------------------------------------------------------------- strona glowna
def glowna():
    R = ''
    S_KAFEL = '(max-width:760px) 100vw, (max-width:1180px) 42vw, 280px'
    kafle = [
        ('organizacja', 'biuro', 'Biuro obsługi klienta w zakładzie', 'Organizacja pogrzebu', ['Kompleksowa organizacja pogrzebu', 'Bezgotówkowa organizacja pogrzebów', 'Pomoc w formalnościach']),
        ('kremacje', 'stojak-urna', 'Stojak na urnę z bordowym aksamitem i świecami na cmentarzu', 'Kremacje', ['Organizacja kremacji', 'Sprzedaż urn', 'Nagrobki urnowe']),
        ('trumny-urny', 'urny', 'Urny na półkach w zakładzie', 'Trumny, urny, ubrania', ['Sprzedaż trumien i urn', 'Ubrania dla zmarłych']),
        ('transport', 'karawan', 'Karawan zakładu Morfeusz', 'Transport', ['Krajowy i międzynarodowy transport zwłok', 'Karawany i autokary', 'Własna chłodnia']),
        ('ubieranie', None, '', 'Ubieranie i kosmetyka', 'Ubieranie i kosmetyka osób zmarłych - z szacunkiem, według życzeń rodziny.'),
        ('oprawa', 'kaplica-ceremonia', 'Kaplica z trumną i kwiatami przed ceremonią', 'Oprawa ceremonii', ['Oprawa muzyczna: trąbka, skrzypce, orkiestra, organista', 'Wieńce i wiązanki', 'Dekoracje żałobne mieszkań']),
        ('cmentarz', 'grob-namiot', 'Namiot zakładu nad grobem przygotowanym do pochówku', 'Usługi grabarskie', 'Przygotowanie grobu i obsługa ceremonii na cmentarzu.'),
        ('kamieniarstwo', None, '', 'Kamieniarstwo', ['Pomniki', 'Nagrobki urnowe', 'Litery i zdjęcia na pomnikach', 'Poziomowanie i naprawa pomników']),
    ]
    k = ''
    for kot, foto, alt, h, tresc in kafle:
        t = ('<ul>' + ''.join(f'<li>{x}</li>' for x in tresc) + '</ul>') if isinstance(tresc, list) else f'<p>{tresc}</p>'
        if foto:
            k += f'''      <a class="kafel" href="oferta/#{kot}">
        <div class="kafel-foto">{img(foto, alt, S_KAFEL, R)}</div>
        <div class="kafel-tx"><h3>{h}</h3>{t}</div>
      </a>
'''
        else:
            k += f'''      <a class="kafel kafel-bez" href="oferta/#{kot}">
        <div class="kafel-tx"><h3>{h}</h3>{t}</div>
      </a>
'''
    hero_sizes = '(max-width:760px) 100vw, 54vw'
    tresc = f'''<section class="hero">
  <figure class="hero-foto">
    {img('namiot-cmentarz', 'Namiot Zakładu Pogrzebowego Morfeusz z bordowym stojakiem w alei cmentarza', hero_sizes, R, eager=True)}
  </figure>
  <div class="hero-in">
    <p class="hero-adr">Wrzosowa, ul. Górna 30 - okolice Częstochowy</p>
    <h1>Zakład Pogrzebowy „Morfeusz”</h1>
    <p class="hero-czynne"><span class="dot" aria-hidden="true"></span>Czynne całą dobę, także w święta</p>
    <p class="hero-lead">Kompleksowe usługi pogrzebowe. Pomożemy we wszystkich formalnościach, pogrzeb zorganizujemy także bezgotówkowo.</p>
    <a class="tel-main" id="telMain" href="{TEL[1]}">
      <span class="tel-lab">Telefon całodobowy</span>
      <span class="tel-num">{TEL[0]}</span>
    </a>
    <div class="tel-inne">
      <a href="{TEL_STACJ[1]}"><span>tel.</span> {TEL_STACJ[0]}</a>
      <a href="{TEL_KOM[1]}"><span>kom.</span> {TEL_KOM[0]}</a>
    </div>
  </div>
</section>

<section class="sec sec-alt" id="uslugi">
  <div class="wrap">
    <div class="sec-head">
      <h2>Zakres usług</h2>
      <p>Świadczymy kompleksowe usługi pogrzebowe - od pierwszego telefonu, przez formalności i transport, po oprawę ceremonii i pomnik.</p>
    </div>
    <div class="kafle">
{k}    </div>
    <div class="sec-dol"><a class="dalej" href="oferta/">Pełna oferta</a></div>
  </div>
</section>

<section class="sec" id="gdy-umrze">
  <div class="wrap gdy">
    <div class="gdy-tx">
      <h2>Co zrobić, gdy umrze bliska osoba</h2>
      <p class="gdy-lead">Nie musisz wiedzieć wszystkiego od razu. Wystarczy jeden telefon - resztę przejdziemy razem, krok po kroku.</p>
      <ol class="kroki">
        <li><strong>Zadzwoń do nas.</strong> Odbieramy o każdej porze, także w nocy, w niedziele i w święta. Jeśli śmierć nastąpiła w domu, potrzebny jest też lekarz, który stwierdzi zgon.</li>
        <li><strong>Przygotuj dokumenty zmarłego,</strong> które masz pod ręką, np. dowód osobisty. Przez telefon podpowiemy, co jeszcze będzie potrzebne.</li>
        <li><strong>Spokojnie ustalimy przebieg pogrzebu</strong> - termin, miejsce, oprawę. Pomożemy w formalnościach, pogrzeb możemy zorganizować bezgotówkowo.</li>
        <li><strong>Resztą zajmiemy się my:</strong> transport, przygotowanie zmarłego, oprawa ceremonii i cmentarz.</li>
      </ol>
      <a class="dalej" href="gdy-umrze-bliska-osoba/">Formalności krok po kroku</a>
    </div>
    <aside class="gdy-tel" aria-label="Telefony">
      <p>Telefon całodobowy</p>
      <a href="{TEL[1]}">{TEL[0]}</a>
      <p class="gdy-tel-inne">tel. <a href="{TEL_STACJ[1]}">{TEL_STACJ[0]}</a><br>kom. <a href="{TEL_KOM[1]}">{TEL_KOM[0]}</a></p>
    </aside>
  </div>
</section>

<section class="sec sec-alt" id="zaklad">
  <div class="wrap zaklad">
    <div class="zaklad-tx">
      <h2>Zakład we Wrzosowej</h2>
      <p>Zakład mieści się przy ul. Górnej 30 we Wrzosowej, w gminie Poczesna pod Częstochową. Mamy własną kaplicę, własną chłodnię oraz karawany, którymi przewozimy zmarłych w kraju i za granicę.</p>
      <p>Ceremonie obsługują stosownie ubrani, przeszkoleni pracownicy. Na cmentarzu rozstawiamy namiot z zasłonami, a na życzenie zapewniamy oprawę muzyczną, wieńce i wiązanki.</p>
      <p>Organizujemy pogrzeby dla rodzin z Wrzosowej, Poczesnej, Częstochowy, Kamienicy Polskiej i okolicznych miejscowości.</p>
      <a class="dalej" href="galeria/">Zakład i zdjęcia</a>
    </div>
    <div class="zaklad-foto">
      <figure class="fot-lewo">{img('siedziba', 'Budynek Zakładu Pogrzebowego Morfeusz przy ul. Górnej 30', '(max-width:760px) 50vw, 330px', R)}</figure>
      <figure>{img('kaplica', 'Kaplica przy zakładzie z krzyżem na czerwonej ścianie', '(max-width:760px) 50vw, 330px', R)}</figure>
    </div>
  </div>
</section>

<section class="sec" id="kontakt">
  <div class="wrap kontakt">
{blok_kontakt(R)}
{blok_mapa(R)}
  </div>
</section>'''
    tresc = tresc.replace('<p class="k-czynne">Zakład czynny całą dobę w dni powszednie i święta.</p>',
                          '<p class="k-czynne">Zakład czynny całą dobę w dni powszednie i święta.</p>\n      <a class="dalej" href="kontakt/#formularz">Formularz kontaktowy</a>')
    zapisz('', strona('', 'Zakład Pogrzebowy Morfeusz Wrzosowa - całą dobę 601 460 964',
                      'Zakład Pogrzebowy „Morfeusz”, ul. Górna 30, Wrzosowa k. Częstochowy. Organizacja pogrzebów, kremacje, transport, własna chłodnia, kamieniarstwo. Całą dobę: 601 460 964.',
                      tresc, glowna=True, schemy=[schema_firma()], preload=preload_img('namiot-cmentarz', hero_sizes, R)))


# ---------------------------------------------------------------- oferta
def oferta():
    R = '../'
    S = '(max-width:900px) 100vw, 540px'
    bloki = [
        ('organizacja', 'Organizacja pogrzebu i formalności', 'biuro', 'Biuro obsługi klienta w zakładzie',
         ['Pogrzeb organizujemy kompleksowo, więc rodzina nie musi sama chodzić po urzędach ani ustalać szczegółów z kilkoma firmami. Wszystko omawiamy spokojnie, w biurze zakładu albo przez telefon.'],
         ['Kompleksowa organizacja pogrzebu', 'Bezgotówkowa organizacja pogrzebu - rozliczenie z zasiłku pogrzebowego', 'Pomoc w formalnościach w urzędzie, parafii i na cmentarzu', 'Ceremonie wyznaniowe i świeckie'],
         ('gdy-umrze-bliska-osoba/', 'Formalności krok po kroku')),
        ('kremacje', 'Kremacje', 'stojak-urna', 'Stojak na urnę z bordowym aksamitem i świecami przy grobie',
         ['Organizujemy pogrzeby z kremacją: przewóz zmarłego do krematorium, wybór urny i pogrzeb urnowy na cmentarzu.'],
         ['Organizacja kremacji', 'Sprzedaż urn', 'Pogrzeb urnowy z oprawą na cmentarzu', 'Nagrobki urnowe'], None),
        ('trumny-urny', 'Trumny, urny i ubrania', 'urny', 'Urny na półkach w zakładzie',
         ['W zakładzie można wybrać trumnę lub urnę oraz ubranie dla zmarłego. Pomożemy dobrać je do rodzaju pogrzebu i życzeń rodziny.'],
         ['Sprzedaż trumien', 'Sprzedaż urn', 'Ubrania dla zmarłych'], None),
        ('ubieranie', 'Ubieranie i kosmetyka zmarłych', None, '',
         ['Przygotowanie zmarłego do pożegnania wykonujemy z szacunkiem i według życzeń rodziny. Można przynieść własne ubranie zmarłego albo wybrać je w zakładzie.'],
         ['Ubieranie osób zmarłych', 'Kosmetyka osób zmarłych', 'Ubrania dla zmarłych'], None),
        ('transport', 'Transport zmarłych i własna chłodnia', 'karawan', 'Karawan zakładu Morfeusz',
         ['Przewozimy zmarłych własnymi karawanami do naszej chłodni, a w dniu pogrzebu na ceremonię. Wykonujemy też transport zmarłych na terenie całego kraju i za granicę.'],
         ['Karawany', 'Krajowy i międzynarodowy transport zwłok', 'Własna chłodnia', 'Autokary dla uczestników pogrzebu'], None),
        ('oprawa', 'Oprawa ceremonii', 'kaplica-ceremonia', 'Kaplica z trumną i kwiatami przed ceremonią',
         ['Na życzenie rodziny zapewniamy oprawę muzyczną, kwiaty i dekoracje. Pożegnanie może odbyć się w naszej kaplicy.'],
         ['Oprawa muzyczna: trąbka, skrzypce, orkiestra, organista', 'Wieńce i wiązanki', 'Dekoracje żałobne mieszkań'], None),
        ('cmentarz', 'Usługi grabarskie', 'grob-namiot', 'Namiot zakładu nad grobem wyłożonym zieloną matą',
         ['Przygotowujemy grób do pochówku i obsługujemy ceremonię na cmentarzu. Przy grobie rozstawiamy namiot z zasłonami, a teren wokół wykładamy matą.'],
         ['Usługi grabarskie', 'Namiot z zasłonami przy grobie', 'Obsługa pogrzebu tradycyjnego i urnowego'], None),
        ('kamieniarstwo', 'Usługi kamieniarskie', None, '',
         ['Po pogrzebie pomagamy w sprawach pomnika: wykonujemy pomniki i nagrobki urnowe, litery i zdjęcia, a także poziomowanie i naprawę pomników.'],
         ['Pomniki', 'Nagrobki urnowe', 'Litery i zdjęcia na pomnikach', 'Poziomowanie i naprawa pomników'], None),
    ]
    b = ''
    for kot, h, foto, alt, pars, lista, link in bloki:
        tx = ''.join(f'<p>{p}</p>' for p in pars)
        li = ''.join(f'<li>{x}</li>' for x in lista)
        ln = f'\n      <a class="dalej" href="{R}{link[0]}">{link[1]}</a>' if link else ''
        if foto:
            b += f'''  <div class="usl" id="{kot}">
    <div>
      <h2>{h}</h2>
      <div class="tx">{tx}</div>
      <ul class="lista">{li}</ul>{ln}
    </div>
    <figure class="usl-foto">{img(foto, alt, S, R)}</figure>
  </div>
'''
        else:
            b += f'''  <div class="usl usl-bez" id="{kot}">
    <div>
      <h2>{h}</h2>
      <div class="tx">{tx}</div>
    </div>
    <ul class="lista">{li}</ul>
  </div>
'''
    tresc = ph('Usługi pogrzebowe',
               'Świadczymy kompleksowe usługi pogrzebowe: od pierwszego telefonu, przez formalności, transport i przygotowanie zmarłego, po ceremonię, cmentarz i pomnik. Zakład jest czynny całą dobę, także w święta.',
               R, 'kaplica', 'Kaplica przy zakładzie Morfeusz') + f'''

<section class="sec">
  <div class="wrap">
{b}  </div>
</section>

<section class="cta">
  <div class="wrap cta-in">
    <div>
      <h2>Zakład czynny całą dobę</h2>
      <p>Także w niedziele i święta. Jeśli nie wiesz, od czego zacząć, zadzwoń - wszystko wyjaśnimy.</p>
    </div>
    <a class="cta-tel" href="{TEL[1]}"><span>Telefon całodobowy</span><strong>{TEL[0]}</strong></a>
  </div>
</section>'''
    zapisz('oferta', strona('oferta/', 'Usługi pogrzebowe Wrzosowa, Częstochowa - oferta | Morfeusz',
                            'Organizacja pogrzebów i formalności, kremacje, trumny i urny, transport zwłok w kraju i za granicę, własna chłodnia, oprawa muzyczna, wieńce, usługi grabarskie i kamieniarskie.',
                            tresc, schemy=[okruszki('oferta/', 'Oferta')]))


# ---------------------------------------------------------------- poradnik
def poradnik():
    R = '../'
    tresc = ph('Co zrobić, gdy umrze bliska osoba',
               'Formalności po śmierci bliskiej osoby jest sporo, a to trudny moment. Poniżej opisujemy po kolei, co trzeba zrobić. Nie musisz pamiętać wszystkiego - wystarczy zadzwonić, resztę przejdziemy razem.',
               R) + f'''

<section class="sec">
  <div class="wrap porad">
    <div class="porad-tx">
      <h2>Pierwsze kroki</h2>
      <h3>Gdy śmierć nastąpi w domu</h3>
      <p>Wezwij lekarza, który stwierdzi zgon i wystawi kartę zgonu. W godzinach pracy przychodni jest to zwykle lekarz rodzinny, w nocy i w dni wolne lekarz nocnej i świątecznej opieki zdrowotnej. Jeśli śmierć jest nagła albo nastąpiła w niejasnych okolicznościach, zadzwoń pod numer alarmowy 112.</p>
      <p>Gdy lekarz stwierdzi zgon, zadzwoń do nas: <a href="{TEL[1]}"><strong>{TEL[0]}</strong></a>. Przyjedziemy i przewieziemy zmarłego do naszej chłodni - o każdej porze, także w nocy i w święta.</p>
      <h3>Gdy śmierć nastąpi w szpitalu, hospicjum lub domu opieki</h3>
      <p>Kartę zgonu wystawia lekarz placówki. Zadzwoń do nas - ustalimy, kiedy odbierzemy zmarłego i jakie dokumenty trzeba odebrać z placówki.</p>

      <h2>Dokumenty, które warto przygotować</h2>
      <ul>
        <li><strong>Karta zgonu</strong> - wystawia ją lekarz.</li>
        <li><strong>Dowód osobisty zmarłego.</strong></li>
        <li><strong>Twój dowód osobisty.</strong></li>
        <li><strong>Informacje o emeryturze lub rencie zmarłego</strong> (ZUS, KRUS, MSWiA, MON) - przydadzą się przy zasiłku pogrzebowym.</li>
        <li><strong>Ubranie dla zmarłego</strong> - jeśli rodzina chce przygotować własne. Ubranie można też wybrać w zakładzie.</li>
      </ul>
      <p>Nie masz wszystkiego? Nic nie szkodzi - przez telefon podpowiemy, co jest naprawdę potrzebne w Twojej sytuacji.</p>

      <h2>Akt zgonu</h2>
      <p>Na podstawie karty zgonu urząd stanu cywilnego sporządza akt zgonu. Zgon trzeba zgłosić w ciągu 3 dni od wystawienia karty zgonu. Na podstawie upoważnienia od rodziny możemy załatwić to w urzędzie w Twoim imieniu.</p>

      <h2>Zasiłek pogrzebowy i pogrzeb bezgotówkowy</h2>
      <p>Po śmierci osoby ubezpieczonej, emeryta lub rencisty przysługuje zasiłek pogrzebowy - z ZUS lub KRUS, a w przypadku służb mundurowych z MSWiA lub MON.</p>
      <p>Pogrzeb możemy zorganizować bezgotówkowo: koszty rozliczamy bezpośrednio z zasiłku pogrzebowego, więc rodzina nie musi wykładać pieniędzy z góry. Szczegóły, w tym ewentualną dopłatę ponad kwotę zasiłku, omówimy przy ustalaniu pogrzebu.</p>

      <h2>Co ustalamy przy organizacji pogrzebu</h2>
      <ul>
        <li>Termin i miejsce ceremonii oraz cmentarz.</li>
        <li>Pogrzeb tradycyjny z trumną albo pogrzeb z kremacją.</li>
        <li>Trumnę lub urnę, ubranie i przygotowanie zmarłego.</li>
        <li>Oprawę: muzykę, wieńce i wiązanki, dekoracje.</li>
        <li>Transport zmarłego i, jeśli trzeba, autokar dla uczestników pogrzebu.</li>
        <li>Prace na cmentarzu, a później pomnik lub nagrobek.</li>
      </ul>
      <p>Usługi wykonujemy sami albo je koordynujemy, tak aby rodzina miała jeden kontakt w sprawie całego pogrzebu. <a href="{R}oferta/">Zobacz pełną ofertę</a>.</p>

      <p class="uwaga">Opis ma charakter ogólny. Szczegóły mogą się różnić w zależności od sytuacji, urzędu i parafii - zawsze chętnie podpowiemy przez telefon.</p>
    </div>
    <aside class="gdy-tel" aria-label="Telefony">
      <p>Telefon całodobowy</p>
      <a href="{TEL[1]}">{TEL[0]}</a>
      <p class="gdy-tel-inne">tel. <a href="{TEL_STACJ[1]}">{TEL_STACJ[0]}</a><br>kom. <a href="{TEL_KOM[1]}">{TEL_KOM[0]}</a></p>
      <p style="margin-top:14px">Odbieramy o każdej porze, także w nocy, w niedziele i w święta.</p>
    </aside>
  </div>
</section>'''
    zapisz('gdy-umrze-bliska-osoba', strona('gdy-umrze-bliska-osoba/', 'Co zrobić, gdy umrze bliska osoba - poradnik | Morfeusz',
                                             'Krok po kroku: karta zgonu, akt zgonu, dokumenty, zasiłek pogrzebowy i pogrzeb bezgotówkowy. Zakład Pogrzebowy „Morfeusz”, Wrzosowa k. Częstochowy, całą dobę 601 460 964.',
                                             tresc, schemy=[okruszki('gdy-umrze-bliska-osoba/', 'Gdy umrze bliska osoba')]))


# ---------------------------------------------------------------- galeria
def galeria():
    R = '../'
    S = '(max-width:380px) 100vw, (max-width:900px) 50vw, 380px'
    grupy = [
        ('Siedziba i biuro', 'W biurze zakładu przy ul. Górnej 30 ustalamy szczegóły pogrzebu, można też wybrać urnę i trumnę.', [
            ('biuro', 'Biuro obsługi'), ('urny', 'Urny w zakładzie')]),
        ('Kaplica', 'Przy zakładzie jest kaplica, w której rodzina może pożegnać zmarłego przed pogrzebem.', [
            ('kaplica', 'Kaplica przy zakładzie'), ('kaplica-ceremonia', 'Kaplica przed pożegnaniem')]),
        ('Ceremonia', 'Przygotowujemy oprawę ceremonii w kościele: urnę lub trumnę na katafalku, świece, wieńce i wiązanki.', [
            ('ceremonia-kosciol', 'Oprawa ceremonii w kościele')]),
        ('Chłodnia i transport', 'Własna chłodnia i karawany pozwalają nam zająć się zmarłym od razu, o każdej porze.', [
            ('chlodnia', 'Własna chłodnia'), ('karawan', 'Karawan zakładu'), ('karawany-kosciol', 'Karawany przed kościołem')]),
        ('Na cmentarzu', 'Przy grobie rozstawiamy namiot z zasłonami, teren wokół wykładamy matą, a przy pogrzebie urnowym przygotowujemy stojak na urnę.', [
            ('namiot-cmentarz', 'Namiot zakładu w alei cmentarza'), ('grob-namiot', 'Grób przygotowany do pochówku'),
            ('stojak-urna', 'Stojak na urnę ze świecami'), ('pogrzeb-urnowy', 'Przygotowanie do pogrzebu urnowego'),
            ('namiot-zima', 'Namiot przy pogrzebie urnowym'), ('urna-grob', 'Urna z wiązanką róż')]),
    ]
    g = ''
    for h, opis, zd in grupy:
        figs = ''.join(f'''
      <figure><a href="{R}img/{najwiekszy(n)}">{img(n, a, S, R)}</a><figcaption>{a}</figcaption></figure>''' for n, a in zd)
        g += f'''  <div class="gal-grupa">
    <h2>{h}</h2>
    <p>{opis}</p>
    <div class="gal">{figs}
    </div>
  </div>
'''
    tresc = ph('Zakład we Wrzosowej',
               'Zakład Pogrzebowy „Morfeusz” mieści się przy ul. Górnej 30 we Wrzosowej, w gminie Poczesna pod Częstochową. Mamy własną kaplicę, chłodnię i karawany. Poniżej zdjęcia zakładu i ceremonii, które przygotowywaliśmy.',
               R, 'siedziba', 'Budynek Zakładu Pogrzebowego Morfeusz') + f'''

<section class="sec">
  <div class="wrap">
{g}  </div>
</section>'''
    zapisz('galeria', strona('galeria/', 'Zakład i galeria - Zakład Pogrzebowy Morfeusz, Wrzosowa',
                             'Siedziba zakładu przy ul. Górnej 30 we Wrzosowej, kaplica, własna chłodnia, karawany oraz zdjęcia przygotowania ceremonii na cmentarzach w okolicach Częstochowy.',
                             tresc, schemy=[okruszki('galeria/', 'O zakładzie')]))


# ---------------------------------------------------------------- kontakt
def kontakt():
    R = '../'
    tresc = ph('Kontakt',
               'Zakład jest czynny całą dobę, w dni powszednie i święta. W pilnej sprawie najlepiej zadzwonić.', R) + f'''

<section class="sec">
  <div class="wrap kontakt">
{blok_kontakt(R).replace('<h2>Kontakt</h2>', '<h2>Telefony i adres</h2>')}
{blok_mapa(R)}
  </div>
</section>

<section class="sec sec-alt" id="formularz">
  <div class="wrap form-sek">
    <div>
      <h2>Napisz do nas</h2>
      <div class="tx">
        <p>Formularz jest dla spraw, które mogą chwilę poczekać - na przykład pytań o pomnik, nagrobek urnowy czy naprawę pomnika.</p>
        <p>Jeśli bliska osoba właśnie zmarła, prosimy dzwonić: <a href="{TEL[1]}"><strong>{TEL[0]}</strong></a>. Odbieramy całą dobę.</p>
      </div>
      <p class="k-firma">Zakład Pogrzebowy „MORFEUSZ” Ireneusz Jeziorowski<br>NIP 573-170-69-29, REGON 150320820</p>
    </div>
    <form class="form" id="form-kontakt" novalidate data-adres="{FORM_ADRES}">
      <div>
        <label for="f-imie">Imię i nazwisko</label>
        <input id="f-imie" name="imie" type="text" autocomplete="name" required>
      </div>
      <div class="form-2">
        <div>
          <label for="f-tel">Telefon</label>
          <input id="f-tel" name="telefon" type="tel" autocomplete="tel" inputmode="tel">
        </div>
        <div>
          <label for="f-mail">E-mail <span>(jeśli wolisz odpowiedź mailem)</span></label>
          <input id="f-mail" name="email" type="email" autocomplete="email">
        </div>
      </div>
      <div>
        <label for="f-tresc">Wiadomość</label>
        <textarea id="f-tresc" name="wiadomosc" rows="6" required></textarea>
      </div>
      <div class="hp" aria-hidden="true"><label for="f-hp">Nie wypełniaj tego pola</label><input id="f-hp" name="_honey" type="text" tabindex="-1" autocomplete="off"></div>
      <p class="form-info">Podane dane wykorzystamy wyłącznie do odpowiedzi na wiadomość. Więcej w <a href="{R}polityka-prywatnosci/">polityce prywatności</a>.</p>
      <div class="form-wynik" aria-live="polite"></div>
      <button type="submit">Wyślij wiadomość</button>
    </form>
  </div>
</section>'''
    zapisz('kontakt', strona('kontakt/', 'Kontakt - Zakład Pogrzebowy Morfeusz, Wrzosowa, ul. Górna 30',
                             'Zakład Pogrzebowy „Morfeusz”, ul. Górna 30, 42-263 Wrzosowa (gm. Poczesna). Telefon całodobowy 601 460 964, tel. 34 327 51 06, kom. 603 847 926, zpmorfeusz@onet.eu.',
                             tresc, schemy=[schema_firma(), okruszki('kontakt/', 'Kontakt')]))


# ---------------------------------------------------------------- polityka
def polityka():
    R = '../'
    tresc = ph('Polityka prywatności', 'Zasady przetwarzania danych osobowych na stronie Zakładu Pogrzebowego „Morfeusz”.', R, tel=False) + f'''

<section class="sec">
  <div class="wrap prawny">
    <h2>Administrator danych</h2>
    <p>Administratorem danych osobowych jest Ireneusz Jeziorowski, prowadzący działalność gospodarczą pod nazwą Zakład Pogrzebowy „MORFEUSZ” Ireneusz Jeziorowski, ul. Górna 30, 42-263 Wrzosowa, NIP 573-170-69-29, REGON 150320820. Kontakt: <a href="mailto:{MAIL}">{MAIL}</a>, tel. <a href="{TEL_STACJ[1]}">{TEL_STACJ[0]}</a>.</p>

    <h2>Jakie dane i w jakim celu</h2>
    <p>Przetwarzamy dane, które przekazujesz nam sam: przez formularz kontaktowy (imię i nazwisko, numer telefonu, adres e-mail, treść wiadomości), telefonicznie lub e-mailem. Wykorzystujemy je wyłącznie do odpowiedzi na wiadomość i do przygotowania lub wykonania usługi, o którą pytasz.</p>
    <p>Podstawą prawną jest podjęcie działań na Twoje żądanie przed zawarciem umowy i jej wykonanie (art. 6 ust. 1 lit. b RODO) oraz nasz prawnie uzasadniony interes, czyli udzielenie odpowiedzi na pytanie (art. 6 ust. 1 lit. f RODO). Podanie danych jest dobrowolne, ale bez numeru telefonu lub adresu e-mail nie będziemy mogli odpowiedzieć.</p>

    <h2>Komu przekazujemy dane</h2>
    <p>Wiadomości z formularza są przekazywane na naszą skrzynkę e-mail za pośrednictwem usługi FormSubmit (formsubmit.co). Dane mogą też trafić do dostawcy hostingu strony i dostawcy poczty e-mail - wyłącznie w zakresie potrzebnym do działania tych usług. Korzystanie z usługi FormSubmit może wiązać się z przekazaniem danych poza Europejski Obszar Gospodarczy.</p>

    <h2>Jak długo przechowujemy dane</h2>
    <p>Dane z wiadomości przechowujemy przez czas potrzebny do załatwienia sprawy, a jeśli dojdzie do wykonania usługi - przez okres wymagany przepisami (np. podatkowymi) oraz okres przedawnienia ewentualnych roszczeń.</p>

    <h2>Twoje prawa</h2>
    <p>Masz prawo dostępu do swoich danych, ich sprostowania, usunięcia lub ograniczenia przetwarzania, a także prawo sprzeciwu wobec przetwarzania. W tych sprawach napisz na <a href="mailto:{MAIL}">{MAIL}</a>. Masz też prawo wnieść skargę do Prezesa Urzędu Ochrony Danych Osobowych.</p>

    <h2>Pliki cookies i statystyki</h2>
    <p>Strona nie używa plików cookies ani narzędzi statystycznych i reklamowych. Mapa na stronie jest obrazkiem - dopiero po jej kliknięciu otwiera się serwis Mapy Google lub OpenStreetMap, który działa według własnych zasad prywatności.</p>
  </div>
</section>'''
    zapisz('polityka-prywatnosci', strona('polityka-prywatnosci/', 'Polityka prywatności - Zakład Pogrzebowy Morfeusz',
                                           'Zasady przetwarzania danych osobowych na stronie Zakładu Pogrzebowego „Morfeusz” we Wrzosowej: administrator, cel, prawa, pliki cookies.',
                                           tresc))


def nie_znaleziono():
    R = BASE_404
    tresc = f'''<section class="ph ph-bez">
  <div class="wrap ph-in">
    <div>
      <h1>Nie znaleziono strony</h1>
      <p class="ph-lead">Ta strona nie istnieje albo zmieniła adres. Zobacz <a href="{R}">stronę główną</a>, <a href="{R}oferta/">ofertę</a> lub <a href="{R}kontakt/">kontakt</a>.</p>
      <p class="ph-tel">Telefon całodobowy: <a href="{TEL[1]}">{TEL[0]}</a></p>
    </div>
  </div>
</section>'''
    s = strona('404', 'Nie znaleziono strony - Zakład Pogrzebowy Morfeusz', 'Strona nie istnieje.', tresc, noindex=True, base=R)
    zapisz('', s, '404.html')


def sitemap_robots():
    urls = ['', 'oferta/', 'gdy-umrze-bliska-osoba/', 'galeria/', 'kontakt/', 'polityka-prywatnosci/']
    pri = {'': '1.0', 'polityka-prywatnosci/': '0.3'}
    x = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        x += f'  <url><loc>{DOMENA}/{u}</loc><priority>{pri.get(u, "0.8")}</priority></url>\n'
    x += '</urlset>\n'
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write(x)
    open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8', newline='\n').write(
        f'User-agent: *\nAllow: /\n\nSitemap: {DOMENA}/sitemap.xml\n')


if __name__ == '__main__':
    glowna(); oferta(); poradnik(); galeria(); kontakt(); polityka(); nie_znaleziono(); sitemap_robots()
    print('Zbudowano:', 'PRODUKCJA' if PROD else 'TEST (noindex, formularz testowy)')
