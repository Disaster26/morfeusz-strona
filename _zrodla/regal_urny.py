# 04.11d: nowe zdjecie regalu z urnami od klienta (30.10.2026) - obrobka "profesjonalnie, prosto":
# 1) korekta perspektywy przez obrot wirtualnej kamery (punkty zbiegu z 4 naroznikow regalu,
#    ogniskowa z warunku prostopadlosci) - piony regalu pionowe, polki poziome, bez sztucznego rozciagania proporcji,
# 2) kadr do samego regalu (bez sciany po lewej, bez obcego mebla po prawej, bez podlogi), waskie brzegi bocznych scianek,
#    brakujace trojkaty bocznej scianki u gory (poza oryginalnym kadrem) uzupelnione odbiciem slojow scianki z dolu,
# 3) balans bieli sprawdzony na bialej urnie-sercu (byla neutralna) - tylko minimalne zbicie zoltego w swiatlach,
# 4) lekkie rozjasnienie cieni i kontrast w srodkowych tonach (krzywa na L w LAB), lekkie wyostrzenie.
import numpy as np, cv2
from PIL import Image, ImageOps, ImageFilter

SRC = r"C:\Users\Admin\Downloads\Odrobimy_kampania\klienci\Morfeusz\zdjecia_klienta_0411\urny_regal_20261030_181040.jpg"
# narozniki: dolna krawedz frontu polki 1 i 4 przy wewnetrznych krawedziach bocznych scianek (piksele oryginalu 3000x4000)
NAROZ = [(115, 1118), (2965, 905), (460, 3195), (2765, 3545)]  # LG, PG, LD, PD
KADR = (1132, 445, 4142, 4470)  # w ukladzie obrazu po korekcie


def _homografia(w, h):
    P = lambda p: np.array([p[0], p[1], 1.])
    TL, TR, BL, BR = map(P, NAROZ)
    v1 = np.cross(np.cross(TL, TR), np.cross(BL, BR)); v1 /= v1[2]
    v2 = np.cross(np.cross(TL, BL), np.cross(TR, BR)); v2 /= v2[2]
    c = np.array([w / 2, h / 2])
    f = np.sqrt(-(v1[:2] - c) @ (v2[:2] - c))
    K = np.array([[f, 0, c[0]], [0, f, c[1]], [0, 0, 1]]); Ki = np.linalg.inv(K)
    d1 = Ki @ v1; d1 /= np.linalg.norm(d1); d1 *= np.sign(d1[0])
    d2 = Ki @ v2; d2 /= np.linalg.norm(d2); d2 *= np.sign(d2[1])
    d2 = d2 - (d2 @ d1) * d1; d2 /= np.linalg.norm(d2)
    R = np.stack([d1, d2, np.cross(d1, d2)], 1)
    H = K @ R.T @ Ki
    rog = np.array([H @ np.array([x, y, 1.]) for x, y in [(0, 0), (w, 0), (0, h), (w, h)]])
    rog = rog[:, :2] / rog[:, 2:]
    T = np.array([[1, 0, -rog[:, 0].min() + 20], [0, 1, -rog[:, 1].min() + 20], [0, 0, 1]])
    return T @ H, int(np.ptp(rog[:, 0]) + 40), int(np.ptp(rog[:, 1]) + 40)


def _krzywa():
    x = np.linspace(0, 1, 256)
    y = x + 0.42 * x * (1 - x) ** 2           # cienie w gore (najmocniej ok. 1/3 jasnosci)
    y = 0.5 + (y - 0.5) * 1.06                  # lekki kontrast
    return np.clip(y * 255, 0, 255).astype(np.uint8)


def regal_urny():
    im = np.asarray(ImageOps.exif_transpose(Image.open(SRC)).convert('RGB'))
    h, w = im.shape[:2]
    H, W_, H_ = _homografia(w, h)
    a = cv2.warpPerspective(im, H, (W_, H_), flags=cv2.INTER_LANCZOS4)
    ok = cv2.warpPerspective(np.full((h, w), 255, np.uint8), H, (W_, H_), flags=cv2.INTER_NEAREST)
    ok = cv2.erode(ok, np.ones((5, 5), np.uint8))  # bez rozmytej krawedzi oryginalu
    x0, y0, x1, y1 = KADR
    a = a[y0:y1, x0:x1].copy(); ok = ok[y0:y1, x0:x1] > 0
    # uzupelnienie brakujacych naroznikow (tylko waskie paski bocznych scianek u gory): odbicie kolumny od pierwszego dobrego piksela
    for x in np.where(~ok.all(0))[0]:
        col = ok[:, x]
        if not col.any(): continue
        y_ok = np.argmax(col)
        n = y_ok
        if n == 0: continue
        src = a[y_ok:y_ok + n, x][::-1] if y_ok + n <= a.shape[0] else None
        if src is not None and len(src) == n:
            a[:y_ok, x] = src
    # balans bieli: urna-serce prawie neutralna; tylko lekkie zbicie zoltego (b w LAB) w jasnych partiach
    lab = cv2.cvtColor(a, cv2.COLOR_RGB2LAB).astype(np.float32)
    L = lab[..., 0] / 255.
    lab[..., 2] = 128 + (lab[..., 2] - 128) * (1 - 0.10 * L)
    lab[..., 0] = cv2.LUT(lab[..., 0].astype(np.uint8), _krzywa()).astype(np.float32)
    a = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    out = Image.fromarray(a).filter(ImageFilter.UnsharpMask(radius=2.0, percent=45, threshold=3))
    return out


if __name__ == '__main__':
    import sys
    regal_urny().save(sys.argv[1], quality=93)
