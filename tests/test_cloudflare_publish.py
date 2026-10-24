import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

import requests

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import cloudflare_pages as publisher
from cloudflare_transport import make_server


class PublishingBehavior(unittest.TestCase):
    def test_relay_preserves_binary_upload_without_logging_credentials(self):
        seen=[]
        def upstream(method,path,body,headers):
            seen.append((method,path,body,headers))
            return 200,{'Content-Type':'application/octet-stream'},b'result\x00\xff'
        server=make_server(requester=upstream)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            thread.start()
            try:
                response=requests.post(f'http://127.0.0.1:{server.server_port}/client/v4/pages/assets/upload?fixture=yes',
                    data=b'file\x00\xff',headers={'Authorization':'Bearer fixture-credential','Content-Type':'application/octet-stream'},timeout=3)
                self.assertEqual(response.content,b'result\x00\xff')
            finally:
                server.shutdown();server.server_close();thread.join()
        self.assertEqual(seen[0][:3],('POST','/client/v4/pages/assets/upload?fixture=yes',b'file\x00\xff'))
        self.assertEqual(seen[0][3]['Authorization'],'Bearer fixture-credential')
        self.assertNotIn('fixture-credential',output.getvalue())
        self.assertNotIn('fixture=yes',output.getvalue())

    def test_deploy_failure_closes_relay_and_preserves_caller_environment(self):
        urls=[]
        def server_factory():
            return make_server(requester=lambda *args:(200,{'Content-Type':'application/json'},b'{}'))
        def child(executable,arguments,env,cwd):
            urls.append(env['CLOUDFLARE_API_BASE_URL']+'/user')
            response=requests.get(urls[-1],timeout=3)
            self.assertEqual(response.status_code,200)
            raise subprocess.CalledProcessError(7,['fixture-wrangler'])
        env={'JIANZHOU_PUBLISH_BRANCH':'main','HTTPS_PROXY':'http://fixture-proxy'}
        before=env.copy()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'index.html').write_text('fixture',encoding='utf-8')
            with patch.object(publisher,'make_server',side_effect=server_factory),patch.object(publisher,'run_wrangler',side_effect=child):
                with self.assertRaises(subprocess.CalledProcessError):
                    publisher.deploy('fixture',env,root,'fixture-project',root,'relay')
        self.assertEqual(env,before)
        with self.assertRaises(requests.ConnectionError):
            requests.get(urls[0],timeout=.5)

    def test_existing_project_is_not_created_again(self):
        calls=[]
        def api(session,method,path,**kwargs):
            calls.append(method)
            if path=='/user':return {'email':'fixture@example.com'}
            if path=='/accounts':return [{'id':'fixture-account','name':'fixture'}]
            return {'name':'fixture-project','subdomain':'fixture-project.pages.dev'}
        with tempfile.TemporaryDirectory() as directory:
            argv=['publisher','ensure-project','--project-dir',directory,'--project-name','fixture-project']
            output=io.StringIO()
            output.reconfigure=lambda **kwargs:None
            with patch.object(sys,'argv',argv),patch.object(publisher,'find_wrangler',return_value='fixture'),patch.object(publisher,'api_session',return_value=contextlib.nullcontext(object())),patch.object(publisher,'api',side_effect=api),contextlib.redirect_stdout(output):
                publisher.main()
            self.assertFalse(json.loads(output.getvalue())['created'])
            self.assertTrue(all(method=='GET' for method in calls))


if __name__=='__main__':
    unittest.main()
