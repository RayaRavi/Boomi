cd /tmp/w
python3 - <<'P'
s=open('/tmp/w/Boomi_Academy_CHECKPOINT_01/index.html',encoding='utf8').read()
d=open('/tmp/w/supp.json',encoding='utf8').read()
css=open('/tmp/w/build/supp.css').read(); js=open('/tmp/w/build/supp.js').read()
extra=''
import os
if os.path.exists('/tmp/w/build/audit_block.html'): extra=open('/tmp/w/build/audit_block.html',encoding='utf8').read()
inj=f'<style id="supp-style">{css}</style>\n<script id="supp-data">window.__SUPP={d.replace("</","<\\/")};</script>\n<script id="supp-render">{js}</script>\n{extra}'
i=s.rfind('</body>'); open('/tmp/w/build/index.html','w',encoding='utf8').write(s[:i]+inj+s[i:])
P
node --check build/supp.js
