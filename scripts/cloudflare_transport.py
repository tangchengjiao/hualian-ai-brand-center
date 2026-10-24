"""Optional localhost API transport for the observed Node/Windows connection resets."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HOP_HEADERS={'host','content-length','transfer-encoding','connection','accept-encoding','content-encoding'}


def make_server(port=0, requester=None):
    def forward_request(method,path,body,headers):
        with requests.Session() as session:
            session.trust_env=False
            session.mount('https://',HTTPAdapter(max_retries=Retry(total=2,backoff_factor=.5,status_forcelist=[502,503,504])))
            response=session.request(method,'https://api.cloudflare.com'+path,data=body,
                                     headers=headers,timeout=(15,120),allow_redirects=False)
            return response.status_code,dict(response.headers),response.content

    send=requester or forward_request

    class Handler(BaseHTTPRequestHandler):
        protocol_version='HTTP/1.1'

        def log_message(self,*args):
            pass

        def forward(self):
            if not self.path.startswith('/client/v4/'):
                self.send_error(404)
                return
            if self.headers.get('Transfer-Encoding','').lower()=='chunked':
                chunks=[]
                while True:
                    size=int(self.rfile.readline().split(b';',1)[0].strip(),16)
                    if not size:
                        self.rfile.readline()
                        break
                    chunks.append(self.rfile.read(size))
                    self.rfile.read(2)
                body=b''.join(chunks)
            else:
                length=int(self.headers.get('Content-Length','0'))
                body=self.rfile.read(length) if length else None
            headers={k:v for k,v in self.headers.items() if k.lower() not in HOP_HEADERS}
            try:
                status,response_headers,content=send(self.command,self.path,body,headers)
            except requests.RequestException as error:
                status,response_headers=502,{'Content-Type':'application/json'}
                content=json.dumps({'success':False,'errors':[{'message':type(error).__name__}]}).encode()
            self.send_response(status)
            for key,value in response_headers.items():
                if key.lower() not in HOP_HEADERS:
                    self.send_header(key,value)
            self.send_header('Content-Length',str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            # No headers, query strings, response bodies or credentials in logs.
            print(self.command,urlsplit(self.path).path,status,flush=True)

        do_GET=forward
        do_POST=forward
        do_PUT=forward
        do_PATCH=forward

    return ThreadingHTTPServer(('127.0.0.1',port),Handler)
