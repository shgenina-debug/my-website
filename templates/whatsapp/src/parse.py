import re, json, sys
md = open(sys.argv[1], encoding='utf-8').read()
sections=[]; cur=None; title=None
lines=md.split('\n'); i=0
while i<len(lines):
    l=lines[i]
    m=re.match(r'^## (.+?)：?\s*$',l)
    if l.startswith('## ') and 'طريقة' not in l:
        name=l[3:].strip()
        name=re.sub(r'^\S+:\s*','',name) if ':' in name else name
        cur={'name':name,'items':[]}; sections.append(cur)
    elif l.startswith('### ') and cur is not None:
        title=re.sub(r'^\d+\.\s*','',l[4:].strip())
    elif l.startswith('```') and cur is not None:
        j=i+1; buf=[]
        while not lines[j].startswith('```'): buf.append(lines[j]); j+=1
        cur['items'].append({'t':title,'b':'\n'.join(buf)}); i=j
    i+=1
print(json.dumps(sections,ensure_ascii=False))
