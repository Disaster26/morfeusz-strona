from PIL import Image, ImageOps, ImageFilter
import os, json, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
SRC=r"C:\Users\Admin\Downloads\Odrobimy_kampania\klienci\Morfeusz\zdjecia_klienta"
KON=r"C:\Users\Admin\Downloads\Morfeusz_koncept\img"
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","img")
os.makedirs(OUT,exist_ok=True)
info={}
def blur(im,prevw,boxes,r=None):
    s=im.width/prevw
    for b in boxes:
        bb=tuple(int(v*s) for v in b)
        rr=r or max(6,int((bb[2]-bb[0])/30))
        bl=im.filter(ImageFilter.GaussianBlur(rr)) if False else im.crop((max(0,bb[0]-60),max(0,bb[1]-60),min(im.width,bb[2]+60),min(im.height,bb[3]+60)))
        ox,oy=max(0,bb[0]-60),max(0,bb[1]-60)
        blr=bl.filter(ImageFilter.GaussianBlur(rr))
        m=Image.new('L',bl.size,0); from PIL import ImageDraw
        ImageDraw.Draw(m).rectangle((bb[0]-ox,bb[1]-oy,bb[2]-ox,bb[3]-oy),fill=255)
        m=m.filter(ImageFilter.GaussianBlur(25))
        im.paste(Image.composite(blr,bl,m),(ox,oy))
    return im
# 04.11b: metadane obrazow - autor i opis (EXIF ASCII bez polskich znakow + XMP w UTF-8), bez GPS i danych aparatu
AUTOR='Zakład Pogrzebowy MORFEUSZ, Wrzosowa'
OPIS={
 'namiot-cmentarz':'Namiot Zakładu Pogrzebowego MORFEUSZ w alei cmentarza, okolice Częstochowy',
 'oprawa-kaplica':'Kaplica zakładu MORFEUSZ we Wrzosowej z trumną i wiązanką przed ceremonią',
 'kaplica':'Kaplica przy Zakładzie Pogrzebowym MORFEUSZ we Wrzosowej',
 'chlodnia':'Własna chłodnia Zakładu Pogrzebowego MORFEUSZ we Wrzosowej',
 'stojak-urna':'Stojak na urnę ze świecami przygotowany przez zakład MORFEUSZ',
 'grob-bez-drabiny':'Grób przygotowany do pochówku z namiotem zakładu MORFEUSZ',
 'pogrzeb-urnowy':'Przygotowanie do pogrzebu urnowego - Zakład Pogrzebowy MORFEUSZ',
 'ceremonia-kosciol':'Oprawa ceremonii pogrzebowej w kościele - Zakład Pogrzebowy MORFEUSZ',
 'urny-zaklad-wrzosowa':'Urny w Zakładzie Pogrzebowym MORFEUSZ we Wrzosowej',
 'karawany-morfeusz':'Trzy karawany Zakładu Pogrzebowego MORFEUSZ przed kościołem',
 'biuro':'Biuro obsługi klienta Zakładu Pogrzebowego MORFEUSZ we Wrzosowej',
 'urny':'Urny w Zakładzie Pogrzebowym MORFEUSZ',
 'karawan':'Karawan Zakładu Pogrzebowego MORFEUSZ',
 'siedziba':'Siedziba Zakładu Pogrzebowego MORFEUSZ, ul. Górna 30, Wrzosowa',
 'wieniec':'Wieniec pogrzebowy - Zakład Pogrzebowy MORFEUSZ',
 'urna-grob':'Urna z wiązanką róż przy grobie - Zakład Pogrzebowy MORFEUSZ',
 'namiot-zima':'Namiot zakładu MORFEUSZ przy pogrzebie urnowym zimą',
 'namiot-zima-2':'Namiot zakładu MORFEUSZ na cmentarzu zimą',
}
import unicodedata
from xml.sax.saxutils import escape as xesc
def _ascii(t): return unicodedata.normalize('NFKD',t.replace('ł','l').replace('Ł','L')).encode('ascii','ignore').decode()
def metadane(name):
    opis=OPIS.get(name,'Zakład Pogrzebowy MORFEUSZ, Wrzosowa')
    ex=Image.Exif(); ex[0x013B]=_ascii(AUTOR); ex[0x010E]=_ascii(opis); ex[0x8298]=_ascii('(c) '+AUTOR)
    xmp=('<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
         '<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">'
         f'<dc:creator><rdf:Seq><rdf:li>{xesc(AUTOR)}</rdf:li></rdf:Seq></dc:creator>'
         f'<dc:description><rdf:Alt><rdf:li xml:lang="x-default">{xesc(opis)}</rdf:li></rdf:Alt></dc:description>'
         f'<dc:rights><rdf:Alt><rdf:li xml:lang="x-default">© {xesc(AUTOR)}</rdf:li></rdf:Alt></dc:rights>'
         '</rdf:Description></rdf:RDF></x:xmpmeta>').encode('utf-8')
    return ex.tobytes(),xmp
