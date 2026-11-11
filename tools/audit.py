import pdfplumber, json, collections, re
pdf=pdfplumber.open('/mnt/user-data/uploads/Boomi_Associate_Integration_Developer_Ravi_Raya_COMPLETE_1.pdf')
chs=json.load(open('/tmp/w/src/data__chapters.json')); acts=json.load(open('/tmp/w/src/data__activities.json'))
owner={}
for c in chs:
    for n in range(c['pdfPages'][0],c['pdfPages'][1]+1): owner[n]=c['id']
for a in acts:
    for n in range(a['pdfPages'][0],a['pdfPages'][1]+1): owner[n]=a['id']
old=json.load(open('/tmp/w/Boomi_Academy_CHECKPOINT_01/diagram_inventory.json'))
oldpages=set()
def collect(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k in('page','pdfPage') and isinstance(v,int): oldpages.add(v)
            collect(v)
    elif isinstance(o,list):
        for x in o: collect(x)
collect(old)
rows=[]
for i,p in enumerate(pdf.pages,1):
    rects=p.rects; lines=p.lines; curves=p.curves; imgs=p.images
    def area(r): return abs((r['x1']-r['x0'])*(r['bottom']-r['top']))
    pa=p.width*p.height
    fills=set(str(r.get('non_stroking_color')) for r in rects if r.get('fill'))
    big=[r for r in rects if area(r)>pa*0.01 and area(r)<pa*0.9]
    imgarea=sum(abs((im['x1']-im['x0'])*(im['bottom']-im['top'])) for im in imgs)/pa
    txt=p.extract_text() or ''
    # text boxes inside rects: node-like
    nodes=[r for r in rects if 25<(r['x1']-r['x0'])<300 and 14<(r['bottom']-r['top'])<160 and r.get('stroke') ]
    conn=len(lines)+len(curves)
    tables=len(p.find_tables())
    rows.append(dict(page=i,owner=owner.get(i),chars=len(p.chars),words=len(txt.split()),rects=len(rects),bigRects=len(big),lines=len(lines),curves=len(curves),images=len(imgs),imgCover=round(imgarea,2),fills=len(fills),nodeRects=len(nodes),tables=tables,inOldInventory=i in oldpages,head=txt.split('\n')[0][:70] if txt else ''))
json.dump(rows,open('/tmp/w/page_stats.json','w'))
print(len(rows),'old inventory pages',sorted(oldpages))
c=collections.Counter()
for r in rows:
    k='img' if r['imgCover']>0.15 else ('vec' if (r['nodeRects']>=4 and r['lines']+r['curves']>=3) else 'text')
    c[k]+=1
print(c)
