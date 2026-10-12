@echo off
echo Background Processes Report - starting...
echo Progress updates every 5 seconds. Ctrl+C to cancel.
set "SABY_REPORT_SELF=%~f0"
set "SABY_REPORT_FOLDER=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[Text.Encoding]::UTF8; $env:PYTHONIOENCODING='utf-8'; Write-Host 'Preparing Python...'; $logFolder=Join-Path $env:SABY_REPORT_FOLDER '.'; $source=[IO.File]::ReadAllText($env:SABY_REPORT_SELF,[Text.Encoding]::UTF8); $marker='#'+'__PYTHON_PAYLOAD__'; $payload=$source.Substring($source.IndexOf($marker)+$marker.Length).TrimStart([char]13,[char]10); $tempScript=Join-Path ([IO.Path]::GetTempPath()) ('saby-report-'+[guid]::NewGuid().ToString()+'.py'); try { [IO.File]::WriteAllText($tempScript,$payload,(New-Object Text.UTF8Encoding($false))); if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 -u $tempScript $logFolder --serve } elseif (Get-Command python -ErrorAction SilentlyContinue) { & python -u $tempScript $logFolder --serve } else { throw 'Install Python 3.9 or newer.' }; if ($LASTEXITCODE -ne 0) { throw 'Report generation failed.' } } catch { Write-Host $_ -ForegroundColor Red; exit 1 } finally { Remove-Item -LiteralPath $tempScript -ErrorAction SilentlyContinue }"
if errorlevel 1 pause
exit /b
#__PYTHON_PAYLOAD__
#!/usr/bin/env python3
"""Nine project methods: streaming log reader, Python 3.9+, stdlib only."""
import argparse, datetime as dt, json, re, sys, time, subprocess
from pathlib import Path
METHODS = ['HelpRoute.SyncImportWithCheck','DeliveryOffline.ImportScheduleInit','Production.Import','FaceBalance.Import','LabelPrintScales.ImportPLUCodes','DeviceType.ImportKKTSoftwareVersion','DeviceType.ImportScannerTestCodes','DeviceType.LogImportedDevices','IdentSync.SyncIdents']
PATTERN = re.compile('|'.join(re.escape(n) for n in METHODS))
EVENT = re.compile(r'^(?P<base>.*?)(?:-|_)events(?:_(?P<rotation>\d+))?\.log$',re.I)
STAMP = re.compile(r'^(\d\d):(\d\d):(\d\d)\.(\d{3})')
EXEC = re.compile(r'\[exec_period\]\s+(\d+)')

