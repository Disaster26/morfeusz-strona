# 04.11d: wspolne narzedzia do zdjec wnetrz od klienta (Galaxy A56, 23 mm ekw.):
# prostowanie pionow obrotem wirtualnej kamery (bez rozciagania), korekta tonow, lekkie wyostrzenie, rozmycie fragmentow.
import numpy as np, cv2
from PIL import Image, ImageOps, ImageFilter


def otworz(p):
    return np.asarray(ImageOps.exif_transpose(Image.open(p)).convert('RGB'))


def ogniskowa(w, h, mm35=23):
    return mm35 * np.hypot(w, h) / np.hypot(36, 24)


def punkt_zbiegu_pionow(a, max_kat=12, skala=1000):
    """Punkt zbiegu pionow z odcinkow prawie pionowych (Hough + RANSAC). Zwraca punkt w pikselach oryginalu."""
    h, w = a.shape[:2]; k = skala / max(w, h)
    g = cv2.cvtColor(cv2.resize(a, (round(w * k), round(h * k)), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    ed = cv2.Canny(cv2.GaussianBlur(g, (3, 3), 0), 50, 140)
    seg = cv2.HoughLinesP(ed, 1, np.pi / 720, 40, minLineLength=skala * 0.08, maxLineGap=4)
    L = []
    for x1, y1, x2, y2 in (seg.reshape(-1, 4) if seg is not None else []):
        dx, dy = x2 - x1, y2 - y1
        if abs(np.degrees(np.arctan2(dx, dy))) % 180 > max_kat and abs(np.degrees(np.arctan2(dx, dy))) % 180 < 180 - max_kat:
            continue
        p1 = np.array([x1 / k, y1 / k, 1.]); p2 = np.array([x2 / k, y2 / k, 1.])
        l = np.cross(p1, p2)
        L.append((l, (p1[:2] + p2[:2]) / 2, np.array([dx, dy], float) / np.hypot(dx, dy), np.hypot(dx, dy) / k))
    rng = np.random.default_rng(1); best = (0, None)
    def kat(v, mid, dr):
        if abs(v[2]) < 1e-9: u = v[:2]
        else: u = v[:2] / v[2] - mid
        u = u / (np.linalg.norm(u) + 1e-12)
        return np.degrees(np.arccos(min(1, abs(u @ dr))))
    for _ in range(3000):
        i, j = rng.choice(len(L), 2, replace=False)
        v = np.cross(L[i][0], L[j][0])
        sc = sum(d for l, mid, dr, d in L if kat(v, mid, dr) < 0.4)
        if sc > best[0]: best = (sc, v)
    # dopasowanie najmniejszych kwadratow do inlierow
    v = best[1]
    inl = [l / np.linalg.norm(l[:2]) * np.sqrt(d) for l, mid, dr, d in L if kat(v, mid, dr) < 0.4]
    _, _, Vt = np.linalg.svd(np.array(inl)); v = Vt[-1]
    v = v / v[2] if abs(v[2]) > 1e-12 else v
    return v, len(L), len(inl)


def obrot_do_pionu(a, v, f, frac=1.0, kat_poziom=0.0):
    """Obraca wirtualna kamere tak, by kierunek punktu zbiegu v byl pionowy (frac<1 = czesciowa korekta).
    kat_poziom: dodatkowy obrot wokol osi optycznej (stopnie). Zwraca obraz i maske poprawnych pikseli."""
    h, w = a.shape[:2]
    K = np.array([[f, 0, w / 2], [0, f, h / 2], [0, 0, 1]]); Ki = np.linalg.inv(K)
    d = Ki @ v; d /= np.linalg.norm(d); d *= np.sign(d[1]) if d[1] != 0 else 1
    t = np.array([0, 1., 0])
    ax = np.cross(d, t); s = np.linalg.norm(ax); ang = np.arctan2(s, d @ t) * frac
    R = cv2.Rodrigues((ax / s * ang) if s > 1e-12 else np.zeros(3))[0]
    Rz = cv2.Rodrigues(np.array([0, 0, np.radians(kat_poziom)]))[0]
    H = K @ Rz @ R @ Ki
    rog = np.array([H @ np.array([x, y, 1.]) for x, y in [(0, 0), (w, 0), (0, h), (w, h)]]); rog = rog[:, :2] / rog[:, 2:]
    T = np.array([[1, 0, -rog[:, 0].min()], [0, 1, -rog[:, 1].min()], [0, 0, 1]])
    W_, H_ = int(np.ptp(rog[:, 0])), int(np.ptp(rog[:, 1]))
    out = cv2.warpPerspective(a, T @ H, (W_, H_), flags=cv2.INTER_LANCZOS4)
    m = cv2.warpPerspective(np.full((h, w), 255, np.uint8), T @ H, (W_, H_), flags=cv2.INTER_NEAREST)
    return out, cv2.erode(m, np.ones((5, 5), np.uint8)) > 0, T @ H


def najwiekszy_prostokat(m, aspekt=None):
    """Prosty kadr: najwiekszy prostokat wpisany w maske (szukanie po wierszach/kolumnach z zawezaniem)."""
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    while True:
        sub = m[y0:y1 + 1, x0:x1 + 1]
        if sub.all(): return x0, y0, x1 + 1, y1 + 1
        brak = {'g': (~sub[0]).sum(), 'd': (~sub[-1]).sum(), 'l': (~sub[:, 0]).sum(), 'p': (~sub[:, -1]).sum()}
        s = max(brak, key=brak.get)
        if s == 'g': y0 += 1
        elif s == 'd': y1 -= 1
        elif s == 'l': x0 += 1
        else: x1 -= 1


def tony(a, cienie=0.35, kontrast=1.05, zolty=0.0, wb=None):
    """Krzywa cieni + kontrast na L (LAB); zolty>0 zbija zolty zafarb w jasnych partiach; wb=(r,g,b) mnozniki."""
    a = a.astype(np.float32)
    if wb is not None:
        a = a * np.array(wb, np.float32)[None, None]
    a = np.clip(a, 0, 255).astype(np.uint8)
    lab = cv2.cvtColor(a, cv2.COLOR_RGB2LAB).astype(np.float32)
    L = lab[..., 0] / 255.
    if zolty:
        lab[..., 2] = 128 + (lab[..., 2] - 128) * (1 - zolty * L)
    x = np.linspace(0, 1, 256); y = x + cienie * x * (1 - x) ** 2; y = 0.5 + (y - 0.5) * kontrast
    lab[..., 0] = cv2.LUT(lab[..., 0].astype(np.uint8), np.clip(y * 255, 0, 255).astype(np.uint8)).astype(np.float32)
    return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)


def wb_szary(a, box, sila=0.6):
    """Mnozniki balansu bieli z obszaru, ktory powinien byc neutralny (sila 0..1)."""
    x0, y0, x1, y1 = box
    m = a[y0:y1, x0:x1].reshape(-1, 3).astype(float).mean(0)
    g = m.mean(); mult = g / m
    return tuple(1 + (mult - 1) * sila)


def rozmyj(a, boxy, r=None):
    a = a.copy()
    for x0, y0, x1, y1 in boxy:
        x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(a.shape[1], x1), min(a.shape[0], y1)
        rr = r or max(9, (x1 - x0) // 12)
        pad = rr * 3
        X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(a.shape[1], x1 + pad), min(a.shape[0], y1 + pad)
        cut = a[Y0:Y1, X0:X1]
        bl = cv2.GaussianBlur(cut, (0, 0), rr)
        m = np.zeros(cut.shape[:2], np.float32); m[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = 1
        m = cv2.GaussianBlur(m, (0, 0), max(3, rr / 2))[..., None]
        a[Y0:Y1, X0:X1] = (bl * m + cut * (1 - m)).astype(np.uint8)
    return a


def wyostrz(a, r=2.0, p=45):
    return Image.fromarray(a).filter(ImageFilter.UnsharpMask(radius=r, percent=p, threshold=3))
