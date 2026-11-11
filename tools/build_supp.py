import json,re,pdfplumber
raw=json.load(open('/tmp/w/supp_raw.json'))
pdf=pdfplumber.open('/mnt/user-data/uploads/Boomi_Associate_Integration_Developer_Ravi_Raya_COMPLETE_1.pdf')
def uris(n):
    out=[]
    for h in pdf.pages[n-1].hyperlinks:
        if not out or out[-1]!=h['uri']: out.append(h['uri'])
    return out
LABELS=('Memory cue:','Scenario:','Model approach:','Concept to remember:','Exam-information caution:','Scope discipline:','Important:','Example:','Safety:','Scoring:','Suggested readiness gate','EDITORIAL NOTE','FINAL TIP','Current official','Do not treat')
def callout(t):
    for l in LABELS:
        if t.startswith(l): return True
    return False
out={}
for lid,pgs in raw.items():
    secs=[];first_h1=True;lastb=None
    for pg in pgs:
        n=pg['page']
        for b in pg['blocks']:
            t=b.get('text','')
            t=t.replace('(cid:127)','•').strip()
            ty=b['type']
            if ty=='table':
                rows=b['rows']
                if len(rows)==1 and len(rows[0])==1: continue   # footer/cover frames
                secs.append(dict(t='table',head=rows[0],rows=rows[1:],page=n)); continue
            if re.match(r'^(Appendix A: Source Discrepancies and Editorial Notes TIBCO BW 5\.x to Boomi)$',t): continue
            if ty=='h1':
                if secs and secs[-1]['t'] in('h1','h2') and secs[-1].get('_cont') is None and secs[-1]['t']=='h1' and b['top']-lastb<40 and secs[-1]['page']==n:
                    secs[-1]['text']+=' '+t; lastb=b['top']; continue
                secs.append(dict(t='h1' if first_h1 else 'h2',text=t,page=n)); first_h1=False; lastb=b['top']; continue
            if ty=='h2': secs.append(dict(t='h2',text=t,page=n)); continue
            if ty=='h3': secs.append(dict(t='h3',text=t,page=n)); continue
            if ty=='bullet': secs.append(dict(t='li',text=t,page=n)); continue
            if t.startswith('•'): secs.append(dict(t='li',text=t.lstrip('• ').strip(),page=n)); continue
            secs.append(dict(t='callout' if callout(t) else 'p',text=t,page=n))
    out[lid]=secs
# ---- targeted repairs
# appA cover + bullets split
a=out['appA']
a[:0]=[dict(t='h1',text='Appendix A: Source Discrepancies and Editorial Notes',page=150),
       dict(t='p',text='Where the three source PDFs differ, flagged instead of guessed.',page=150)]
# the 'In this chapter you will learn' -> h2
for s in a:
    if s.get('text')=='In this chapter you will learn': s['t']='h2'
i0=next(i for i,s in enumerate(a) if s['page']==151 and s['t']=='p');a.insert(i0,dict(t='h2',text='Source discrepancy log',page=151))
# appA p152 checklist: rebuild from clean text
p152=pdf.pages[151].extract_text().split('\n')
chk=[];cur=None
for ln in p152:
    if ln.startswith('•') or ln.startswith('(cid'):
        cur=ln.replace('(cid:127)','•').lstrip('• ').strip(); chk.append(cur)
    elif cur is not None and ln.startswith('   ')==False and not ln.startswith(('FINAL','Build','worth','End','Appendix')) and chk and ln.strip() and not ln.startswith('Boomi'):
        pass
text152=pdf.pages[151].extract_text().replace('(cid:127)','•')
items=re.findall(r'•\s*(.*?)(?=\n•|\nFINAL TIP)',text152,re.S)
items=[re.sub(r'\s+',' ',i).strip() for i in items]
a[:]=[s for s in a if not (s['page']==152 and s['t'] in('li','p','callout') and 'FINAL TIP' not in s['text'] and 'End of book' not in s['text'])]
idx=next(i for i,s in enumerate(a) if s['t']=='h2' and s['text'].startswith('Revision checklist'))
a[idx+1:idx+1]=[dict(t='li',text=i,page=152,check=True) for i in items]
# editorial note callout / final tip
for s in a:
    if s['text'].startswith('EDITORIAL NOTE') if 'text' in s else False: s['t']='callout'
