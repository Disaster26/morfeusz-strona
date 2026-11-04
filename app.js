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

  // Powiekszanie zdjec (lekki lightbox): klik / Enter / spacja na zdjeciu, zamkniecie X, Esc, klik w tlo, gest w gore/dol,
  // strzalki (klawiatura, przyciski, gest w bok) gdy na stronie jest kilka zdjec. Wczytuje wersje 1200 px.
  (function () {
    var zdjecia = [].slice.call(document.querySelectorAll('main img')).filter(function (im) {
      return !im.classList.contains('foto-tlo') && !im.closest('.mapa') && im.getAttribute('srcset');
    });
    if (!zdjecia.length) return;
    function duze(im) {
      var lista = im.getAttribute('srcset').split(',').map(function (s) {
        var p = s.trim().split(/\s+/); return { u: p[0], w: parseInt(p[1], 10) || 0 };
      }).sort(function (a, b) { return a.w - b.w; });
      var wyb = lista[lista.length - 1];
      for (var i = 0; i < lista.length; i++) if (lista[i].w >= 1200) { wyb = lista[i]; break; }
      return wyb.u;
    }
    function opis(im) {
      var fig = im.closest('figure');
      var fc = fig && fig.querySelector('figcaption');
      return (fc && fc.textContent.trim()) || im.alt || '';
    }
    var lb = document.createElement('div');
    lb.className = 'lb';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Powiększone zdjęcie');
    lb.hidden = true;
    lb.innerHTML = '<figure class="lb-fig"><img class="lb-img" alt=""><figcaption class="lb-opis"></figcaption></figure>'
      + '<button type="button" class="lb-x" aria-label="Zamknij powiększenie"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg></button>'
      + '<button type="button" class="lb-pop" aria-label="Poprzednie zdjęcie"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 4l-8 8 8 8"/></svg></button>'
      + '<button type="button" class="lb-nast" aria-label="Następne zdjęcie"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4l8 8-8 8"/></svg></button>'
      + '<p class="lb-licz" aria-live="polite"></p>';
    document.body.appendChild(lb);
    var lbImg = lb.querySelector('.lb-img'), lbOpis = lb.querySelector('.lb-opis'), lbLicz = lb.querySelector('.lb-licz');
    var bX = lb.querySelector('.lb-x'), bPop = lb.querySelector('.lb-pop'), bNast = lb.querySelector('.lb-nast');
    var wiele = zdjecia.length > 1;
    if (!wiele) { bPop.hidden = true; bNast.hidden = true; lbLicz.hidden = true; }
    var nr = 0, powrot = null;
    function pokazNr(i) {
      nr = (i + zdjecia.length) % zdjecia.length;
      var im = zdjecia[nr], u = duze(im);
      lbImg.src = im.currentSrc || im.src;   // od razu to, co juz wczytane, potem ostre 1200 px
      lbImg.alt = im.alt;
      var pre = new Image();
      pre.onload = function () { if (zdjecia[nr] === im) lbImg.src = u; };
      pre.src = u;
      lbOpis.textContent = opis(im);
      lbLicz.textContent = (nr + 1) + ' / ' + zdjecia.length;
    }
    function otworz(i) {
      powrot = document.activeElement;
      pokazNr(i);
      lb.hidden = false;
      document.documentElement.classList.add('lb-otw');
      bX.focus();
    }
    function zamknijLb() {
      lb.hidden = true;
      document.documentElement.classList.remove('lb-otw');
      lbImg.removeAttribute('src');
      if (powrot && powrot.focus) powrot.focus();
    }
    zdjecia.forEach(function (im, i) {
      var link = im.closest('a');
      if (link) {
        // galeria: link do pliku zdjecia (bez JS otwiera samo zdjecie) - z JS lightbox
        link.addEventListener('click', function (e) { e.preventDefault(); otworz(i); });
        link.setAttribute('aria-label', 'Powiększ zdjęcie: ' + opis(im));
      } else {
        im.tabIndex = 0;
        im.setAttribute('role', 'button');
        im.setAttribute('aria-label', 'Powiększ zdjęcie: ' + (im.alt || opis(im)));
        im.addEventListener('click', function () { otworz(i); });
        im.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); otworz(i); }
        });
      }
      im.classList.add('zoom');
    });
    bX.addEventListener('click', zamknijLb);
    bPop.addEventListener('click', function () { pokazNr(nr - 1); });
    bNast.addEventListener('click', function () { pokazNr(nr + 1); });
    lb.addEventListener('click', function (e) {
      if (e.target === lb || e.target.classList.contains('lb-fig')) zamknijLb();
    });
    document.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') { e.preventDefault(); zamknijLb(); }
      else if (wiele && e.key === 'ArrowLeft') pokazNr(nr - 1);
      else if (wiele && e.key === 'ArrowRight') pokazNr(nr + 1);
      else if (e.key === 'Tab') {   // fokus zostaje w oknie powiekszenia
        var b = [bX, bPop, bNast].filter(function (x) { return !x.hidden; });
        var k = b.indexOf(document.activeElement);
        e.preventDefault();
        b[(k + (e.shiftKey ? -1 : 1) + b.length) % b.length].focus();
      }
    });
    var x0 = null, y0 = 0;
    lb.addEventListener('touchstart', function (e) {
      if (e.touches.length !== 1) { x0 = null; return; }
      x0 = e.touches[0].clientX; y0 = e.touches[0].clientY;
    }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
      x0 = null;
      if (Math.abs(dy) > 80 && Math.abs(dy) > Math.abs(dx)) zamknijLb();
      else if (wiele && Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) pokazNr(nr + (dx < 0 ? 1 : -1));
    }, { passive: true });
  })();

  // Formularz kontaktowy: wysylka przez wyslij.php na serwerze strony (adres w atrybucie data-adres formularza).
  // Znacznik antyspamowy (podpisana godzina) z wyslij.php?znacznik=1; wysylka najwczesniej ok. 3,5 s po jego pobraniu.
  var f = document.getElementById('form-kontakt');
  if (!f) return;
  var wynik = f.querySelector('.form-wynik');
  var ADRES = f.getAttribute('data-adres');
  var AWARIA = 'Nie udało się wysłać wiadomości. Prosimy zadzwonić: 601 460 964 (całą dobę) albo napisać na zpmorfeusz@onet.eu.';
  var znacznik = '', znacznikCzas = 0;
  function pobierzZnacznik() {
    return fetch(ADRES + '?znacznik=1', { headers: { 'Accept': 'application/json' }, cache: 'no-store', credentials: 'same-origin' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) {
        if (j && typeof j.z === 'string' && /^\d{10}\.[0-9a-f]{64}$/.test(j.z)) { znacznik = j.z; znacznikCzas = Date.now(); return true; }
        return false;
      })
      .catch(function () { return false; });
  }
  function gotowyZnacznik() {
    var start = (!znacznik || Date.now() - znacznikCzas > 6e6) ? pobierzZnacznik() : Promise.resolve(true);
    return start.then(function (ok) {
      if (!ok) return false;
      var czekaj = 3500 - (Date.now() - znacznikCzas);
      return czekaj > 0 ? new Promise(function (r) { setTimeout(function () { r(true); }, czekaj); }) : true;
    });
  }
  pobierzZnacznik();
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
  var wTrakcie = false;
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    if (wTrakcie) return;
    var imie = f.elements['imie'], telefon = f.elements['telefon'], mail = f.elements['email'], tresc = f.elements['wiadomosc'];
    var ok = true;
    var vi = imie.value.trim().length >= 2; oznacz(imie, !vi, 'Wpisz imię.'); ok = ok && vi;
    var t = telefon.value.replace(/[\s()+.-]/g, ''), m = mail.value.trim();
    var vt = t === '' || (/^\d{9,13}$/.test(t) && /^[\d\s()+.-]+$/.test(telefon.value.trim()));
    var vm = m === '' || /^[^\s@,;<>"]+@[^\s@,;<>"]+\.[^\s@,;<>"]{2,}$/.test(m);
    oznacz(telefon, !vt, 'Wpisz poprawny numer telefonu.');
    oznacz(mail, !vm, 'Wpisz poprawny adres e-mail.');
    ok = ok && vt && vm;
    if (vt && vm && t === '' && m === '') { oznacz(telefon, true, 'Podaj telefon albo e-mail, żebyśmy mogli odpowiedzieć.'); ok = false; }
    var vw = tresc.value.trim().length >= 5; oznacz(tresc, !vw, 'Wpisz treść wiadomości.'); ok = ok && vw;
    if (!ok) { pokaz('Popraw zaznaczone pola i wyślij ponownie.', true); return; }
    var btn = f.querySelector('button[type="submit"]');
    wTrakcie = true; btn.disabled = true; btn.textContent = 'Wysyłanie...';
    function koniec() { wTrakcie = false; btn.disabled = false; btn.textContent = 'Wyślij wiadomość'; }
    function wyslij(ponowka) {
      var dane = new URLSearchParams();
      dane.append('imie', imie.value.trim());
      dane.append('telefon', telefon.value.trim());
      dane.append('email', m);
      dane.append('wiadomosc', tresc.value.trim());
      dane.append('_honey', f.elements['_honey'].value);
      dane.append('skad', location.pathname);
      dane.append('_z', znacznik);
      return fetch(ADRES, { method: 'POST', credentials: 'same-origin',
        headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }, body: dane })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { s: r.status, j: j || {} }; }); })
        .then(function (o) {
          if (o.s === 403 && o.j.blad === 'znacznik' && !ponowka) {   // np. zmiana sieci - nowy znacznik i jedna ponowka
            znacznik = '';
            return gotowyZnacznik().then(function (z) { if (z) return wyslij(true); pokaz(AWARIA, true); koniec(); });
          }
          koniec();
          if (o.s === 200 && o.j.success === true) {
            pokaz('Dziękujemy, wiadomość została wysłana. Odpowiemy najszybciej, jak to możliwe.'
              + (o.j.potwierdzenie ? ' Potwierdzenie wysłaliśmy na podany adres - jeśli go nie widać, prosimy sprawdzić folder SPAM.' : '')
              + ' W pilnej sprawie prosimy dzwonić: 601 460 964.', false);
            f.reset(); znacznik = ''; pobierzZnacznik();
          } else if (o.s === 403 && o.j.blad === 'szybko') {
            pokaz('Formularz został wysłany zbyt szybko. Prosimy odczekać chwilę i kliknąć Wyślij jeszcze raz - dane zostały w formularzu.', true);
          } else if (o.s === 422) {
            pokaz('Coś jest nie tak z danymi w formularzu - prosimy je sprawdzić. W pilnej sprawie prosimy dzwonić: 601 460 964.', true);
          } else if (o.s === 429) {
            pokaz('Wysłano już kilka wiadomości. Prosimy spróbować później albo zadzwonić: 601 460 964 (całą dobę).', true);
          } else {
            pokaz(AWARIA, true);
          }
        });
    }
    gotowyZnacznik()
      .then(function (z) { if (z) return wyslij(false); pokaz(AWARIA, true); koniec(); })
      .catch(function () { pokaz('Brak połączenia, wiadomość nie została wysłana. Prosimy zadzwonić: 601 460 964 (całą dobę).', true); koniec(); });
  });
})();
