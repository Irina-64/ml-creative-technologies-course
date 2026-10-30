"""Record actual localhost HTTP responses as an asciinema v2 cast and JSON."""
import json
import threading
import time
from http.server import HTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from .server import Handler
from .project import DATA, RESULTS, SearchEngine, read_json, save_json

def run():
    Handler.engine=SearchEngine(read_json(DATA/'clean.json'))
    server=HTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    scenarios=[('Поиск','/search',{'query':'саксофон лаконичный'},False),
               ('Выбор','/feedback',{'record_id':'P001','action':'select','actor':'designer_demo'},False),
               ('Пустой запрос','/search',{'query':''},False),
               ('Другой язык','/search',{'query':'jazz minimalist'},False),
               ('Резервный режим','/search',{'query':'джаз минимализм'},True)]
    events=[]; records=[]; text=[]; start=time.monotonic()
    try:
        for label,route,payload,failure in scenarios:
            Handler.simulate_failure=failure
            request=Request(f'http://127.0.0.1:{server.server_port}{route}',data=json.dumps(payload,ensure_ascii=False).encode('utf-8'),headers={'Content-Type':'application/json; charset=utf-8'})
            try:
                with urlopen(request,timeout=5) as reply: status=reply.status; body=json.loads(reply.read())
            except HTTPError as error:
                status=error.code; body=json.loads(error.read())
            record={'case':label,'path':route,'input':payload,'http_status':status,'output':body}
            records.append(record)
            block=f'{label}\nPOST {route} {json.dumps(payload,ensure_ascii=False)}\nHTTP {status}\n{json.dumps(body,ensure_ascii=False,indent=2)}\n\n'
            text.append(block); events.append([round(time.monotonic()-start,4),'o',block.replace('\n','\r\n')])
            print(label,status,body.get('status'),flush=True)
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=3); Handler.simulate_failure=False
    save_json(RESULTS/'walkthrough.json',records)
    (RESULTS/'walkthrough.txt').write_text('Автоматическая запись фактических HTTP-вызовов localhost. Не пользовательское исследование.\n\n'+''.join(text),encoding='utf-8')
    header={'version':2,'width':110,'height':38,'title':'Учебный API — фактические ответы','env':{'TERM':'xterm-256color','SHELL':'python'}}
    (RESULTS/'walkthrough.cast').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in [header,*events])+'\n',encoding='utf-8')

if __name__=='__main__': run()
