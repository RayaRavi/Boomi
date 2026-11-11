import pdfplumber, collections, json, re
PDF='/mnt/user-data/uploads/Boomi_Associate_Integration_Developer_Ravi_Raya_COMPLETE_1.pdf'
pdf=pdfplumber.open(PDF)
chs=json.load(open('/tmp/w/src/data__chapters.json'))
spans={c['id']:c['pdfPages'] for c in chs if c['id']=='appA' or c['id'].startswith('cert')}
def clean(t): return re.sub(r'\s+',' ',t or '').strip()
def page_blocks(n):
    p=pdf.pages[n-1]
    tbs=p.find_tables()
    boxes=[t.bbox for t in tbs]
    blocks=[]
    for t in tbs:
        rows=[[clean(c) for c in r] for r in t.extract()]
        rows=[r for r in rows if any(r)]
        blocks.append(dict(top=t.bbox[1],type='table',rows=rows))
    ws=p.extract_words(extra_attrs=['fontname','size'])
    def inbox(w):
        return any(b[0]-2<=w['x0'] and w['x1']<=b[2]+2 and b[1]-2<=w['top'] and w['bottom']<=b[3]+2 for b in boxes)
    ws=[w for w in ws if not inbox(w) and w['top']<805]
    rows=collections.defaultdict(list)
    for w in ws: rows[round(w['top']/3)].append(w)
    lines=[]
    for k in sorted(rows):
        r=sorted(rows[k],key=lambda w:w['x0'])
        sz=collections.Counter(round(w['size'],1) for w in r).most_common(1)[0][0]
        bold=sum('Bold' in w['fontname'] for w in r)>len(r)/2
        lines.append(dict(top=r[0]['top'],x=r[0]['x0'],size=sz,bold=bold,text=' '.join(w['text'] for w in r)))
    cur=None
    def flush():
        nonlocal cur
        if cur: blocks.append(cur); cur=None
    prev=None
    for l in lines:
        t=l['text']
        if re.search(r'Ravi Raya \| (Supplement )?Page|Boomi Integration Essentials \|',t) and l['size']<7.5: continue
        if l['bold'] and l['size']>=17: flush(); blocks.append(dict(top=l['top'],type='h1',text=t)); prev=None; continue
        if l['bold'] and l['size']>=12.5: flush(); blocks.append(dict(top=l['top'],type='h2',text=t)); prev=None; continue
        if l['bold'] and 8.7<=l['size']<=9.5:
            if cur and cur['type']=='h3' and l['top']-prev<16: cur['text']+=' '+t; prev=l['top']; continue
            flush(); cur=dict(top=l['top'],type='h3',text=t); prev=l['top']; continue
        gap=(l['top']-prev) if prev is not None else 99
        isb=t.startswith('- ') or t.startswith('• ')
        if cur and cur['type']=='h3' and gap<16 and not isb and l['size']<9.5 and not l['bold']:
            flush(); cur=None
        if isb:
            flush(); cur=dict(top=l['top'],type='bullet',text=t[2:].strip())
        elif cur and cur['type'] in('p','bullet') and gap<15.5 and (l['x']<=cur.get('x0',l['x'])+60 or cur['type']=='bullet'):
            cur['text']+=' '+t
        else:
            flush(); cur=dict(top=l['top'],type='p',text=t,x0=l['x'])
        prev=l['top']
    flush()
    blocks.sort(key=lambda b:b['top'])
    for b in blocks: b.pop('x0',None)
    return blocks
out={}
for id_,(a,b) in spans.items():
    out[id_]=[dict(page=n,blocks=page_blocks(n)) for n in range(a,b+1)]
json.dump(out,open('/tmp/w/supp_raw.json','w'),indent=1)
for id_ in ['appA','cert14','cert13']:
    print('#####',id_)
    for pg in out[id_][:2]:
        print('--page',pg['page'])
        for b in pg['blocks']: print(b['type'],'|',(b.get('text') or str(b.get('rows'))[:200])[:140])
