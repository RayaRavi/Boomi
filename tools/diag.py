import pdfplumber, json, math, html, subprocess, os
PDF='/mnt/user-data/uploads/Boomi_Associate_Integration_Developer_Ravi_Raya_COMPLETE_1.pdf'
pdf=pdfplumber.open(PDF)
chs=json.load(open('/tmp/w/src/data__chapters.json'))
owner={}
for c in chs:
    for n in range(c['pdfPages'][0],c['pdfPages'][1]+1): owner[n]=c['id']
def col(c):
    if c is None: return None
    if isinstance(c,(int,float)): c=(c,)
    c=tuple(c)
    if len(c)==1: v=int(round(c[0]*255)); return f'rgb({v},{v},{v})'
    if len(c)==3: return 'rgb(%d,%d,%d)'%tuple(int(round(x*255)) for x in c)
    if len(c)==4:
        k=c[3]; return 'rgb(%d,%d,%d)'%tuple(int(round(255*(1-x)*(1-k))) for x in c[:3])
    return None
def cand_boxes(p):
    out=[]
    for c in p.curves:
        w=c['x1']-c['x0'];h=c['bottom']-c['top']
        if len(c['pts'])>=8 and w>=40 and h>=16 and c.get('fill'): out.append((c['x0'],c['top'],c['x1'],c['bottom']))
    for r in p.rects:
        w=r['x1']-r['x0'];h=r['bottom']-r['top']
        if 40<=w<=200 and 16<=h<=90 and r.get('fill') and r['top']>40 and r['bottom']<800: out.append((r['x0'],r['top'],r['x1'],r['bottom']))
    return out
def regions(p,page):
    if 142<=page<=149: return [(6,22,p.width-6,816)]
    bs=sorted(cand_boxes(p),key=lambda b:b[1]); cl=[]
    for b in bs:
        if cl and b[1]<=cl[-1][3]+18: cl[-1]=[min(cl[-1][0],b[0]),min(cl[-1][1],b[1]),max(cl[-1][2],b[2]),max(cl[-1][3],b[3]),cl[-1][4]+1]
        else: cl.append([b[0],b[1],b[2],b[3],1])
    return [(max(0,a-10),max(0,b-10),min(p.width,c+10),min(p.height,d+10)) for a,b,c,d,n in cl if n>=3]
def inreg(o,R,pad=1):
    return o['x0']>=R[0]-pad and o['x1']<=R[2]+pad and o['top']>=R[1]-pad and o['bottom']<=R[3]+pad