def zapisz(im,name,widths,q=70):
    im=im.convert('RGB'); out=[]; exif,xmp=metadane(name)
    for w in widths:
        if w>im.width: w=im.width
        h=round(im.height*w/im.width)
        r=im.resize((w,h),Image.LANCZOS)
        fn=f"{name}-{w}.webp"; r.save(os.path.join(OUT,fn),'WEBP',quality=q,method=6,exif=exif,xmp=xmp)  # tylko autor/opis, bez GPS/aparatu/ICC
        out.append((fn,w,h))
    info[name]=out; print(name,[(o[0],os.path.getsize(os.path.join(OUT,o[0]))//1024) for o in out])
def otworz(f): return ImageOps.exif_transpose(Image.open(os.path.join(SRC,f))).convert('RGB')
# klienta
im=otworz('20220826_132505.jpg'); blur(im,1000,[(78,385,195,500),(885,365,1000,495),(335,377,428,418)])
zapisz(im,'namiot-cmentarz',[480,800,1200,1600,1920],q=62)
# 04.11: klient chce szerszy kadr kaplicy z trumna i wiazanka (wczesniej tylko krzyz i napis) - prawie cale zdjecie
im=otworz('20160226_104409.jpg'); s=im.width/562; im=im.crop((0,int(30*s),im.width,int(990*s)))
zapisz(im,'oprawa-kaplica',[480,800,1200],q=62)
im=otworz('20230621_132132.jpg'); zapisz(im,'kaplica',[480,800,1200])
im=otworz('20151015_164556.jpg'); zapisz(im,'chlodnia',[480,800,1200])
im=otworz('20220826_132521.jpg'); zapisz(im,'stojak-urna',[480,800,1200],q=60)
# 04.11: kadr bez drabiny (drabina po prawej od x~580/750) i bez napisow na wstegach wiencow po lewej
im=otworz('20230425_132437.jpg'); k=im.width/750; im=im.crop((int(160*k),int(190*k),int(578*k),int(860*k))); zapisz(im,'grob-bez-drabiny',[480,800,1200],q=60)
im=otworz('IMG_20180720_152351.jpg'); blur(im,750,[(105,135,175,190),(285,130,345,175)],r=14); zapisz(im,'pogrzeb-urnowy',[480,800,1200],q=60)
# 28.10: zgoda klienta na zdjecie z kosciola bez portretu i tabliczki z nazwiskiem - kadr bez sztalugi i bez tabliczki
im=otworz('20250109_101525.jpg'); k=im.width/900; im=im.crop((int(232*k),0,im.width,int(765*k))); zapisz(im,'ceremonia-kosciol',[480,800,1200],q=62)
# 04.11: zdjecia ze starej strony (oryginaly w pelnej rozdzielczosci)
STARA=r"C:\Users\Admin\Downloads\Morfeusz_kopia_starej_strony_20261102_1340\wp-content\uploads"
ORIG=r"C:\Users\Admin\Downloads\Morfeusz_koncept\_src\orig"
# regal z urnami (ok. 20 szt.), tabliczki z nazwiskami rozmyte
im=ImageOps.exif_transpose(Image.open(os.path.join(STARA,'2016','03','20150915_233720.jpg'))).convert('RGB')
# 04.11b: user - bez dolnego pasa (tabliczki, znak zakazu palenia, grzejnik): obrot -1.6 st. (polka pozioma) i kadr tuz pod druga polka
im=im.rotate(-1.6,resample=Image.BICUBIC)
blur(im,1000,[(858,350,1000,478)],r=38)  # tabliczka za urna-sercem po prawej
k=im.width/1000; im=im.crop((int(20*k),int(40*k),int(940*k),int(546*k))); zapisz(im,'urny-zaklad-wrzosowa',[480,800,1200],q=62)
# trzy karawany przed kosciolem: znak wodny aparatu usuniety (inpaint), osoby w szybie i w tle rozmyte
import numpy as np, cv2
im=ImageOps.exif_transpose(Image.open(os.path.join(ORIG,'20240611_1341351.jpg'))).convert('RGB')
a=np.asarray(im).copy(); k=im.width/1000; maska=np.zeros(a.shape[:2],np.uint8)
for bx,v,sat in [((45,590,375,700),228,30),((50,594,145,628),175,45),((50,660,290,692),200,40)]:
    X0,Y0,X1,Y1=[int(c*k) for c in bx]; h=cv2.cvtColor(a[Y0:Y1,X0:X1],cv2.COLOR_RGB2HSV)
    maska[Y0:Y1,X0:X1]|=cv2.dilate(((h[...,2]>v)&(h[...,1]<sat)).astype(np.uint8)*255,np.ones((5,5),np.uint8),iterations=2)
a=cv2.inpaint(a,maska,9,cv2.INPAINT_TELEA)
# 04.11b: na tablicach rejestracyjnych napis MORFEUSZ (bialy podklad, perspektywa, niebieski pasek PL zostaje oryginalny)
from tablice import tablica
for (ox,oy),s_,qq in [((560,2070),1.923,[(184,104),(882,94),(882,233),(184,255)]),
                      ((2660,1920),2.857,[(216,122),(866,110),(866,260),(216,272)]),
                      ((3890,1880),3.333,[(220,160),(824,150),(824,304),(220,318)])]:
    tablica(a,[(ox+x/s_,oy+y/s_) for x,y in qq],wariant=b'Condensed',wys=0.74,rozmycie=0.8 if s_<2 else 1.1)
im=Image.fromarray(a)
blur(im,1000,[(120,295,285,358),(28,283,78,342),(858,300,902,336)],r=30)
im=im.crop((0,0,int(960*k),int(735*k))); zapisz(im,'karawany-morfeusz',[480,800,1200],q=62)
# z archiwum (wizualizacja, juz rozmyte)
for f,n in [('biuro','biuro'),('urny','urny'),('karawan','karawan'),('siedziba','siedziba'),('wieniec','wieniec'),('urna-grob','urna-grob'),('namiot','namiot-zima'),('hero-pion','namiot-zima-2')]:
    im=Image.open(os.path.join(KON,f+'.webp')); zapisz(im,n,[480,im.width] if im.width>560 else [im.width])
json.dump(info,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"zdjecia.json"),"w"),indent=1)