# cert01 / cert11 source links
for lid,pg in (('cert01',154),('cert16',176)):
    u=uris(pg);k=0
    for s in out[lid]:
        if s['t']=='li' and k<len(u) and (s['page']==pg) and ('http' in s['text'] or 'Open official resource' in s['text']):
            label=s['text'].split(':')[0].strip(); s['text']=label; s['url']=u[k]; k+=1
# cert10 sub-headings & code
c=out['cert10']
for s in c:
    if s['t']=='p' and s['text'] in('Input example','Expected target example','Build steps','Acceptance criteria'): s['t']='h3'
    if s['t']=='p' and s['text'].startswith('SKU-1001,'):
        s['t']='code'; s['text']=re.sub(r' (?=SKU-\d)','\n',s['text'])
    if s['t']=='p' and s['text'].startswith('{"sku"'): s['t']='code'
# mark ordered steps lists
def mark_steps(lid,after):
    on=False
    for s in out[lid]:
        if s['t'] in('h2','h3'): on = s['text'].startswith(after)
        elif s['t']=='li' and on: s['step']=True
mark_steps('cert03','Document lifecycle');mark_steps('cert04','Map build sequence');mark_steps('cert07','Troubleshooting sequence');mark_steps('cert08','Release checklist');mark_steps('cert10','Build steps')
for s in out['cert11']:
    if s['t']=='li': s['memory']=True
# cert13: MCQs from clean text of pages 167-172
qs=[]
txt='\n'.join(pdf.pages[n-1].extract_text() for n in range(168,173))
txt=re.sub(r'\nBoomi Associate Integration Developer.*?(?=\n|$)','',txt)
parts=re.split(r'\n?(?=Q\d+\. )',txt)
for p in parts:
    m=re.match(r'Q(\d+)\. (.*?)\nA\. (.*?)Correct answer: ([A-D])\. (.*)',p,re.S)
    if not m: 
        continue
    num,q,opts,ans,exp=m.groups()
    opts=re.sub(r'\s+',' ',opts).strip()
    sp=re.split(r'(?:(?<=\s)|^)(?=[B-D]\. )',opts)
    o=['A. '+sp[0].strip()]+[x.strip() for x in sp[1:]]
    qs.append(dict(n=int(num),q=re.sub(r'\s+',' ',q).strip(),o=[re.sub(r'^[A-D]\.\s*','',x) for x in o],a='ABCD'.index(ans),e=re.sub(r'\s+',' ',exp).strip()))
print('mcq',len(qs),[len(q['o']) for q in qs if len(q['o'])!=4])
intro=[s for s in out['cert13'] if s['page']==167]
out['cert13']=intro+[dict(t='mcq',items=qs,page=168)]
# cert14 scenarios: group
sc=[];cur=None
for s in out['cert14']:
    if s['t']=='h1': continue
    if s['t']=='h3': cur=dict(title=s['text'],model='',concept='');sc.append(cur)
    elif cur is not None:
        t=s['text']
        if t.startswith('Concept to remember:'): cur['concept']=t[len('Concept to remember:'):].strip(); cur['_c']=True
        elif t.startswith('Model approach:'): cur['model']=t[len('Model approach:'):].strip()
        elif cur.get('_c'): cur['concept']+=' '+t
        else: cur['model']+=' '+t
for c2 in sc: c2.pop('_c',None)
print('scenarios',len(sc),[ (c2['title'][:30],len(c2['model']),len(c2['concept'])) for c2 in sc][-2:])
out['cert14']=[dict(t='h1',text='13. Scenario-based practical examination',page=173),dict(t='scenarios',items=sc,page=173)]
# cert15 scorecard
for s in out['cert15']:
    if s['t']=='table': s['t']='scorecard'
    if s['t']=='li': s['check']=True
json.dump(out,open('/tmp/w/supp.json','w'),ensure_ascii=False)
for k,v in out.items(): print(k,len(v),collections:=None) if False else print(k,len(v),sorted(set(x['t'] for x in v)))
