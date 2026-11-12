import json,subprocess,sys,os
S=sys.argv[1]; D=os.path.dirname(os.path.abspath(S))
def load(f): return json.loads(subprocess.check_output(['python3',S+'/parse.py',D+'/'+f],text=True))
data=json.dumps({'ar':load('client-messages.md'),'en':load('client-messages.en.md')},ensure_ascii=False)
html=open(S+'/template.html',encoding='utf-8').read().replace('__DATA__',data.replace('</','<\\/'))
open(D+'/index.html','w',encoding='utf-8').write(html)
