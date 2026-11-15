import json, re, sys
L=[json.loads(l) for l in open(sys.argv[2])]
G=json.load(open(sys.argv[1]))['games']; G=[g for g in G if not g.get('community')]
ids={g['id'] for g in G}
# keyword aliases
alias={}
for g in G:
    n=re.sub(r'[®™:]','',g['name']).lower()
    alias[g['id']]=[n]
extra={'01007EF00011E000':['breath of the wild','botw','旷野','荒野'],'0100F2C0115B6000':['tears of the kingdom','totk','王国之泪','王泪'],
'0100000000010000':['odyssey','奥德赛'],'01006F8002326000':['animal crossing','动森'],'0100FD8022DAA000':['galaxy 2','银河2'],
'010099C022B96000':['super mario galaxy','银河'],'0100F43008C44000':['pokemon za','legends z-a','pokémon za','pokemon legends za','pokemon z-a'],
'0100152000022000':['mario kart 8','mk8','马车8'],'0400C3F00006E000':['mario kart world','马车世界'],'0400486024DEC000':['ocarina','时之笛'],
'040074A01BF12000':['bananza'],'010015100B514000':['wonder','惊奇'],'0100ECD018EBE000':['thousand-year','ttyd','千年之门'],
'01008CF01BAAC000':['echoes of wisdom','智慧的再现'],'010028600EBDA000':['3d world','bowser'],'0100965017338000':['jamboree'],
'01004D300C5AE000':['forgotten land','星之卡比'],'0100C1F0051B6000':['tropical freeze'],'01009D901BC56000':['country returns'],
'0100B7C00933A000':['pikmin 4','皮克敏'],'010049900F546000':['3d all-stars','3d all stars'],'0100A00019DE0000':['hades ii','hades 2'],
'01006FE013472000':['mario party superstars'],'01007A3009184000':['princess peach','showtime'],'010067300059A000':['kingdom battle']}
for k,v in extra.items():
    if k in alias: alias[k]+=v
out={}
for x in L:
    txt=(x['title']+' '+(x['body'] or '')).lower()
    labs=[l.split(': ')[1] for l in x['labels'] if l.startswith('game: ')]
    hit=set(i for i in labs if i[:14]+'00' in ids or i in ids)
    hit|={i for i in ids if i.lower() in x['title'].lower()}
    if not hit:
        t=x['title'].lower()
        hit={i for i,a in alias.items() if any(len(s)>3 and s in t for s in a)}
    x['games']=sorted(hit)
    for h in hit: out.setdefault(h[:13]+'000' if h[:13]+'000' in ids else h,[]).append(x)
json.dump(L,open(sys.argv[3],'w'),ensure_ascii=False)
names={g['id']:g['name'] for g in G}
for gid,xs in sorted(out.items(),key=lambda k:names.get(k[0],k[0])):
    print('\n##',names.get(gid,gid),gid)
    for x in sorted(xs,key=lambda x:x['number']): print(' ',x['number'],x['state'][0],'|',x['title'][:120])
um=[x for x in L if not x['games']]
print('\n## UNMATCHED',len(um))