def build(page,R,k):
    p=pdf.pages[page-1]; X0,Y0,X1,Y1=R; W=X1-X0;H=Y1-Y0
    P=[]; X=lambda x:round(x-X0,1); Y=lambda y:round(y-Y0,1)
    P.append(f'<rect x="0" y="0" width="{W:.1f}" height="{H:.1f}" fill="#fff"/>')
    for r in p.rects:
        if (r['x0']<R[2] and r['x1']>R[0] and r['top']<R[3] and r['bottom']>R[1]):
            f=col(r.get('non_stroking_color')) if r.get('fill') else 'none'; s=col(r.get('stroking_color')) if r.get('stroke') else 'none'
            P.append(f'<rect x="{X(r["x0"])}" y="{Y(r["top"])}" width="{r["x1"]-r["x0"]:.1f}" height="{r["bottom"]-r["top"]:.1f}" fill="{f}" stroke="{s}" stroke-width="{r.get("linewidth") or 0.6}"/>')
    arrows=[];paths=[]
    for c in p.curves:
        if not (c['x0']<R[2] and c['x1']>R[0] and c['top']<R[3] and c['bottom']>R[1]): continue
        pts=c['pts']
        def seg(sg):
            k=sg[0]
            if k=='m': return f'M{X(sg[1][0])},{Y(sg[1][1])}'
            if k=='l': return f'L{X(sg[1][0])},{Y(sg[1][1])}'
            if k=='c': return 'C'+' '.join(f'{X(q[0])},{Y(q[1])}' for q in sg[1:4])
            if k=='h': return 'Z'
            return ''
        d=' '.join(seg(sg) for sg in c['path']) if c.get('path') else 'M'+' L'.join(f'{X(x)},{Y(y)}' for x,y in pts)
        w=c['x1']-c['x0'];h=c['bottom']-c['top']
        if c.get('fill') and len(pts)<=5 and w<14 and h<14: arrows.append(c['pts'][:3])
        f=col(c.get('non_stroking_color')) if c.get('fill') else 'none'; s=col(c.get('stroking_color')) if c.get('stroke') else 'none'
        if not c.get('fill') and len(pts)>=2: paths.append(pts)
        P.append(f'<path d="{d}" fill="{f}" stroke="{s}" stroke-width="{c.get("linewidth") or 0.6}" stroke-linejoin="round"/>')
    lines=[]
    for l in p.lines:
        if not inreg(l,R,1.5): continue
        s=col(l.get('stroking_color')) or '#888'; P.append(f'<line x1="{X(l["x0"])}" y1="{Y(l["top"] if l["pts"][0][1]<=l["pts"][-1][1] else l["bottom"])}" x2="{X(l["x1"])}" y2="{Y(l["bottom"] if l["pts"][0][1]<=l["pts"][-1][1] else l["top"])}" stroke="{s}" stroke-width="{l.get("linewidth") or 0.6}"/>')
        lines.append([(l['pts'][0][0],l['pts'][0][1]),(l['pts'][-1][0],l['pts'][-1][1])])
    words=[w for w in p.extract_words(extra_attrs=['fontname','size','non_stroking_color'],keep_blank_chars=False,use_text_flow=False) if inreg(w,R)]
    for w in words:
        b='bold' if 'Bold' in w['fontname'] else 'normal'; f=col(w.get('non_stroking_color')) or '#000'
        P.append(f'<text x="{X(w["x0"])}" y="{Y(w["bottom"])-w["size"]*0.22:.1f}" font-size="{w["size"]:.1f}" font-weight="{b}" fill="{f}" textLength="{w["x1"]-w["x0"]:.1f}" lengthAdjust="spacingAndGlyphs" font-family="Helvetica,Arial,sans-serif">{html.escape(w["text"].replace('(cid:127)','•'))}</text>')
    # nodes
    cands=[]
    for b in cand_boxes(p):
        if not (b[0]>=R[0]-1 and b[2]<=R[2]+1 and b[1]>=R[1]-1 and b[3]<=R[3]+1): continue
        ws=[w for w in words if w['x0']>=b[0]-1 and w['x1']<=b[2]+1 and w['top']>=b[1]-1 and w['bottom']<=b[3]+1]
        if 1<=len(ws)<=45: cands.append((b,ws))
    cands.sort(key=lambda t:-(t[0][2]-t[0][0])*(t[0][3]-t[0][1]))
    ch=[]
    for b,ws in cands:
        a=(b[2]-b[0])*(b[3]-b[1])
        if a>0.5*W*H and len(cands)>1: continue
        dup=False
        for c2,_ in ch:
            ix=max(0,min(b[2],c2[2])-max(b[0],c2[0]));iy=max(0,min(b[3],c2[3])-max(b[1],c2[1]))
            if ix*iy>0.5*a: dup=True;break
        if not dup: ch.append((b,ws))
    ch.sort(key=lambda t:(round(t[0][1]/22),t[0][0]))
    nodes=[dict(x=X(b[0]),y=Y(b[1]),w=round(b[2]-b[0],1),h=round(b[3]-b[1],1),text=' '.join(w['text'].replace('(cid:127)','•') for w in sorted(ws,key=lambda w:(round(w['top']/3),w['x0'])))) for b,ws in ch]
    # moving dots
    dots=[]
    for tri in arrows:
        if len(tri)<3: continue
        best=None
        for t in range(3):
            o=[tri[(t+1)%3],tri[(t+2)%3]]; m=((o[0][0]+o[1][0])/2,(o[0][1]+o[1][1])/2); d=math.hypot(tri[t][0]-m[0],tri[t][1]-m[1])
            if best is None or d>best[0]: best=(d,tri[t],m)
        d,tip,m=best
        if d<1: continue
        ux,uy=(tip[0]-m[0])/d,(tip[1]-m[1])/d
        start=None
        for seg in lines+[pp for pp in paths if len(pp)==2]:
            for e,f in ((seg[-1],seg[0]),(seg[0],seg[-1])):
                if math.hypot(e[0]-m[0],e[1]-m[1])<7 and math.hypot(f[0]-e[0],f[1]-e[1])>=8: start=f;break
            if start: break
        if not start: start=(tip[0]-ux*16,tip[1]-uy*16)
        dots.append(f'M{X(start[0])},{Y(start[1])} L{X(tip[0])},{Y(tip[1])}')
    dots=dots[:50]
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" role="img" aria-label="Recreated diagram from PDF page {page}">'+''.join(P)+'<g class="hl"></g><g class="dots">'+''.join(f'<circle r="2.6" fill="#38bdf8" stroke="#fff" stroke-width=".6"><animateMotion dur="{1.4+0.1*(i%5):.1f}s" repeatCount="indefinite" path="{d}"/></circle>' for i,d in enumerate(dots))+'</g></svg>'
    return dict(id=f'dg{page:03d}_{k}',page=page,lesson=owner.get(page),w=round(W,1),h=round(H,1),region=[round(v,1) for v in R],svg=svg,nodes=nodes,arrows=len(arrows),dots=len(dots),words=len(words))
V=[8,10,12,13,38,56,61,75,100,117,119,122]+list(range(142,150))
out=[]
os.makedirs('/tmp/w/diag/crops',exist_ok=True)
for pg in V:
    p=pdf.pages[pg-1]
    for k,R in enumerate(regions(p,pg),1):
        d=build(pg,R,k); out.append(d)
        # crop PNG of original region
        x,y,w,h=[int(v*150/72) for v in (R[0],R[1],R[2]-R[0],R[3]-R[1])]
        subprocess.run(['pdftoppm','-r','150','-f',str(pg),'-l',str(pg),'-x',str(x),'-y',str(y),'-W',str(w),'-H',str(h),'-png','-singlefile',PDF,f'/tmp/w/diag/crops/{d["id"]}'],check=True)
        print(d['id'],d['lesson'],d['w'],d['h'],'nodes',len(d['nodes']),'dots',d['dots'],'svgKB',len(d['svg'])//1024)
json.dump(out,open('/tmp/w/diag/diagrams.json','w'),ensure_ascii=False)
