# Builds the v2 (single consolidated message) page from consolidated-message.md
import json,os,re
D=os.path.dirname(os.path.abspath(__file__))
md=open(D+'/consolidated-message.md',encoding='utf-8').read()
msg=re.search(r'```\n(.*?)\n```',md,re.S).group(1)
tpl=open(D+'/../src/template.html',encoding='utf-8').read()
css=re.search(r'<style>\n(.*?)\n\.sel\{[^}]*\}',tpl,re.S).group(0).replace('<style>\n','')
css=css[:css.rfind('.sel{')]+'.sel{position:fixed;opacity:0;pointer-events:none}'
html=open(D+'/page.html',encoding='utf-8').read().replace('__CSS__',css).replace('__MSG__',json.dumps(msg,ensure_ascii=False).replace('</','<\\/'))
open(D+'/index.html','w',encoding='utf-8').write(html)
open(D+'/almasiya-message-v2.html','w',encoding='utf-8').write('<!doctype html>\n<html lang="ar" dir="rtl">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n'+html+'\n</body>\n</html>\n')
