"""Inspect, create, deploy or verify a selected static Pages project using current Wrangler auth."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from cloudflare_transport import make_server


class APIError(Exception):
    def __init__(self,status,errors):
        self.status,self.errors=status,errors
        super().__init__(f'Cloudflare HTTP {status}')


def run_wrangler(executable,arguments,env,cwd,capture=False):
    command=[executable,*arguments]
    if os.name=='nt' and Path(executable).suffix.lower() in ['.cmd','.bat']:
        command=['cmd.exe','/d','/c',*command]
    return subprocess.run(command,env=env,cwd=cwd,capture_output=capture,check=True)


def find_wrangler(explicit,project):
    choices=[explicit,os.environ.get('JIANZHOU_WRANGLER'),
             str(project/'node_modules/.bin'/('wrangler.cmd' if os.name=='nt' else 'wrangler')),
             shutil.which('wrangler')]
    if os.name=='nt':
        choices.append('E:/CodexTools/Cloudflare/wrangler.cmd')
    for choice in choices:
        if choice and Path(choice).is_file():
            return str(Path(choice).resolve())
    raise RuntimeError('Wrangler not found. Pass --wrangler or configure JIANZHOU_WRANGLER.')


def api_session(wrangler,env,project):
    result=run_wrangler(wrangler,['auth','token','--json'],env,project,capture=True)
    raw=result.stdout.decode('utf-8',errors='replace')
    start=raw.find('{')
    if start<0:
        raise RuntimeError('Wrangler returned no JSON credential; log in with Wrangler first.')
    credential,_=json.JSONDecoder().raw_decode(raw[start:])
    token=credential.get('token')
    if not token:
        raise RuntimeError('Wrangler returned no token field. Credential values were withheld.')
    session=requests.Session()
    session.trust_env=False
    session.headers.update({'Authorization':'Bearer '+token,'User-Agent':'Jianzhou-Pages-Publisher'})
    session.mount('https://',HTTPAdapter(max_retries=Retry(total=2,backoff_factor=.5,status_forcelist=[502,503,504])))
    return session


def api(session,method,path,allow_missing=False,**kwargs):
    response=session.request(method,'https://api.cloudflare.com/client/v4'+path,timeout=(15,60),**kwargs)
    if allow_missing and response.status_code==404:
        return None
    data=response.json()
    if not response.ok or not data.get('success',False):
        raise APIError(response.status_code,data.get('errors',[]))
    return data['result']


def select_account(session,explicit):
    accounts=api(session,'GET','/accounts',params={'per_page':50})
    if explicit:
        if not any(account['id']==explicit for account in accounts):
            raise RuntimeError('Selected account is not available to the current user.')
        return explicit
    if len(accounts)!=1:
        print(json.dumps({'accounts':[{'id':a['id'],'name':a['name']} for a in accounts]},ensure_ascii=False))
        raise RuntimeError('Pass --account-id to select the intended account.')
    return accounts[0]['id']


def verify_site(url,paths):
    checks=[]
    with requests.Session() as session:
        session.mount('https://',HTTPAdapter(max_retries=Retry(total=2,backoff_factor=.5)))
        for path in dict.fromkeys(['/',*paths]):
            response=session.get(url.rstrip('/')+'/'+path.lstrip('/'),timeout=(15,40),stream=True)
            response.raise_for_status()
            checks.append({'path':path,'status':response.status_code})
            response.close()
    return checks


def deploy(wrangler,env,project,name,directory,transport):
    if not (directory/'index.html').is_file():
        raise RuntimeError('Static output must contain index.html; build the project first.')
    child_env=env.copy()
    server=None
    thread=None
    if transport=='relay':
        server=make_server()
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        local=f'http://127.0.0.1:{server.server_port}/client/v4'
        child_env.update({'CLOUDFLARE_API_BASE_URL':local,'CLOUDFLARE_BASE_URL':local,
                          'NO_PROXY':'127.0.0.1,localhost'})
        for key in ['HTTPS_PROXY','HTTP_PROXY','ALL_PROXY','https_proxy','http_proxy','all_proxy']:
            child_env.pop(key,None)
    try:
        run_wrangler(wrangler,['pages','deploy',str(directory),'--project-name',name,
                              '--branch',env['JIANZHOU_PUBLISH_BRANCH']],child_env,project)
    finally:
        if server:
            server.shutdown()
            server.server_close()
            thread.join()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['inspect','ensure-project','deploy','verify'])
    parser.add_argument('--project-dir',type=Path,default=Path.cwd())
    parser.add_argument('--project-name',required=True)
    parser.add_argument('--account-id')
    parser.add_argument('--wrangler')
    parser.add_argument('--branch',default='main')
    parser.add_argument('--directory',default='dist')
    parser.add_argument('--transport',choices=['direct','relay'],default='direct')
    parser.add_argument('--site-url')
    parser.add_argument('--check-path',action='append',default=[])
    args=parser.parse_args()
    project=args.project_dir.resolve()
    if not project.is_dir():
        parser.error('Project directory does not exist.')
    env=os.environ.copy()
    env['JIANZHOU_PUBLISH_BRANCH']=args.branch
    wrangler=find_wrangler(args.wrangler,project)
    # Preserve the encrypted credential mode used by this machine's existing wrapper.
    if os.name=='nt' and wrangler.lower().replace('\\','/')=='e:/codextools/cloudflare/wrangler.cmd':
        env.setdefault('CLOUDFLARE_AUTH_USE_KEYRING','true')
    with api_session(wrangler,env,project) as session:
        user=api(session,'GET','/user')
        account=select_account(session,args.account_id)
        env['CLOUDFLARE_ACCOUNT_ID']=account
        path=f'/accounts/{account}/pages/projects/{args.project_name}'
        current=api(session,'GET',path,allow_missing=True)
        created=False
        if args.action=='ensure-project' and current is None:
            current=api(session,'POST',f'/accounts/{account}/pages/projects',
                        json={'name':args.project_name,'production_branch':args.branch})
            created=True
        if args.action=='deploy':
            if current is None:
                raise RuntimeError('Project does not exist. Run ensure-project once first.')
            directory=(project/args.directory).resolve()
            deploy(wrangler,env,project,args.project_name,directory,args.transport)
            current=api(session,'GET',path)
        url=args.site_url or ('https://'+current['subdomain'] if current else None)
        report={'action':args.action,'user':user['email'],'account_id':account,
                'project':args.project_name,'exists':current is not None,'created':created,'url':url}
        if args.action in ['verify','deploy']:
            if not url:
                raise RuntimeError('No site URL is available to verify.')
            report['checks']=verify_site(url,args.check_path)
        print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    try:
        main()
    except APIError as error:
        print(json.dumps({'status':error.status,'errors':error.errors},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(3)
    except (RuntimeError,requests.RequestException,subprocess.CalledProcessError) as error:
        print(str(error),file=sys.stderr)
        raise SystemExit(1)
