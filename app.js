(function () {
  // Menu na telefonie
  var burger = document.getElementById('burger');
  var nav = document.getElementById('nav');
  function zamknij() { nav.classList.remove('otw'); burger.setAttribute('aria-expanded', 'false'); burger.setAttribute('aria-label', 'Otwórz menu'); }
  burger.addEventListener('click', function () {
    var otw = nav.classList.toggle('otw');
    burger.setAttribute('aria-expanded', otw ? 'true' : 'false');
    burger.setAttribute('aria-label', otw ? 'Zamknij menu' : 'Otwórz menu');
  });
  nav.addEventListener('click', function (e) { if (e.target.tagName === 'A') zamknij(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') zamknij(); });

  // Strona glowna: telefon w naglowku i dolny pasek pokazuja sie po przewinieciu za duzy przycisk w hero.
  // Na podstronach sa widoczne od razu (CSS).
  var tel = document.getElementById('telMain');
  if (tel) {
    var mob = document.getElementById('mob');
    var topTel = document.querySelector('.top-tel');
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (wpisy) {
        var w = wpisy[0];
        var pokaz = !w.isIntersecting && w.boundingClientRect.top < 0;
        mob.classList.toggle('widac', pokaz);
        topTel.classList.toggle('widac', pokaz);
      }, { threshold: 0 }).observe(tel);
    } else {
      mob.classList.add('widac'); topTel.classList.add('widac');
    }
  }

  // Formularz kontaktowy (FormSubmit). Adres odbiorcy w atrybucie data-adres formularza.
  var f = document.getElementById('form-kontakt');
  if (!f) return;
  var wynik = f.querySelector('.form-wynik');
  function pokaz(tekst, blad) {
    wynik.textContent = tekst;
    wynik.className = 'form-wynik ' + (blad ? 'blad' : 'ok');
    wynik.setAttribute('role', blad ? 'alert' : 'status');
  }
  function oznacz(el, zle, tekst) {
    var w = el.parentNode.querySelector('.pole-blad');
    el.setAttribute('aria-invalid', zle ? 'true' : 'false');
    if (zle) {
      if (!w) { w = document.createElement('span'); w.className = 'pole-blad'; el.insertAdjacentElement('afterend', w); }
      w.textContent = tekst;
    } else if (w) { w.remove(); }
  }
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var imie = f.elements['imie'], telefon = f.elements['telefon'], mail = f.elements['email'], tresc = f.elements['wiadomosc'];
    var ok = true;
    var vi = imie.value.trim().length >= 2; oznacz(imie, !vi, 'Wpisz imię.'); ok = ok && vi;
    var t = telefon.value.replace(/[\s()+-]/g, ''), m = mail.value.trim();
    var vt = t === '' || /^\d{9,13}$/.test(t);
    var vm = m === '' || /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(m);
    oznacz(telefon, !vt, 'Wpisz poprawny numer telefonu.');
    oznacz(mail, !vm, 'Wpisz poprawny adres e-mail.');
    ok = ok && vt && vm;
    if (vt && vm && t === '' && m === '') { oznacz(telefon, true, 'Podaj telefon albo e-mail, żebyśmy mogli odpowiedzieć.'); ok = false; }
    var vw = tresc.value.trim().length >= 5; oznacz(tresc, !vw, 'Wpisz treść wiadomości.'); ok = ok && vw;
    if (!ok) { pokaz('Popraw zaznaczone pola i wyślij ponownie.', true); return; }
    if (f.elements['_honey'].value) return;
    var btn = f.querySelector('button[type="submit"]');
    btn.disabled = true; btn.textContent = 'Wysyłanie...';
    var dane = {
      _subject: 'Wiadomość ze strony zakładu Morfeusz',
      _template: 'table', _captcha: 'false',
      'Imię i nazwisko': imie.value.trim(),
      'Telefon': telefon.value.trim() || '-',
      email: m || '-',
      'Wiadomość': tresc.value.trim(),
      'Strona': location.href
    };
    if (m) dane._replyto = m;
    fetch(f.getAttribute('data-adres'), { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(dane) })
      .then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function (j) {
        if (j && (j.success === true || j.success === 'true')) {
          pokaz('Dziękujemy, wiadomość została wysłana. Odpowiemy najszybciej, jak to możliwe. W pilnej sprawie prosimy dzwonić: 601 460 964.', false);
          f.reset();
        } else {
          pokaz('Nie udało się wysłać wiadomości. Prosimy zadzwonić: 601 460 964 albo napisać na zpmorfeusz@onet.eu.', true);
        }
      })
      .catch(function () { pokaz('Brak połączenia, wiadomość nie została wysłana. Prosimy zadzwonić: 601 460 964.', true); })
      .then(function () { btn.disabled = false; btn.textContent = 'Wyślij wiadomość'; });
  });
})();
