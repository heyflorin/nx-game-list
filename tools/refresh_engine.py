import json,re,glob
t=open('readmes/games-index.md').read().split('## Keys')[0]
idx={}
for l in t.splitlines():
    if not l.startswith('| ['): continue
    r=[c.strip() for c in l.strip().strip('|').split('|')]
    m=re.search(r'`([0-9A-F]{16})`',r[1])
    if m: idx[m.group(1)]={'name':re.sub(r'\[(.*?)\]\(.*?\)',r'\1',r[0]),'build':r[2],'sdk':r[3],'engine':r[4],'gfx':r[5]}
json.dump(idx,open('readmes/index.json','w'),ensure_ascii=False)
out={}
for f in glob.glob('readmes/all/*.md'):
    i=f.split('/')[-1][:-3]
    t=open(f).read(); text=re.sub(r'\s+',' ',re.split(r'\n## ',t)[0])
    st=re.search(r'## Status\s*\n(.*?)(\n## |\Z)',t,re.S)
    if st: text+=' '+re.sub(r'\s+',' ',st.group(1))
    phone=bool(re.search(r'\b(plays|playable|runs|played)\b[^.]{0,60}\b(iPhone|iPad|iOS)\b',text,re.I)) and not re.search(r'(iOS|iPhone)[^.]{0,30}(untested|not tested|not run|unvalidated|remains? untested)',text,re.I)
    mac=bool(re.search(r'(plays|playable|runs|brought up|played)[^.]{0,40}\bMac\b|\bon the Mac\b',text,re.I))
    out[i]={'phone':phone,'mac':mac}
json.dump(out,open('readmes/classify.json','w'))
print(len(idx),'profiles in index;',len(out),'notes')
