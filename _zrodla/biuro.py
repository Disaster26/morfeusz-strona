# 04.11d: aktualne zdjecia biura od klienta (04.11.2026, Galaxy A56). Obrobka: piony wyprostowane obrotem wirtualnej kamery,
# kadr bez przypadkowych elementow, rozmyte tabliczki z nazwiskami / ulotki / dokumenty i wyswietlacze na biurku,
# delikatny balans bieli, rozjasnione cienie, lekkie wyostrzenie. Tresc certyfikatu bez retuszu (tylko prostowanie i kadr).
import os, numpy as np, cv2
from prostowanie import otworz, ogniskowa, punkt_zbiegu_pionow, obrot_do_pionu, tony, rozmyj, wyostrz, wb_szary
from PIL import Image

D = r"C:\Users\Admin\Downloads\Odrobimy_kampania\klienci\Morfeusz\zdjecia_klienta_0411"
PELNE = D  # obrobione pliki w pelnej rozdzielczosci obok oryginalow (*_obrobione.jpg)


def _pion(plik):
    a = otworz(os.path.join(D, plik)); h, w = a.shape[:2]
    v, _, _ = punkt_zbiegu_pionow(a)
    o, m, _ = obrot_do_pionu(a, v, ogniskowa(w, h))
    return o, o.shape[1] / 1000  # wspolrzedne ponizej w skali podgladu 1000 px szerokosci


def _px(b, k):
    return tuple(int(round(x * k)) for x in b)


def _kadr(o, b, k):
    x0, y0, x1, y1 = _px(b, k)
    return o[y0:y1, x0:x1], (x0, y0)


def _rozmyj_p(o, boxy, k, r=14):
    # rozmycie umiarkowane: napisy nieczytelne (takze w pelnej rozdzielczosci), ksztalty przedmiotow zostaja
    return rozmyj(o, [_px(b, k) for b in boxy], r)


def biuro_cale():
    """140815: cale biuro - sofa, biurko obslugi, regaly z urnami (glowne zdjecie biura)."""
    o, k = _pion('biuro_1_20261104_140815.jpg')
    o = _rozmyj_p(o, [(322, 68, 388, 114),            # tabliczki nagrobne z nazwiskami na scianie
                      (98, 140, 302, 192),            # tabliczki, ulotki ze zdjeciem osoby pod polka
                      (362, 150, 470, 200),           # dokumenty i segregatory przy drukarce
                      (438, 216, 528, 246)], k, r=12)  # kartki i wyswietlacz na biurku
    o, _ = _kadr(o, (146, 6, 850, 534), k)
    o = tony(o, cienie=0.30, kontrast=1.04, zolty=0.10)
    return wyostrz(o)


def biuro_sofa():
    """140506: kacik z sofa, akwarium i polkami z urnami."""
    o, k = _pion('biuro_1_20261104_140506.jpg')
    o = _rozmyj_p(o, [(276, 163, 320, 260),           # czarne tabliczki z imionami
                      (343, 250, 668, 314),           # tabliczki z nazwiskami, ulotki, zdjecie osoby
                      (796, 190, 864, 250),           # tabliczka S.P.
                      (864, 166, 942, 252),           # tabliczka nagrobna z nazwiskiem i data
                      (650, 522, 690, 560),           # karteczka na biurku
                      (690, 520, 875, 640),           # dokumenty na biurku
                      (866, 352, 912, 486)], k, r=12)  # papiery w segregatorach
    o, _ = _kadr(o, (106, 16, 866, 586), k)
    o = tony(o, cienie=0.30, kontrast=1.04, zolty=0.08)
    return wyostrz(o)


def kacik_las():
    """140612 (pion): kacik z fototapeta lasu, krzesla, podswietlany regal z urnami."""
    o, k = _pion('biuro_1_20261104_140612.jpg')
    o, _ = _kadr(o, (186, 42, 724, 930), k)
    o = tony(o, cienie=0.28, kontrast=1.04, zolty=0.06)
    return wyostrz(o)


def certyfikat():
    """140711: certyfikat Elitarny Lider Jakosci 2026 - tylko korekta perspektywy (nadrukowana ramka -> prostokat) i kadr."""
    a = otworz(os.path.join(D, 'biuro_1_20261104_140711.jpg'))
    src = np.float32([(700, 477), (3672, 493), (740, 2562), (3642, 2512)])
    W, H = 2937, 2052; m = 300
    dst = np.float32([(m, m), (m + W, m), (m, m + H), (m + W, m + H)])
    M = cv2.getPerspectiveTransform(src, dst)
    o = cv2.warpPerspective(a, M, (W + 2 * m, H + 2 * m), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    o = tony(o, cienie=0.15, kontrast=1.03)
    return wyostrz(o, 1.6, 35)


def statuetka():
    """140945 (pion): statuetka Elitarny Lider Jakosci 2026 na polce miedzy urnami."""
    a = otworz(os.path.join(D, 'biuro_0_20261104_140945.jpg'))
    o = a[380:3780, 760:2640]
    o = tony(o, cienie=0.22, kontrast=1.04, zolty=0.05)
    return wyostrz(o)


WSZYSTKIE = [('biuro-morfeusz-wrzosowa', biuro_cale), ('biuro-sofa-urny', biuro_sofa), ('biuro-kacik-las', kacik_las),
             ('certyfikat-elitarny-lider-2026', certyfikat), ('statuetka-elitarny-lider-2026', statuetka)]

if __name__ == '__main__':
    import sys
    out = sys.argv[1]
    for n, fn in WSZYSTKIE:
        im = fn(); im.save(os.path.join(out, n + '.jpg'), quality=92); print(n, im.size)
