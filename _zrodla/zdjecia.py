from PIL import Image, ImageOps, ImageFilter
import os, json
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
def zapisz(im,name,widths,q=70):
    im=im.convert('RGB'); out=[]
    for w in widths:
        if w>im.width: w=im.width
        h=round(im.height*w/im.width)
        r=im.resize((w,h),Image.LANCZOS)
        fn=f"{name}-{w}.webp"; r.save(os.path.join(OUT,fn),'WEBP',quality=q,method=6)  # bez EXIF/ICC
        out.append((fn,w,h))
    info[name]=out; print(name,[(o[0],os.path.getsize(os.path.join(OUT,o[0]))//1024) for o in out])
def otworz(f): return ImageOps.exif_transpose(Image.open(os.path.join(SRC,f))).convert('RGB')
# klienta
im=otworz('20220826_132505.jpg'); blur(im,1000,[(78,385,195,500),(885,365,1000,495),(335,377,428,418)])
zapisz(im,'namiot-cmentarz',[480,800,1200,1600,1920],q=62)
im=otworz('20160226_104409.jpg'); s=im.width/562; im=im.crop((0,0,im.width,int(580*s)))
zapisz(im,'kaplica-ceremonia',[480,800,1200])
im=otworz('20230621_132132.jpg'); zapisz(im,'kaplica',[480,800,1200])
im=otworz('20151015_164556.jpg'); zapisz(im,'chlodnia',[480,800,1200])
im=otworz('20220826_132521.jpg'); zapisz(im,'stojak-urna',[480,800,1200],q=60)
im=otworz('20230425_132437.jpg'); k=im.width/750; im=im.crop((int(235*k),0,im.width,im.height)); zapisz(im,'grob-namiot',[480,800,1200],q=58)
im=otworz('IMG_20180720_152351.jpg'); blur(im,750,[(105,135,175,190),(285,130,345,175)],r=14); zapisz(im,'pogrzeb-urnowy',[480,800,1200],q=60)
# 28.10: zgoda klienta na zdjecie z kosciola bez portretu i tabliczki z nazwiskiem - kadr bez sztalugi i bez tabliczki
im=otworz('20250109_101525.jpg'); k=im.width/900; im=im.crop((int(232*k),0,im.width,int(765*k))); zapisz(im,'ceremonia-kosciol',[480,800,1200],q=62)
# z archiwum (wizualizacja, juz rozmyte)
for f,n in [('biuro','biuro'),('urny','urny'),('karawan','karawan'),('flota','karawany-kosciol'),('siedziba','siedziba'),('wieniec','wieniec'),('urna-grob','urna-grob'),('namiot','namiot-zima'),('hero-pion','namiot-zima-2')]:
    im=Image.open(os.path.join(KON,f+'.webp')); zapisz(im,n,[480,im.width] if im.width>560 else [im.width])
json.dump(info,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"zdjecia.json"),"w"),indent=1)
