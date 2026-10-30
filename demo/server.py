"""Local-only educational API. Do not expose to a public network."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from .project import DATA, SearchEngine, api_search, feedback, read_json, save_json, ROOT

class Handler(BaseHTTPRequestHandler):
    engine = None
    simulate_failure = False

    def do_GET(self):
        if self.path != '/health':
            self.send_json(404, {'error':'not_found'}); return
        self.send_json(200,{'status':'ok','educational_demo':True})

    def do_POST(self):
        if self.path not in ('/search','/feedback'):
            self.send_json(404,{'error':'not_found'}); return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size<1 or size>4096: raise ValueError('invalid_body_size')
            payload=json.loads(self.rfile.read(size).decode('utf-8'))
            if self.path=='/search':
                code,body=api_search(self.engine,payload,self.simulate_failure)
            else:
                if not isinstance(payload,dict): raise ValueError('object_required')
                body=feedback(payload.get('record_id'),payload.get('action'),payload.get('actor'),payload.get('proposed_style'))
                path=ROOT/'demo/runtime/feedback.json'
                events=read_json(path) if path.exists() else []
                events.append(body); save_json(path,events); code=200
        except (ValueError,UnicodeError) as exc:
            code,body=400,{'status':'error','error':str(exc)}
        self.send_json(code,body)

    def send_json(self,code,body):
        raw=json.dumps(body,ensure_ascii=False).encode('utf-8')
        self.send_response(code); self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def log_message(self,*args): pass

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8765); parser.add_argument('--simulate-failure',action='store_true'); args=parser.parse_args()
    Handler.engine=SearchEngine(read_json(DATA/'clean.json')); Handler.simulate_failure=args.simulate_failure
    print(f'Local educational API: http://127.0.0.1:{args.port}',flush=True)
    HTTPServer(('127.0.0.1',args.port),Handler).serve_forever()

if __name__=='__main__': main()