def collect(folder, recursive=False):
    files = [p for p in (folder.rglob('*.log') if recursive else folder.glob('*.log')) if EVENT.match(p.name)]
    files.sort(key=lambda p:(str(p.parent),EVENT.match(p.name)['base'],int(EVENT.match(p.name)['rotation'] or 0)))
    print('Events files: %d; %.1f MB' % (len(files),sum(p.stat().st_size for p in files)/1048576),flush=True)
    if not files: raise ValueError('Не найдены events.log в папке: '+str(folder))
    pending={}; completed=[]; rpc=[]; states={}; scanned=0; first=None; last=None; last_report=time.monotonic()
    for i,p in enumerate(files,1):
        source=str(p.relative_to(folder)); base=EVENT.match(p.name)['base']; process=re.sub(r'^\d{4}-\d{2}-\d{2}_','',base) or 'Launcher'
        scope=(str(p.parent),base)
        date=re.search(r'\d{4}-\d{2}-\d{2}',p.name)
        day=dt.date.fromisoformat(date[0]).toordinal()*86400000 if date else 0
        previous,day=states.get(scope,(None,day))
        print('[%d/%d] %s (%.1f MB)'%(i,len(files),source,p.stat().st_size/1048576),flush=True)
        with p.open(encoding='utf-8-sig',errors='replace') as stream:
            for ln,line in enumerate(stream,1):
                scanned+=1
                if time.monotonic()-last_report>=5:
                    print('  lines: %s; completed: %s; file line: %s'%(f'{scanned:,}',len(completed),f'{ln:,}'),flush=True);last_report=time.monotonic()
                tm=STAMP.match(line)
                if not tm:continue
                h,m,s,ms=map(int,tm.groups());raw=((h*60+m)*60+s)*1000+ms
                if previous is not None and previous-raw>43200000:day+=86400000
                previous=raw;t=day+raw;first=t if first is None else min(first,t);last=t if last is None else max(last,t)
                if not PATTERN.search(line):continue
                c=line.rstrip('\r\n').split('\t');msg=c[-1];trace=c[4] if len(c)>5 else ''
                ctx=c[8] if len(c)>9 else c[5] if len(c)>5 else ''
                name=re.sub(r'/\d+$','',ctx.strip())
                if name in METHODS and ('[w][start]' in msg or '[w][finish]' in msg):
                    request=re.search(r'\[w\]\[(?:start|finish)\](?:\[(\d+)\])?',msg);rid=request[1] or ''
                    pid=c[1].split(']')[0] if len(c)>1 else ''
                    key=(scope,pid,trace,name,rid)
                    if '[w][start]' in msg:
                        if key in pending:
                            old=pending.pop(key);old['end']=None;old['duration']=None;old['state']='Нет завершения';completed.append(old)
                        pending[key]=dict(name=name,start=t,file=source,line=ln,process=process,trace=trace)
                    else:
                        row=pending.pop(key,None);dur=EXEC.search(msg)
                        if row is None:
                            if not dur:continue
                            row=dict(name=name,start=t-int(dur[1]),file=source,line=ln,process=process,trace=trace,estimated=True)
                        row.update(end=t,duration=max(0,t-row['start']),finish_file=source,finish_line=ln,state='Завершён',status=(re.search(r'status:\s*(.*?)(?:\s*\[exec_period\]|$)',msg) or ['',''])[1])
                        completed.append(row)
                elif '[rpc call][finish]' in msg:
                    match=re.search(r'\[rpc call\]\[finish\]\s*([^\s]+)',msg)
                    name=re.sub(r'/\d+$','',match[1]) if match else ''
                    dur=EXEC.search(msg);child=re.search(r'\bruuid:([\w-]+)',msg)
                    if name in METHODS and dur:
                        rpc.append(dict(name=name,start=t-int(dur[1]),end=t,duration=int(dur[1]),file=source,line=ln,process=process,trace=child[1] if child else trace,state='RPC',estimated=True,scope=str(p.parent)))
        states[scope]=(previous,day)
    for row in pending.values():row.update(end=None,duration=None,state='Нет завершения');completed.append(row)
    receivers={(str(Path(r['file']).parent),r['trace'],r['name']) for r in completed}
    for r in rpc:
        key=(str(Path(r['file']).parent),r['trace'],r['name'])
        if key not in receivers:completed.append(r)
    completed.sort(key=lambda r:(r['start'],r['name']))
    for i,r in enumerate(completed):
        r['id']=i;r['time']=absolute(r['start']);r['start']-=first
        if r['end'] is not None:r['end']-=first
    return completed,dict(files=len(files),lines=scanned,span=max(1,(last or 0)-(first or 0)),origin=absolute(first or 0),folder=str(folder))

