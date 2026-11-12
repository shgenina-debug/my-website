import json,subprocess,sys
S=sys.argv[1]
data=subprocess.check_output(['python3',S+'/parse.py','templates/whatsapp/client-messages.md'],text=True).strip()
html=open(S+'/template.html',encoding='utf-8').read().replace('__DATA__',data.replace('</','<\\/'))
open('templates/whatsapp/index.html','w',encoding='utf-8').write(html)
