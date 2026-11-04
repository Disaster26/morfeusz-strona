import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = r'C:/Windows/Fonts/bahnschrift.ttf'


def tablica(a, quad, tekst='MORFEUSZ', wariant=b'SemiBold Condensed', wys=0.70, marg=0.05, rozmycie=0.7):
    """a: RGB uint8 (modyfikowane w miejscu). quad: 4 rogi bialego pola znakow (TL,TR,BR,BL) w px zdjecia."""
    q = np.float32(quad)
    W = int(round(max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3]))))
    H = int(round(max(np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1]))))
    dst = np.float32([[0, 0], [W, 0], [W, H], [0, H]])
    M = cv2.getPerspectiveTransform(q, dst)
    flat = cv2.warpPerspective(a, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    g = cv2.cvtColor(flat, cv2.COLOR_RGB2GRAY).astype(np.float32)
    jasne = g > np.percentile(g, 55)
    ciemne = g < np.percentile(g, 12)
    kol_txt = np.median(flat[ciemne], axis=0)
    # tlo: gladka powierzchnia z jasnych pikseli (wielomian 2 st. po x,y na kazdy kanal)
    ys, xs = np.nonzero(jasne)
    X = np.stack([np.ones_like(xs), xs / W, ys / H, (xs / W) ** 2, (ys / H) ** 2, xs * ys / (W * H)], 1).astype(np.float64)
    yy, xx = np.mgrid[0:H, 0:W]
    XA = np.stack([np.ones(H * W), xx.ravel() / W, yy.ravel() / H, (xx.ravel() / W) ** 2, (yy.ravel() / H) ** 2,
                   xx.ravel() * yy.ravel() / (W * H)], 1)
    tlo = np.zeros_like(flat, dtype=np.float32)
    for c in range(3):
        wsp, *_ = np.linalg.lstsq(X, flat[ys, xs, c].astype(np.float64), rcond=None)
        tlo[..., c] = (XA @ wsp).reshape(H, W)
    szum = flat[jasne].astype(np.float32).std(axis=0).mean() * 0.35
    rng = np.random.default_rng(7)
    tlo += rng.normal(0, szum, (H, W, 1)).astype(np.float32)
    # tekst renderowany 4x i zmniejszany
    S = 4
    f = ImageFont.truetype(FONT, 100)
    f.set_variation_by_name(wariant)
    mask = Image.new('L', (W * S, H * S), 0)
    d = ImageDraw.Draw(mask)
    bb = d.textbbox((0, 0), tekst, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    tmp = Image.new('L', (tw + 4, th + 4), 0)
    ImageDraw.Draw(tmp).text((2 - bb[0], 2 - bb[1]), tekst, font=f, fill=255)
    cel_h = H * S * wys
    cel_w = W * S * (1 - 2 * marg)
    tmp = tmp.resize((int(cel_w), int(cel_h)), Image.LANCZOS)
    mask.paste(tmp, (int((W * S - cel_w) / 2), int((H * S - cel_h) / 2)))
    mask = mask.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(rozmycie))
    m = np.asarray(mask, np.float32)[..., None] / 255
    nowa = tlo * (1 - m) + kol_txt[None, None, :] * m
    nowa = np.clip(nowa, 0, 255).astype(np.uint8)
    # z powrotem w perspektywie, maska wpasowania z miekka krawedzia (1 px)
    Mi = cv2.getPerspectiveTransform(dst, q)
    H0, W0 = a.shape[:2]
    x0, y0 = int(q[:, 0].min()) - 4, int(q[:, 1].min()) - 4
    x1, y1 = int(q[:, 0].max()) + 5, int(q[:, 1].max()) + 5
    T = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]], np.float64) @ Mi
    war = cv2.warpPerspective(nowa, T, (x1 - x0, y1 - y0), flags=cv2.INTER_CUBIC)
    ok = np.zeros((H, W), np.uint8); ok[1:-1, 1:-1] = 255
    wm = cv2.warpPerspective(ok, T, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR)
    wm = cv2.GaussianBlur(wm, (3, 3), 0).astype(np.float32)[..., None] / 255
    reg = a[y0:y1, x0:x1].astype(np.float32)
    a[y0:y1, x0:x1] = np.clip(reg * (1 - wm) + war * wm, 0, 255).astype(np.uint8)
    return a