def absolute(t):
    day=int(t//86400000);date=dt.date.fromordinal(max(1,day)).isoformat()
    return date+' '+f'{int(t//3600000)%24:02}:{int(t//60000)%60:02}:{int(t//1000)%60:02}.{int(t)%1000:03}'

HTML=r'''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Фоновые синхронизации — 9 методов</title><style>
*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:#24384c;font:13px Segoe UI,Arial}main{max-width:1600px;margin:auto;padding:24px}h1{font-size:23px;margin:0 0 8px}.muted{color:#718298;line-height:1.5}.panel{background:white;border:1px solid #dce5ef;border-radius:10px;padding:18px;margin:18px 0}.toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap}button{background:white;border:1px solid #c9d8e8;border-radius:5px;padding:7px 12px;color:#245e99;cursor:pointer}svg{display:block;width:100%;min-width:1000px;user-select:none}.scroll{overflow:auto}.bar{cursor:pointer}.bar:hover{stroke:#172e48;stroke-width:2}.selected{stroke:#172e48;stroke-width:3}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:9px;border-bottom:1px solid #e7edf4;font-variant-numeric:tabular-nums}th{background:#f3f7fb}tr[data-id]{cursor:pointer}tr[data-id]:hover{background:#edf5ff}#detail{white-space:pre-wrap;line-height:1.6}summary{cursor:pointer}#selection{pointer-events:none}.empty{padding:20px;color:#718298}</style><main><h1>Фоновые синхронизации · 9 методов</h1><div class="muted" id="source"></div><div class="panel"><div class="toolbar"><b id="totals"></b><button id="reset">Весь журнал</button><span class="muted">Выделите участок шкалы мышью для увеличения. Нажмите на вызов для подробностей.</span></div><p class="muted">Полоса — время вызова вместе с ожиданиями, не загрузка ЦП. Повторы показаны отдельно, одновременные вызовы — на разных уровнях. Незавершённый вызов отмечен ромбом; длительность неизвестна.</p><div class="scroll"><svg id="timeline"></svg></div><div class="muted" id="window"></div></div><div class="panel"><b>Выбранный вызов</b><div id="detail" class="muted">Нажмите на полосу на таймлайне.</div></div><details class="panel"><summary>Все вызовы по времени</summary><div class="scroll"><table><thead><tr><th>Время</th><th>Метод</th><th>Длительность</th><th>Процесс / результат</th></tr></thead><tbody id="calls"></tbody></table></div><button id="more" hidden>Ещё 200</button></details></main><script>
const D=__DATA__,M=__META__,N=__NAMES__,$=id=>document.getElementById(id),esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;'),C=['#d45c3b','#ac547c','#8572cc','#cf893f','#329b8c','#438fc0','#b363a6','#698b42','#cc5261'];let range=[0,M.span],selected=null,limit=200,drag=null;
$('source').textContent=M.folder+' · '+M.files+' events-файлов · начало журнала '+M.origin;
$('totals').textContent=D.length+' вызовов · '+D.filter(r=>r.end===null).length+' без завершения';
function clock(t){return new Date(Date.parse(M.origin.replace(' ','T')+'Z')+t).toISOString().replace('T',' ').slice(0,23)}
function choose(id){selected=id;const r=D[id];$('detail').className='';$('detail').textContent=r.name+'\n'+r.time+' → '+(r.end===null?'завершение не найдено':clock(r.end))+'\nДлительность: '+(r.duration===null?'неизвестна':r.duration+' мс')+' · '+r.process+' · '+(r.status||r.state)+'\nИсточник: '+r.file+':'+r.line+(r.finish_file?'\nЗавершение: '+r.finish_file+':'+r.finish_line:'')+'\nTrace: '+r.trace+(r.estimated?'\nНачало восстановлено по exec_period; '+(r.state==='RPC'?'интервал взят со стороны вызывающего процесса.':'начало в журнале не найдено.'):'');draw()}
function draw(){const [a,b]=range,span=Math.max(1,b-a),left=430,right=1380,x=t=>left+(t-a)/span*(right-left);let y=55,s='';for(let i=0;i<=6;i++){const t=a+span*i/6;s+=`<text x="${x(t)}" y="18" text-anchor="${i===6?'end':'start'}" font-size="11" fill="#49627d">${clock(t).slice(11)}</text>`}
N.forEach((name,idx)=>{const all=D.filter(r=>r.name===name),rr=all.filter(r=>r.start<=b&&(r.end??r.start)>=a),ends=[],placed=[];rr.forEach(r=>{let lane=ends.findIndex(end=>end<=r.start);if(lane<0)lane=ends.length;ends[lane]=Math.max(r.start+1,r.end??r.start);placed.push([r,lane])});const height=Math.max(62,ends.length*20+14);s+=`<rect x="0" y="${y-10}" width="1400" height="${height}" fill="${idx%2?'#f8fafc':'#fff'}"/><text x="0" y="${y+6}" font-size="13" fill="${C[idx]}">${esc(name)}</text>`;const finished=all.filter(r=>r.duration!==null),max=finished.reduce((n,r)=>Math.max(n,r.duration),0),avg=finished.length?Math.round(finished.reduce((n,r)=>n+r.duration,0)/finished.length):null;s+=`<text x="0" y="${y+25}" font-size="11" fill="#718298">Вызовов: ${all.length} · среднее ${avg===null?'—':avg+' мс'} · макс. ${finished.length?max+' мс':'—'}</text>`;if(!rr.length)s+=`<text x="${left}" y="${y+12}" font-size="12" fill="#9aa8b7">${all.length?'Нет вызовов в этом окне':'Не обнаружен'}</text>`;placed.forEach(([r,lane])=>{const xx=x(Math.max(a,r.start)),yy=y+lane*20,tip=esc(r.time+' · '+(r.duration===null?'длительность неизвестна':r.duration+' мс')+' · '+r.process);s+=r.end===null?`<path data-id="${r.id}" class="bar ${selected===r.id?'selected':''}" d="M${xx},${yy} l5,7 l-5,7 l-5,-7 Z" fill="${C[idx]}"><title>${tip}</title></path>`:`<rect data-id="${r.id}" class="bar ${selected===r.id?'selected':''}" x="${xx}" y="${yy}" width="${Math.max(2,x(Math.min(b,r.end))-xx)}" height="14" rx="3" fill="${C[idx]}"><title>${tip}</title></rect>`});y+=height});for(let i=0;i<=6;i++)s+=`<line x1="${left+i*(right-left)/6}" x2="${left+i*(right-left)/6}" y1="30" y2="${y}" stroke="#cdd8e5" opacity=".5" pointer-events="none"/>`;$('timeline').setAttribute('viewBox',`0 0 1400 ${y+8}`);$('timeline').innerHTML=s;$('window').textContent=clock(a)+' — '+clock(b)+' · '+((b-a)/1000).toFixed(3)+' с';}
function list(){const visible=D.filter(r=>r.start<=range[1]&&(r.end??r.start)>=range[0]);$('calls').innerHTML=visible.slice(0,limit).map(r=>`<tr data-id="${r.id}"><td>${esc(r.time)}</td><td>${esc(r.name)}</td><td>${r.duration===null?'неизвестна':r.duration+' мс'}</td><td>${esc(r.process+' · '+(r.status||r.state))}</td></tr>`).join('');$('more').hidden=visible.length<=limit;}
$('timeline').onclick=e=>{if(drag&&drag.moved)return;const el=e.target.closest('[data-id]');if(el)choose(Number(el.dataset.id))};$('calls').onclick=e=>{const el=e.target.closest('[data-id]');if(el)choose(Number(el.dataset.id))};$('more').onclick=()=>{limit+=200;list()};$('reset').onclick=()=>{range=[0,M.span];limit=200;draw();list()};function pos(e){const box=$('timeline').getBoundingClientRect();return Math.max(430,Math.min(1380,(e.clientX-box.left)/box.width*1400))} $('timeline').onpointerdown=e=>{if(pos(e)<=430||e.button!==0)return;drag={x:pos(e),moved:false};$('timeline').setPointerCapture(e.pointerId)};$('timeline').onpointermove=e=>{if(!drag)return;const xx=pos(e);drag.moved=Math.abs(xx-drag.x)>6;if(drag.moved){$('selection')?.remove();const box=document.createElementNS('http://www.w3.org/2000/svg','rect');box.id='selection';box.setAttribute('x',Math.min(xx,drag.x));box.setAttribute('y',30);box.setAttribute('width',Math.abs(xx-drag.x));box.setAttribute('height',10000);box.setAttribute('fill','#2274cf');box.setAttribute('opacity','.12');$('timeline').append(box)}};$('timeline').onpointerup=e=>{if(!drag)return;const xx=pos(e);if(drag.moved){const [a,b]=range;range=[a+(Math.min(xx,drag.x)-430)/950*(b-a),a+(Math.max(xx,drag.x)-430)/950*(b-a)];limit=200;draw();list()}setTimeout(()=>drag=null,0)};$('timeline').onpointercancel=()=>{drag=null;$('selection')?.remove()};draw();list();
</script></html>'''

def serve(out):
    code="""import http.server,functools,sys,threading,webbrowser
from urllib.parse import quote
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=sys.argv[1]))
threading.Timer(.5,lambda:webbrowser.open('http://127.0.0.1:'+str(s.server_port)+'/'+quote(sys.argv[2]))).start()
t=threading.Timer(7200,s.shutdown);t.daemon=True;t.start()
s.serve_forever()
s.server_close()
"""
    subprocess.Popen([sys.executable,'-c',code,str(out.parent),out.name],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def main():
    ap=argparse.ArgumentParser(description='Таймлайн девяти фоновых методов проекта')
    ap.add_argument('folder',nargs='?',default=str(Path(__file__).resolve().parent));ap.add_argument('--recursive',action='store_true');ap.add_argument('--output',default='ReportBackrgoudProcees.html');ap.add_argument('--serve',action='store_true');a=ap.parse_args()
    folder=Path(a.folder).resolve()
    if not folder.is_dir():ap.error('Папка не существует: '+str(folder))
    started=time.monotonic();rows,meta=collect(folder,a.recursive)
    encode=lambda v:json.dumps(v,ensure_ascii=False).replace('</','<\\/')
    page=HTML.replace('__DATA__',encode(rows)).replace('__META__',encode(meta)).replace('__NAMES__',encode(METHODS));out=folder/a.output;out.write_text(page,encoding='utf-8')
    print('Done: %d calls; %.1f seconds\n%s'%(len(rows),time.monotonic()-started,out),flush=True)
    if a.serve:serve(out)
if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:print('Cancelled.',flush=True);sys.exit(130)
    except Exception:
        import traceback
        traceback.print_exc();sys.exit(1)
