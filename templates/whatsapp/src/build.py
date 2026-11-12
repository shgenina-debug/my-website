import subprocess,sys,os
S=sys.argv[1]; D=os.path.dirname(os.path.abspath(S))
data=subprocess.check_output(['python3',S+'/parse.py',D+'/client-messages.md'],text=True).strip()
html=open(S+'/template.html',encoding='utf-8').read().replace('__DATA__',data.replace('</','<\\/'))
open(D+'/index.html','w',encoding='utf-8').write(html)
# standalone file that opens directly on a phone (full document skeleton)
open(D+'/whatsapp-messages.html','w',encoding='utf-8').write('<!doctype html>\n<html lang="ar" dir="rtl">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n'+html+'\n</body>\n</html>\n')
