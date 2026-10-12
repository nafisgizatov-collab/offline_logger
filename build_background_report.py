#!/usr/bin/env python3
"""Saby timeline: Python 3.9+, no dependencies."""
import argparse,json,re,datetime,subprocess,sys,time,threading,traceback,base64,os
from pathlib import Path
HTML = '<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Отчет по логам оффлайн</title><style>\n*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:#21354c;font:12px system-ui,Arial}main{padding:26px;max-width:1800px;margin:auto}h1{margin:0;font-size:28px}.sub{color:#708196;line-height:1.6}.panel{background:white;border:1px solid #dce5ee;border-radius:12px;padding:18px;margin:18px 0}.toolbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap}button,input,select{border:1px solid #cdd9e5;background:white;border-radius:6px;padding:8px;color:inherit}button{cursor:pointer}button.active,input.active,select.active{border-color:#2274cf;background:#e7f2ff;color:#1456a0}button.active{background:#2274cf;color:white}#chart{width:100%;height:150px;cursor:crosshair;display:block;touch-action:none}.scroll{height:calc(66vh + 150px);min-height:240px;overflow:auto;resize:vertical}table{width:100%;border-collapse:separate;border-spacing:0;table-layout:fixed}th{position:sticky;top:0;background:#edf3f9;z-index:2;text-align:left;padding:12px}td{padding:10px;border-bottom:1px solid #edf1f5;vertical-align:middle}th:first-child{width:39%}th:nth-child(2){width:45%}th:last-child{width:16%}.name{overflow-wrap:anywhere}.name.background,.name.log-only{color:#7b8796;font-style:italic}.branch{display:flex;align-items:center;gap:6px}.toggle{padding:0;width:22px;height:22px;flex-shrink:0}.leaf{width:22px;flex-shrink:0}.track{height:24px;position:relative;background:repeating-linear-gradient(to right,#f6f9fc 0,#f6f9fc calc(10% - 1px),#e4ebf3 calc(10% - 1px),#e4ebf3 10%)}.bar{position:absolute;top:5px;height:14px;min-width:2px;border-radius:3px;border-left:2px solid #183d60;border-right:2px solid #183d60}.small{font-size:11px;color:#8291a3}.selected td{border-top:2px solid #2581df;border-bottom:2px solid #2581df;background:#eff7ff}.selected td:first-child{border-left:2px solid #2581df}.selected td:last-child{border-right:2px solid #2581df}#details,#response,#params{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.7 Consolas,monospace}.legend{display:flex;gap:15px;flex-wrap:wrap;font-size:12px;margin:10px 0}.dot{display:inline-block;width:10px;height:10px;margin-right:5px;border-radius:2px}.axis{display:flex;justify-content:space-between;font-size:11px;font-weight:400}.hint{padding:8px 0;color:#60758d}#status{font-weight:600}.dur{font-variant-numeric:tabular-nums}\n .call-details{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,1fr);gap:24px}#response,#params{max-height:650px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere}@media(max-width:800px){.call-details{grid-template-columns:1fr}} .name.has-error,.has-error td.dur{color:#cc2435!important}.error-marker{cursor:pointer} .errors-hidden .error-marker{display:none} .name.console-event{color:#245b92;font-weight:600;font-style:normal} .filter-panel{display:flex;flex-direction:column;gap:12px}.filter-checkboxes{border-top:1px solid #edf1f5;padding-top:10px}.filter-checkboxes label{display:inline-flex;align-items:center;gap:5px;white-space:nowrap} .report-heading{display:flex;align-items:baseline;gap:20px;flex-wrap:wrap}.report-heading h1,.report-heading #logPeriod{font:700 28px system-ui,Arial;color:inherit} .console-marker{cursor:pointer} </style><main><div class="report-heading"><h1>Отчет по логам оффлайн</h1><span id="logPeriod"></span></div><div class="sub" id="subtitle"></div><div class="panel"><b>Активность во всём журнале</b><div class="hint">Выделите участок мышью, чтобы отфильтровать журнал. «Весь журнал» сбрасывает диапазон. Нажмите на пик: каскад перейдёт к активному вызову и выделит его рамкой. Высота — число одновременно выполняющихся методов БЛ/RPC, включая ожидания; это не загрузка CPU. Серые серии с суффиксом -background — вызовы без найденного UI-инициатора в цепочке родителей; при неполных логах источник может быть неизвестен.</div><div id="legend" class="legend"></div><svg id="chart" viewBox="0 0 1200 150"></svg><div id="chartaxis" class="axis"></div></div>\n<div class="panel filter-panel"><div class="toolbar filter-controls"><button id="all" class="active">Весь журнал</button><button id="near">Окно выбранного вызова</button><label title="Отступ до начала и после конца выбранного вызова"><input id="windowMs" type="number" value="1000" min="0" step="100" style="width:90px" aria-label="Отступ окна выбранного вызова в миллисекундах"> мс</label><button id="collapse">Свернуть всё</button><button id="expand">Развернуть всё</button><input id="query" list="methodSuggestions" autocomplete="off" placeholder="Найти метод и его вложенность" style="min-width:300px"><datalist id="methodSuggestions"></datalist><button id="clearQuery" title="сброс поиска" aria-label="сброс поиска" style="width:34px;height:34px;padding:0;font-size:20px;flex-shrink:0">×</button><select id="proc"><option value="">Все процессы</option></select><label>Длительность верхнего уровня от <input id="min" type="number" value="__THRESHOLD__" min="0" style="width:75px"> мс</label><button id="sort">По началу ↓</button><button id="resetBlacklist" hidden>Сбросить ЧС</button><span id="status"></span></div><div class="toolbar filter-checkboxes"><label id="visibleLabel" title="Снимите отметку, чтобы показать все процессы" style="padding:7px;border-radius:6px"><input id="visibleOnly" type="checkbox" checked> Только видимые процессы</label><label style="padding:7px;border-radius:6px" id="diagnosticsLabel"><input id="showDiagnostics" type="checkbox"> Показать ожидания и SQL</label><label id="consoleLabel"><input id="showConsole" type="checkbox" checked> Показывать логи UI-console</label><label id="errorsLabel"><input id="showErrors" type="checkbox" checked> Показать ошибки</label></div></div>\n<div class="sub">Обычный шрифт — запросы из HAR или invoke без явного асинхронного запуска. Серый курсив — остальные операции из events.log. Invoke подтверждает запрос; источник UI при неполных логах может требовать проверки. Стрелка раскрывает дочерние вызовы; длинные задачи показаны внутри инициатора. SQL и ожидания доступны через чекбокс «Показать ожидания и SQL». Вложенность по времени и trace — реконструкция, связь по ruuid — явная связь запуска.</div>\n<div class="panel scroll" id="scroll" title="Высоту списка можно менять: потяните нижний правый угол"><table><thead><tr><th>Метод / инициатор</th><th><div class="axis" id="axis"></div></th><th>Длительность / начало</th></tr></thead><tbody id="body"></tbody></table></div><div class="panel call-details"><div><b>Выбранный вызов</b><div id="details">Нажмите на название метода.</div></div><div><b>Параметры вызова</b><div id="paramsSource" class="small"></div><pre id="params">Нажмите на название метода.</pre></div><div><b>Результат вызова</b><div id="responseSource" class="small"></div><pre id="response">Нажмите на название метода.</pre></div></div></main><script>\nconst rows=__DATA__,meta=__META__,$=id=>document.getElementById(id),esc=s=>String(s).replaceAll(\'&\',\'&amp;\').replaceAll(\'<\',\'&lt;\').replaceAll(\'>\',\'&gt;\').replaceAll(\'"\',\'&quot;\');\nconst children=rows.map(()=>[]),roots=[],expanded=new Set(),blacklist=new Set(),palette=[\'#367dba\',\'#9b75bd\',\'#22a58f\',\'#e39c45\',\'#c56c92\',\'#6d8a9a\'];let selected=null,range=[0,meta.span],sortDuration=false,rangeMode="all",chartDrag=null,suppressChartClick=false;\nrows.forEach(r=>r.parent===null?roots.push(r.id):children[r.parent].push(r.id));\nconst processes=[...new Set(rows.map(r=>r.process))].sort(),colors=Object.fromEntries(processes.map((p,i)=>[p,palette[i%palette.length]]));\nprocesses.forEach(p=>{const o=document.createElement(\'option\');o.value=p;o.textContent=p;$(\'proc\').append(o)});\n$(\'logPeriod\').textContent=`${meta.logStart||meta.origin} — ${meta.logEnd||logClock(meta.span,true)}`;\n$(\'subtitle\').textContent=`${meta.files} журналов · ${meta.count} операций · ${roots.length} инициаторов · HAR: ${meta.har}. ${meta.errors.length?\'Ошибки HAR: \'+meta.errors.join(\'; \'):\'\'}`;\n$(\'min\').value=meta.threshold;\nconst uiInitiated=new Map();function fromUI(id){if(uiInitiated.has(id))return uiInitiated.get(id);const path=[],seen=new Set();let result=false;while(id!==null&&!seen.has(id)){if(uiInitiated.has(id)){result=uiInitiated.get(id);break}seen.add(id);const r=rows[id];path.push(id);if(r.visible||r.kind===\'HAR\'){result=true;break}id=r.parent}path.forEach(i=>uiInitiated.set(i,result));return result}\nconst activityRows=rows.filter(r=>[\'БЛ\',\'RPC\',\'HAR\'].includes(r.kind)),activityKey=r=>r.process+(fromUI(r.id)?\'\':\'-background\'),activityGroups=processes.flatMap(p=>[p,p+\'-background\']).filter(key=>activityRows.some(r=>activityKey(r)===key)),activityColors=Object.fromEntries(activityGroups.map(key=>[key,key.endsWith(\'-background\')?\'#929ba5\':colors[key]]));\n$(\'legend\').innerHTML=activityGroups.map(p=>`<span><i class="dot" style="background:${activityColors[p]}"></i>${esc(p)}</span>`).join(\'\');\n$(\'methodSuggestions\').innerHTML=[...new Set(rows.filter(r=>![\'Длинная задача\',\'SQL\'].includes(r.kind)).map(r=>r.name))].sort().map(name=>`<option value="${esc(name)}"></option>`).join(\'\');\n$(\'clearQuery\').onclick=()=>{$(\'query\').value=\'\';render();$(\'query\').focus()};\nconst seconds=t=>(t/1000).toFixed(3)+\' с\';\nfunction logClock(t,milliseconds=false){const origin=meta.originMs??Date.parse(meta.origin.replace(\' \',\'T\')+\'Z\');const date=new Date(origin+t);return date.toISOString().slice(11,milliseconds?23:19)}\nfunction render(){drawActivity();updateRangeOverlay();const [a,b]=range,pct=t=>(t-a)/(b-a)*100,q=$(\'query\').value.toLowerCase(),proc=$(\'proc\').value;const keep=new Set(),matched=new Set(),visibleOnly=$(\'visibleOnly\').checked,showDiagnostics=$(\'showDiagnostics\').checked,showErrors=$(\'showErrors\').checked,showConsole=$(\'showConsole\').checked;const forced=new Set(),errorPaths=new Set();$(\'chart\').classList.toggle(\'errors-hidden\',!showErrors);const diagnostic=r=>r.kind===\'SQL\'||r.kind===\'Длинная задача\';\nconst searchScope=new Set();if(q){for(const r of rows){if(!r.name.toLowerCase().includes(q))continue;const todo=[r.id];while(todo.length){const id=todo.pop();if(searchScope.has(id))continue;searchScope.add(id);todo.push(...children[id])}}}const inSearch=r=>(!q||searchScope.has(r.id))&&(!proc||r.process===proc);\nif(showErrors){for(const r of rows){if(!inSearch(r)||!r.has_error||!(r.call_errors||[]).some(error=>error.time>=a&&error.time<=b))continue;forced.add(r.id);let id=r.id;while(id!==null&&!errorPaths.has(id)){errorPaths.add(id);keep.add(id);id=rows[id].parent}}}\nfor(const r of rows){if(r.kind===\'Консоль UI\'&&!showConsole)continue;if((r.kind===\'Ошибка\'||r.kind===\'Ошибка UI\')&&!showErrors)continue;if(diagnostic(r)&&!showDiagnostics)continue;if(visibleOnly&&!r.visible&&!r.has_error)continue;if(r.end<a||r.start>b)continue;if((!q||r.name.toLowerCase().includes(q))&&(!proc||r.process===proc)){matched.add(r.id);let id=r.id;while(id!==null&&!keep.has(id)){keep.add(id);id=rows[id].parent}}}\n// Include descendants of a matching method; expansion remains controlled by the plus button.\nif(!visibleOnly&&(q||proc)){const todo=[...matched];while(todo.length){const id=todo.pop();for(const child of children[id]){const r=rows[child];if(r.end<a||r.start>b||diagnostic(r)&&!showDiagnostics)continue;if(!keep.has(child)){keep.add(child);todo.push(child)}}}}\nfor(const id of expanded){if(!keep.has(id)||!inSearch(rows[id]))continue;for(const child of children[id]){const r=rows[child];if(r.end>=a&&r.start<=b&&(!diagnostic(r)||showDiagnostics))keep.add(child)}}\nlet visible=[];function walk(ids,depth){const ordered=[...ids].sort((i,j)=>sortDuration?rows[j].duration-rows[i].duration:rows[i].start-rows[j].start);for(const id of ordered){if(!keep.has(id))continue;if(rows[id].kind===\'Консоль UI\'&&!showConsole)continue;if(depth===0&&rows[id].kind!==\'Консоль UI\'&&!errorPaths.has(id)&&rows[id].duration<Number($(\'min\').value))continue;const excluded=!errorPaths.has(id)&&(blacklist.has(rows[id].name)||(diagnostic(rows[id])&&!showDiagnostics));if(excluded){walk(children[id],depth);continue}visible.push([id,depth]);if(errorPaths.has(id)||expanded.has(id)||((q||proc)&&!matched.has(id)&&children[id].some(child=>keep.has(child))))walk(children[id],depth+1)}}walk(roots,0);\n$(\'body\').innerHTML=visible.map(([id,depth])=>{const r=rows[id],left=Math.max(a,r.start),right=Math.min(b,r.end);return `<tr id="row-${id}" data-id="${id}" class="${selected===id?\'selected\':\'\'} ${showErrors&&r.has_error?\'has-error\':\'\'}"><td><div class="branch" style="padding-left:${depth*18}px">${children[id].length?`<button class="toggle" data-toggle="${id}" aria-expanded="${expanded.has(id)}">${expanded.has(id)?\'−\':\'+\'}</button>`:\'<span class="leaf"></span>\'}<div class="name ${r.appearance} ${r.kind===\'Консоль UI\'?\'console-event\':\'\'} ${showErrors&&r.has_error?\'has-error\':\'\'}">${esc(r.name)} <span class="small">${esc(r.log_time)}</span> <button data-blacklist="${id}" title="Скрыть все вызовы этого метода" style="padding:1px 5px;font-size:11px;font-style:normal">в ЧС</button><div class="small">${esc(r.process)}${r.kind===\'Длинная задача\'?\' · длинная задача\':\'\'}${children[id].length?\' · \'+children[id].length+\' вложенных\':\'\'}</div></div></div></td><td><div class="track"><div class="bar" style="left:${Math.max(0,pct(left))}%;width:${Math.max(.1,(right-left)/(b-a)*100)}%;background:${r.visible?colors[r.process]:\'#929ba5\'}" title="${seconds(r.start)} → ${seconds(r.end)}"></div></div></td><td class="dur">${r.kind===\'Консоль UI\'?\'Событие UI\':r.kind===\'Ошибка UI\'?\'UI-error\':Math.round(r.duration)+\' мс\'}<div class="small">${seconds(r.start)} → ${seconds(r.end)}</div></td></tr>`}).join(\'\');\n$(\'axis\').innerHTML=Array.from({length:6},(_,i)=>`<span>${seconds(a+(b-a)*i/5)}</span>`).join(\'\');$(\'resetBlacklist\').hidden=blacklist.size===0;$(\'resetBlacklist\').textContent=\'Сбросить ЧС (\'+blacklist.size+\')\';$(\'status\').textContent=visible.length+\' строк\';$(\'all\').classList.toggle(\'active\',a===0&&b===meta.span);$(\'near\').classList.toggle(\'active\',rangeMode===\'near\');$(\'sort\').classList.toggle(\'active\',sortDuration);$(\'query\').classList.toggle(\'active\',!!q);$(\'clearQuery\').disabled=!q;$(\'visibleLabel\').style.background=visibleOnly?\'#e7f2ff\':\'\';$(\'visibleLabel\').style.color=visibleOnly?\'#1456a0\':\'\';$(\'proc\').classList.toggle(\'active\',!!proc);$(\'diagnosticsLabel\').style.background=showDiagnostics?\'#e7f2ff\':\'\';$(\'diagnosticsLabel\').style.color=showDiagnostics?\'#1456a0\':\'\';}\nfunction decodeSaby(value){\n if(Array.isArray(value))return value.map(decodeSaby);\n if(!value||typeof value!==\'object\')return value;\n if(Array.isArray(value.s)&&Array.isArray(value.d)&&value.s.length&&value.s.every(field=>field&&typeof field.n===\'string\')){\n  const fields=value.s;\n  const record=data=>{if(!Array.isArray(data))return decodeSaby(data);const result=Object.create(null);fields.forEach((field,i)=>{if(i<data.length){let cell=data[i];const type=field.t;const schema=Array.isArray(type)?type:type&&typeof type===\'object\'&&Array.isArray(type.s)?type.s:null;if(schema&&Array.isArray(cell))cell={s:schema,d:cell,f:type.f};result[field.n]=decodeSaby(cell)}});if(data.length>fields.length)result[\'Дополнительные значения\']=data.slice(fields.length).map(decodeSaby);return result};\n  // f=0 is a record, f=1 is a record set. Otherwise use the data shape.\n  const recordSet=value.f===1||(value.f!==0&&value.d.length>0&&value.d.every(row=>Array.isArray(row)&&row.length===fields.length));\n  return recordSet?value.d.map(record):record(value.d);\n }\n return Object.fromEntries(Object.entries(value).map(([key,child])=>[key,decodeSaby(child)]));\n}\n\nfunction prettyResponse(text){\n if(text===undefined||text===null)return \'Тело ответа не найдено в логах. Это не означает, что метод вернул пустой результат.\';\n text=String(text);try{return JSON.stringify(decodeSaby(JSON.parse(text)),null,2)}catch{}\n // Loggers may truncate JSON. Format its structure without changing string values.\n if(!/^[\\s]*[\\[{]/.test(text))return text;\n let output=\'\',depth=0,inString=false,escaped=false;\n const newline=()=>{output=output.replace(/[ \\t]+$/,\'\');if(!output.endsWith(\'\\n\'))output+=\'\\n\';output+=\'  \'.repeat(Math.max(0,depth))};\n for(let i=0;i<text.length;i++){const c=text[i];if(inString){output+=c;if(escaped)escaped=false;else if(c===\'\\\\\')escaped=true;else if(c===\'"\')inString=false;continue}\n if(c===\'"\'){inString=true;output+=c}else if(c===\'{\'||c===\'[\'){output+=c;depth++;newline()}else if(c===\'}\'||c===\']\'){depth=Math.max(0,depth-1);output=output.replace(/\\s+$/,\'\');newline();output+=c}else if(c===\',\'){output+=c;newline()}else if(c===\':\'){output+=\': \'}else if(!/\\s/.test(c)){output+=c}}\n return output.trimEnd();\n}\n\nfunction choose(id,scroll=true){selected=id;let p=rows[id].parent;while(p!==null){expanded.add(p);p=rows[p].parent}render();updateMarker();const {response,response_source,params,params_source,...info}=rows[id];delete info.response_previous_source;delete info.params_previous_source;delete info.response_invalid;delete info.params_invalid;$(\'params\').textContent=params===undefined?\'Параметры вызова не найдены в логах.\':prettyResponse(params);$(\'paramsSource\').textContent=params_source||\'\';$(\'details\').textContent=JSON.stringify(info,null,2);$(\'response\').textContent=prettyResponse(response);$(\'responseSource\').textContent=response_source||\'\';if(scroll)document.getElementById(\'row-\'+id)?.scrollIntoView({block:\'center\',behavior:\'smooth\'});}\n$(\'resetBlacklist\').onclick=()=>{blacklist.clear();render()};\n$(\'body\').onclick=e=>{const blocked=e.target.closest(\'[data-blacklist]\');if(blocked){blacklist.add(rows[Number(blocked.dataset.blacklist)].name);if(selected!==null&&blacklist.has(rows[selected].name)){selected=null;$(\'selection-marker\')?.remove();$(\'details\').textContent=\'Метод добавлен в ЧС.\'}render();return}const t=e.target.closest(\'[data-toggle]\');if(t){const id=Number(t.dataset.toggle);expanded.has(id)?expanded.delete(id):expanded.add(id);render();return}const tr=e.target.closest(\'tr\');if(tr)choose(Number(tr.dataset.id),false)};\n$(\'all\').onclick=()=>{rangeMode=\'all\';range=[0,meta.span];render()};function applySelectedWindow(){if(selected===null)return;rangeMode=\'near\';const r=rows[selected],pad=Math.max(0,Number($(\'windowMs\').value)||0);range=[Math.max(0,r.start-pad),Math.min(meta.span,r.end+pad)];if(range[1]<=range[0])range[1]=range[0]+1;render()}$(\'near\').onclick=applySelectedWindow;$(\'windowMs\').oninput=()=>{if($(\'near\').classList.contains(\'active\'))applySelectedWindow()};$(\'collapse\').onclick=()=>{expanded.clear();render()};$(\'expand\').onclick=()=>{rows.forEach(r=>expanded.add(r.id));render()};$(\'sort\').onclick=()=>{sortDuration=!sortDuration;$(\'sort\').textContent=sortDuration?\'По длительности ↓\':\'По началу ↓\';render()};[\'query\',\'proc\',\'min\',\'visibleOnly\',\'showDiagnostics\',\'showErrors\',\'showConsole\'].forEach(id=>$(id).oninput=render);\nconst bins=240,series=activityGroups.map(()=>Array(bins).fill(0));for(const r of activityRows){const lo=Math.max(0,Math.floor(r.start/meta.span*bins)),hi=Math.min(bins-1,Math.floor(r.end/meta.span*bins));for(let i=lo;i<=hi;i++)series[activityGroups.indexOf(activityKey(r))][i]+=Math.max(0,Math.min(r.end,(i+1)*meta.span/bins)-Math.max(r.start,i*meta.span/bins))/(meta.span/bins)}\nlet activityCache=null;\nfunction chartRange(){return rangeMode===\'near\'?range:[0,meta.span]}\nfunction chartTime(x,bounds=chartRange()){return bounds[0]+(x-30)/1160*(bounds[1]-bounds[0])}\nfunction chartPosition(t){const [a,b]=chartRange();return 30+(t-a)/Math.max(1,b-a)*1160}\nfunction drawActivity(){const [chartStart,chartEnd]=chartRange(),chartSpan=Math.max(1,chartEnd-chartStart);let plotSeries=series;if(chartStart!==0||chartEnd!==meta.span){const key=chartStart+\':\'+chartEnd;if(!activityCache||activityCache.key!==key){const zoom=activityGroups.map(()=>Array(bins).fill(0));for(const r of activityRows){if(r.end<chartStart||r.start>chartEnd)continue;const lo=Math.max(0,Math.floor((r.start-chartStart)/chartSpan*bins)),hi=Math.min(bins-1,Math.floor((r.end-chartStart)/chartSpan*bins));for(let i=lo;i<=hi;i++)zoom[activityGroups.indexOf(activityKey(r))][i]+=Math.max(0,Math.min(r.end,chartStart+(i+1)*chartSpan/bins)-Math.max(r.start,chartStart+i*chartSpan/bins))/(chartSpan/bins)}activityCache={key,series:zoom}}plotSeries=activityCache.series}const showBackground=!$(\'visibleOnly\').checked,shown=activityGroups.map((key,index)=>index).filter(index=>showBackground||!activityGroups[index].endsWith(\'-background\'));const peak=Math.max(1,...Array.from({length:bins},(_,i)=>shown.reduce((sum,index)=>sum+plotSeries[index][i],0)));let svg=`<text x="0" y="15" fill="#789">${peak.toFixed(1)}</text>`;for(let i=0;i<bins;i++){let y=140;shown.forEach(p=>{const s=plotSeries[p];const h=s[i]/peak*120;y-=h;if(h)svg+=`<rect x="${30+i*1160/bins}" y="${y}" width="${1160/bins}" height="${h}" fill="${activityColors[activityGroups[p]]}"><title>${logClock(chartStart+i*chartSpan/bins,true)} · ${esc(activityGroups[p])} · ${s[i].toFixed(2)} активных</title></rect>`})}if($(\'showConsole\').checked){for(const marker of meta.console_markers||[]){if(marker.time<chartStart||marker.time>chartEnd)continue;const x=chartPosition(marker.time),init=marker.type===\'initialization\';svg+=`<g class="console-marker" data-console-id="${marker.node}"><title>${esc(logClock(marker.time,true)+\' · \'+marker.label)}</title><line x1="${x}" x2="${x}" y1="22" y2="145" stroke="#176aca" stroke-width="1.5"/>${init?\'\':`<text x="${Math.min(1150,x+4)}" y="${init?20:36}" fill="#176aca" font-size="10" font-weight="${init?700:400}">${esc(marker.label)}</text>`}</g>`}}for(const error of meta.error_markers||[]){if(error.time<chartStart||error.time>chartEnd)continue;const x=chartPosition(error.time);svg+=`<g class="error-marker" data-error-id="${error.node}"><title>${esc(logClock(error.time,true)+\' · \'+error.file+\':\'+error.line+\' · \'+error.message)}</title><line x1="${x}" x2="${x}" y1="16" y2="145" stroke="#d92335" stroke-width="1.5"/><text x="${x}" y="12" fill="#d92335" font-size="10" text-anchor="middle">${esc(error.label||\'error\')}</text></g>`}$(\'chartaxis\').innerHTML=Array.from({length:7},(_,i)=>`<span>${logClock(chartStart+chartSpan*i/6)}</span>`).join(\'\');$(\'chart\').innerHTML=svg;$(\'legend\').innerHTML=shown.map(index=>{const key=activityGroups[index];return `<span><i class="dot" style="background:${activityColors[key]}"></i>${esc(key)}</span>`}).join(\'\');updateMarker();updateRangeOverlay();$(\'chart\').classList.toggle(\'errors-hidden\',!$(\'showErrors\').checked);}\n$(\'chartaxis\').innerHTML=Array.from({length:7},(_,i)=>`<span>${logClock(meta.span*i/6)}</span>`).join(\'\');\nfunction updateMarker(){ $(\'selection-marker\')?.remove(); if(selected===null)return; const x=chartPosition(rows[selected].start);if(x<30||x>1190)return; const line=document.createElementNS(\'http://www.w3.org/2000/svg\',\'line\');line.id=\'selection-marker\';line.setAttribute(\'x1\',x);line.setAttribute(\'x2\',x);line.setAttribute(\'y1\',5);line.setAttribute(\'y2\',145);line.setAttribute(\'stroke\',\'#df263b\');line.setAttribute(\'stroke-width\',\'2\');line.setAttribute(\'stroke-dasharray\',\'6 4\');line.style.pointerEvents=\'none\';$(\'chart\').append(line);}\n$(\'chart\').onclick=e=>{if(suppressChartClick){suppressChartClick=false;return;}const milestone=e.target.closest(\'[data-console-id]\');if(milestone){rangeMode=\'all\';range=[0,meta.span];$(\'query\').value=\'\';$(\'proc\').value=\'\';choose(Number(milestone.dataset.consoleId));return;}const error=e.target.closest(\'[data-error-id]\');if(error){rangeMode=\'all\';range=[0,meta.span];$(\'query\').value=\'\';$(\'proc\').value=\'\';choose(Number(error.dataset.errorId));return;}const time=chartTime(chartX(e));let candidates=rows.filter(r=>[\'БЛ\',\'RPC\',\'HAR\'].includes(r.kind)&&r.start<=time&&r.end>=time);if(!candidates.length)candidates=[...rows].sort((a,b)=>Math.abs(a.start-time)-Math.abs(b.start-time)).slice(0,1);if(!candidates.length)return;const r=candidates.sort((a,b)=>b.duration-a.duration)[0];rangeMode=\'all\';range=[0,meta.span];$(\'query\').value=\'\';$(\'proc\').value=\'\';choose(r.id)};render();\n\nfunction chartX(e){const chart=$(\'chart\'),matrix=chart.getScreenCTM();if(!matrix)return 30;const point=chart.createSVGPoint();point.x=e.clientX;point.y=e.clientY;return Math.max(30,Math.min(1190,point.matrixTransform(matrix.inverse()).x))}\nfunction updateRangeOverlay(preview=null){$(\'range-overlay\')?.remove();const bounds=preview||range,view=chartRange();if(!preview&&bounds[0]===view[0]&&bounds[1]===view[1])return;const box=document.createElementNS(\'http://www.w3.org/2000/svg\',\'rect\');box.id=\'range-overlay\';box.setAttribute(\'x\',chartPosition(bounds[0]));box.setAttribute(\'y\',0);box.setAttribute(\'width\',Math.max(1,(bounds[1]-bounds[0])/(view[1]-view[0])*1160));box.setAttribute(\'height\',150);box.setAttribute(\'fill\',\'#2274cf\');box.setAttribute(\'fill-opacity\',\'.15\');box.setAttribute(\'stroke\',\'#2274cf\');box.style.pointerEvents=\'none\';$(\'chart\').append(box)}\n$(\'chart\').onpointerdown=e=>{if(e.button!==0)return;suppressChartClick=false;chartDrag={x:chartX(e),moved:false,bounds:[...chartRange()]};$(\'chart\').setPointerCapture(e.pointerId)};\n$(\'chart\').onpointermove=e=>{if(!chartDrag)return;const x=chartX(e);if(Math.abs(x-chartDrag.x)>5)chartDrag.moved=true;if(chartDrag.moved)updateRangeOverlay([chartTime(Math.min(x,chartDrag.x),chartDrag.bounds),chartTime(Math.max(x,chartDrag.x),chartDrag.bounds)])};\n$(\'chart\').onpointerup=e=>{if(!chartDrag)return;const x=chartX(e);if(chartDrag.moved&&Math.abs(x-chartDrag.x)>5){range=[chartTime(Math.min(x,chartDrag.x),chartDrag.bounds),chartTime(Math.max(x,chartDrag.x),chartDrag.bounds)];rangeMode=\'custom\';suppressChartClick=true;render();$(\'scroll\').scrollTop=0}chartDrag=null;updateRangeOverlay()};\n$(\'chart\').onpointercancel=()=>{chartDrag=null;updateRangeOverlay()};\n</script></html>'
def method(s):return re.sub(r'/\d+$','',s.strip().split('->')[-1])
START=time.monotonic()
STATE={'stage':'Запуск','detail':''}
def progress(stage,detail=''):
 STATE.update(stage=stage,detail=detail)
 print(f"[{time.monotonic()-START:7.1f} с] {stage}: {detail}",flush=True)
def heartbeat(stop):
 while not stop.wait(5):progress(STATE['stage'],STATE['detail'])
def main():
 ap=argparse.ArgumentParser(description='Иерархический каскад Saby logs + HAR')
 ap.add_argument('folder',nargs='?',default=str(Path(__file__).resolve().parent));ap.add_argument('--output',default='log_report.html');ap.add_argument('--recursive',action='store_true');ap.add_argument('--serve',action='store_true');ap.add_argument('--long-task-ms',type=int,default=100)
 a=ap.parse_args();folder=Path(a.folder).resolve();
 if not folder.is_dir():ap.error('Папка логов не существует: '+str(folder))
 progress('Поиск логов',str(folder));files=sorted(p for p in (folder.rglob('*.log') if a.recursive else folder.glob('*.log')) if re.search(r'(?:-|_)events(?:_\d+)?\.log$',p.name))
 progress('Найдены файлы',f'{len(files)} шт.; {sum(p.stat().st_size for p in files)/1048576:.1f} МБ')
 if not files:ap.error('Не найдены *events.log')
 nodes=[];edges={};async_traces=set();errors=[];log_start=None;log_end=None
 def add(process,trace,root,name,start,end,kind,file,line,thread='',visible=False):
  if end<start:return
  nodes.append(dict(process=process,trace=trace,root=root,name=method(name),start=start,end=end,duration=end-start,kind=kind,file=file,line=line,thread=thread,visible=visible,parent=None))
 for file_index,p in enumerate(files,1):
  progress('Чтение',f'{file_index}/{len(files)} · {p.name} · {p.stat().st_size/1048576:.1f} МБ');file_size=p.stat().st_size;read_bytes=0;last_progress=time.monotonic()
  process=re.sub(r'^\d{4}-\d{2}-\d{2}_','',p.name).removesuffix('-events.log');process=re.sub(r'(?:-|_)events(?:_\d+)?\.log$','',process);process='Launcher' if re.fullmatch(r'events(?:_\d+)?\.log',process) else process
  dm=re.search(r'\d{4}-\d{2}-\d{2}',p.name);day=datetime.date.fromisoformat(dm[0]).toordinal()*86400000 if dm else 0;last=0;pending={}
  for ln,l in enumerate(p.open(encoding='utf-8-sig',errors='replace'),1):
   read_bytes+=len(l.encode('utf-8'))
   if time.monotonic()-last_progress>=2:
    progress('Чтение',f'{file_index}/{len(files)} · {p.name} · ~{min(100,read_bytes/max(1,file_size)*100):.0f}% · строк {ln:,} · операций {len(nodes):,}');last_progress=time.monotonic()
   tm=re.match(r'(\d\d):(\d\d):(\d\d)\.(\d{3})',l)
   if not tm:continue
   h,m,s,ms=map(int,tm.groups());raw=((h*60+m)*60+s)*1000+ms
   if last-raw>43200000:day+=86400000
   last=raw;t=day+raw;log_start=t if log_start is None else min(log_start,t);log_end=t if log_end is None else max(log_end,t);c=l.rstrip().split('\t');msg=c[-1];thread=c[1] if len(c)>1 else ''
   trace=c[4] if len(c)>5 else '';root=c[5] if len(c)>9 else trace;ctx=c[8] if len(c)>9 else c[5] if len(c)>5 else ''
   child=re.search(r'\bruuid:([\w-]+)',msg)
   if child and '[async call]' in msg:async_traces.add(child[1])
   if child and ('[async call]' in msg or '[rpc call][start]' in msg):edges[child[1]]=(trace,t)
   key=(thread,trace)
   if '[w][start]' in msg:pending[key]=(t,ctx,ln)
   d=re.search(r'\[exec_period\]\s+(\d+)',msg)
   if not d:continue
   dur=int(d[1]);start=t-dur;end=t;name='';kind=''
   if '[w][finish]' in msg:
    st=pending.pop(key,None);start=st[0] if st else start;name=ctx;kind='БЛ'
   elif '[rpc call][finish]' in msg:
    # A receiving local w interval represents this same call; reconcile below.
    name=msg.split('[rpc call][finish]',1)[1].split(' ruuid:',1)[0].strip();kind='RPC';trace=child[1] if child else trace
   elif '[m][finish]' in msg:name=msg.split('[m][finish]',1)[1].split('[exec_period]',1)[0].strip();kind='Метод'
   elif '[event][hdl][finish]' in msg:name=msg.split('[event][hdl][finish]',1)[1].split('[exec_period]',1)[0].strip();kind='Обработчик'
   elif '[sql][finish]' in msg:name='SQL · '+method(ctx);kind='SQL'
   elif 'Waiting for the GIL' in msg or 'waiting for future' in msg:
    name=msg.split('[exec_period]',1)[0].strip();kind='Длинная задача';start=t;end=t+dur
   if name:add(process,trace,root,name,start,end,kind,str(p.relative_to(folder)),ln,thread)
  for (thread,trace),(start,name,ln) in pending.items():
   add(process,trace,trace,name,start,start,'Незавершённый вызов',str(p.relative_to(folder)),ln,thread)
 progress('Сопоставление вызовов',f'{len(nodes):,} операций')
 # Prefer actual receiving RPC over its caller-side representation.
 receivers={(n['trace'],n['name']) for n in nodes if n['kind']=='БЛ'}
 nodes=[n for n in nodes if not(n['kind']=='RPC' and (n['trace'],n['name']) in receivers)]
 # Invoke records establish request provenance; explicitly asynchronous requests stay background.
 invokefiles=sorted(p for p in (folder.rglob('*.log') if a.recursive else folder.glob('*.log')) if re.search(r'(?:-|_)invoke(?:_\d+)?\.log$',p.name))
 invoked=set();response_nodes={}
 for n in nodes:
  if n['trace']:response_nodes.setdefault((n['trace'],n['name']),[]).append(n)
 def set_payload(n,text,source,field):
  valid=True
  try:
   data=json.loads(text)
   if isinstance(data,list) and len(data)==1 and isinstance(data[0],dict) and 'jsonrpc' in data[0]:data=data[0]
   if isinstance(data,dict) and 'jsonrpc' in data:
    data=data.get('params',data) if field=='params' else {'error':data['error']} if 'error' in data else data.get('result',data)
   compact=json.dumps(data,ensure_ascii=False,separators=(',',':'));text=json.dumps(data,ensure_ascii=False,indent=2)
  except (ValueError,TypeError):valid=False;compact=text
  is_events=bool(re.search(r'(?:-|_)events(?:_\d+)?\.log:',source));score=(valid,is_events,len(compact))
  old=n.get(field)
  if old is not None:
   try:oldscore=(True,bool(re.search(r'(?:-|_)events(?:_\d+)?\.log:',n.get(field+'_source',''))),len(json.dumps(json.loads(old),ensure_ascii=False,separators=(',',':'))))
   except (ValueError,TypeError):oldscore=(False,bool(re.search(r'(?:-|_)events(?:_\d+)?\.log:',n.get(field+'_source',''))),len(old))
   if score<=oldscore:return
  if old is not None:n[field+'_previous_source']=n[field+'_source']
  n[field]=text;n[field+'_source']=source
  if not valid:n[field+'_invalid']=True
  else:n.pop(field+'_invalid',None)
 def set_response(n,text,source):set_payload(n,text,source,'response')
 progress('Чтение invoke',f'{len(invokefiles)} файлов')
 for p in invokefiles:
  progress('Чтение invoke',p.name)
  for response_line,line in enumerate(p.open(encoding='utf-8-sig',errors='replace'),1):
   if '[post request]' not in line and '[response]' not in line:continue
   c=line.rstrip().split('\t')
   if len(c)<=9:continue
   key=(c[4],method(c[8]))
   if '[post request]' in line:invoked.add(key)
   if key[0]:
    candidates=[n for n in response_nodes.get(key,[]) if Path(n['file']).parent==p.relative_to(folder).parent and re.sub(r'(?:-|_)events(?:_\d+)?\.log$','',Path(n['file']).name)==re.sub(r'(?:-|_)invoke(?:_\d+)?\.log$','',p.name)]
    if len(candidates)==1:
     field,marker=('params','[post request]') if '[post request]' in line else ('response','[response]')
     set_payload(candidates[0],line.split(marker,1)[1].strip(),str(p.relative_to(folder))+':'+str(response_line),field)
 for n in nodes:
  if (n['trace'],n['name']) in invoked and n['trace'] not in async_traces:
   n['visible']=True;n['provenance']='Запрос зарегистрирован в invoke; явного async-запуска в прочитанных логах нет'
 # HAR timestamps use local wall-clock time, matching local log timestamps.
 harfiles=sorted(folder.rglob('*.har') if a.recursive else folder.glob('*.har'));harcount=0
 progress('Чтение HAR',f'{len(harfiles)} файлов')
 for p in harfiles:
  progress('Чтение HAR',p.name)
  try:
   entries=json.loads(p.read_text(encoding='utf-8-sig'))['log']['entries']
   for e in entries:
    req=e.get('request',{});body=req.get('postData',{}).get('text','')
    try:payload=json.loads(body)
    except (ValueError,TypeError):continue
    calls=payload if isinstance(payload,list) else [payload]
    for call in calls:
     if not isinstance(call,dict) or not call.get('method'):continue
     name=method(call['method']);dt=datetime.datetime.fromisoformat(e['startedDateTime'].replace('Z','+00:00')).astimezone();start=dt.date().toordinal()*86400000+((dt.hour*60+dt.minute)*60+dt.second)*1000+dt.microsecond/1000;end=start+max(0,e.get('time',0));harcount+=1
     candidates=[n for n in nodes if n['name']==name and n['kind']=='БЛ' and abs(n['start']-start)<2000 and n['end']>=start-100]
     if candidates:
      n=min(candidates,key=lambda n:abs(n['start']-start));n['visible']=True;n['har']=p.name
     else:
      add('UI / HAR','har:'+str(harcount),'',name,start,end,'HAR',p.name,0,visible=True);n=nodes[-1]
     if 'params' in call:set_payload(n,json.dumps(call['params'],ensure_ascii=False),p.name+' · HAR request','params')
     content=e.get('response',{}).get('content',{});text=content.get('text')
     if text is not None:
      if content.get('encoding')=='base64':text=base64.b64decode(text).decode('utf-8',errors='replace')
      if len(calls)==1:set_response(n,text,p.name+' · HAR response')
      else:
       try:
        batch=json.loads(text);matches=[item for item in batch if isinstance(item,dict) and 'id' in call and item.get('id')==call['id']]
        if len(matches)==1:set_response(n,json.dumps(matches[0],ensure_ascii=False),p.name+' · HAR response')
       except (ValueError,TypeError):pass
  except Exception as exc:errors.append(p.name+': '+str(exc))
 ui_error_records=[]
 # Selected browser console milestones are point events, not method durations.
 consolefiles=sorted(p for p in (folder.rglob('*.log') if a.recursive else folder.glob('*.log')) if re.search(r'(?:-|_)UI-console(?:_\d+)?\.log$',p.name,re.I))
 keys_candidates=[folder/'UI-console-keys',Path(os.environ.get('SABY_REPORT_SELF',__file__)).resolve().parent/'UI-console-keys',Path(__file__).resolve().parent/'UI-console-keys']
 keys_file=next((path for path in keys_candidates if path.is_file()),None)
 default_keys=['RetailCore/page:','Инициализация оффлайн приложения','Выход из системы','SyncManager:','applicationId:','Состояние лицензий:','Синхронизируемся','StoreStrategy:','Уведомление:','Состояние памяти:','SyncDialog:','Состояние фичи','id раздела:']
 console_keys=[line.strip().casefold() for line in (keys_file.read_text(encoding='utf-8-sig').splitlines() if keys_file else default_keys) if line.strip() and not line.lstrip().startswith('#')]
 ignore_candidates=[folder/'UI-console-ignore',Path(os.environ.get('SABY_REPORT_SELF',__file__)).resolve().parent/'UI-console-ignore',Path(__file__).resolve().parent/'UI-console-ignore']
 ignore_file=next((path for path in ignore_candidates if path.is_file()),None)
 console_ignore=[line.strip().casefold() for line in (ignore_file.read_text(encoding='utf-8-sig').splitlines() if ignore_file else ['подписка','Подписались']) if line.strip() and not line.lstrip().startswith('#')]
 progress('Чтение UI-console',str(len(consolefiles))+' файлов')
 for consolefile in consolefiles:
  relative=str(consolefile.relative_to(folder));dm=re.search(r'\d{4}-\d{2}-\d{2}',consolefile.name);day=datetime.date.fromisoformat(dm[0]).toordinal()*86400000 if dm else 0;previous=0;record=None
  def save_console(record):
   if record is None:return
   t,line_number,text,is_error=record
   text=re.sub(r'\s*\((?:resources/|https?://|file:)[^\r\n]*?:\d+(?::\d+)?\)\s*$','',text.strip())
   if is_error:
    add('UI-console','console-error:'+relative+':'+str(line_number),'',text,t,t,'Ошибка UI',relative,line_number,visible=True)
    target=nodes[-1];target['name']=text;target['has_error']=True;target['call_errors']=[dict(time=t,file=relative,line=line_number,message=text)]
    ui_error_records.append(dict(time=t,file=relative,line=line_number,message=text,target=target,label='UI-error'))
    return
   if any(key in text.casefold() for key in console_ignore):return
   if not any(key in text.casefold() for key in console_keys):return
   add('UI-console','console:'+relative+':'+str(line_number),'',text,t,t,'Консоль UI',relative,line_number,visible=True)
   nodes[-1]['name']=text
   section=re.search(r'id\s+раздела:\s*([^\s,;]+)',text,re.I)
   if section:nodes[-1]['console_marker']=dict(label=section[1],type='section')
   if 'инициализация оффлайн приложения' in text.casefold():nodes[-1]['console_marker']=dict(label='Инициализация оффлайн приложения',type='initialization')
  with consolefile.open(encoding='utf-8-sig',errors='replace') as stream:
   for ln,line in enumerate(stream,1):
    tm=re.match(r'(\d\d):(\d\d):(\d\d)\.(\d{3})',line)
    if not tm:
     if record:record[-1]+=line
     continue
    save_console(record);record=None;h,m,sec,ms=map(int,tm.groups());raw=((h*60+m)*60+sec)*1000+ms
    if previous-raw>43200000:day+=86400000
    previous=raw;log_start=day+raw if log_start is None else min(log_start,day+raw);log_end=day+raw if log_end is None else max(log_end,day+raw)
    # Both tab-separated and whitespace-aligned browser console records occur.
    payload=re.split(r'\[(?:INFO|WARNING|WARN|ERROR|DEBUG|LOG|TRACE)\]\s*',line,maxsplit=1,flags=re.I)
    if len(payload)==2:text=payload[1]
    else:
     columns=line.rstrip().split('\t')
     if len(columns)<8:continue
     text='\t'.join(columns[7:])
    record=[day+raw,ln,text,bool(re.search(r'\[ERROR\]',line,re.I))]
   save_console(record)
 # Error logs are small and read once; preserve multiline exception messages.
 error_records=ui_error_records;error_index={}
 for node in nodes:
  if node['trace']:error_index.setdefault(node['trace'],[]).append(node)
 errorfiles=sorted(p for p in (folder.rglob('*.log') if a.recursive else folder.glob('*.log')) if re.search(r'(?:-|_)errors(?:_\d+)?\.log$',p.name,re.I))
 progress('Чтение errors',str(len(errorfiles))+' файлов')
 for errorfile in errorfiles:
  relative=str(errorfile.relative_to(folder));prefix=re.sub(r'(?:-|_)errors(?:_\d+)?\.log$','',errorfile.name,flags=re.I)
  process=re.sub(r'^\d{4}-\d{2}-\d{2}_?','',prefix) or 'Launcher'
  dm=re.search(r'\d{4}-\d{2}-\d{2}',errorfile.name);day=datetime.date.fromisoformat(dm[0]).toordinal()*86400000 if dm else 0
  previous=0;current=None
  def save_error(record):
   if record is None:return
   t,trace,ctx,thread,line_number,message=record
   candidates=[node for node in error_index.get(trace,[]) if trace and node['process']==process and Path(node['file']).parent==Path(relative).parent and (not ctx or node['name']==method(ctx)) and node['start']-100<=t<=node['end']+100]
   if not candidates and not trace:
    candidates=[node for node in nodes if node['process']==process and node['thread']==thread and Path(node['file']).parent==Path(relative).parent and node['start']<=t<=node['end'] and (not ctx or node['name']==method(ctx))]
   target=min(candidates,key=lambda node:node['duration']) if candidates else None
   detail=dict(time=t,file=relative,line=line_number,message=message.strip())
   if target is None:
    add(process,trace,trace,method(ctx) if ctx else 'Ошибка · '+message.splitlines()[0][:160],t,t,'Ошибка',relative,line_number,thread,visible=True);target=nodes[-1]
   target.setdefault('call_errors',[]).append(detail.copy());target['has_error']=True
   error_records.append(dict(time=t,file=relative,line=line_number,message=message.strip(),target=target))
  with errorfile.open(encoding='utf-8-sig',errors='replace') as stream:
   for ln,line in enumerate(stream,1):
    tm=re.match(r'(\d\d):(\d\d):(\d\d)\.(\d{3})',line)
    if not tm:
     if current:current[-1]+=line
     continue
    save_error(current);h,m,sec,ms=map(int,tm.groups());raw=((h*60+m)*60+sec)*1000+ms
    if previous-raw>43200000:day+=86400000
    previous=raw;log_start=day+raw if log_start is None else min(log_start,day+raw);log_end=day+raw if log_end is None else max(log_end,day+raw);c=line.rstrip().split('\t');trace=c[4] if len(c)>6 else '';ctx=c[8] if len(c)>9 else c[5] if len(c)>6 else '';thread=c[1] if len(c)>1 else ''
    current=[day+raw,trace,ctx,thread,ln,c[-1]+'\n']
   save_error(current)
 progress('Построение дерева',f'{len(nodes):,} операций; поиск инициаторов')
 # Build initiator tree: explicit trace edges first, then tight containment in the same trace/thread.
 nodes.sort(key=lambda n:(n['start'],-n['duration']));bytrace={}
 for i,n in enumerate(nodes):n['id']=i;bytrace.setdefault(n['trace'],[]).append(i)
 for i,n in enumerate(nodes):
  if i%2000==0:STATE['detail']=f'{i:,}/{len(nodes):,} операций'
  candidates=[j for j in bytrace.get(n['trace'],[]) if j!=i and nodes[j]['process']==n['process'] and nodes[j]['start']<=n['start'] and nodes[j]['end']>=n['end'] and (nodes[j]['duration']>n['duration'] or j<i) and nodes[j]['kind'] not in ('Длинная задача','SQL')]
  if candidates:n['parent']=min(candidates,key=lambda j:nodes[j]['duration']);n['relation']='Вложенность по trace и интервалу'
  elif n['trace'] in edges:
   parenttrace,launch=edges[n['trace']];candidates=[j for j in bytrace.get(parenttrace,[]) if j!=i and nodes[j]['start']<=launch<=nodes[j]['end'] and nodes[j]['kind'] not in ('Длинная задача','SQL')]
   if candidates:n['parent']=min(candidates,key=lambda j:nodes[j]['duration']);n['relation']='Инициатор по ruuid'
 progress('Проверка дерева',f'{len(nodes):,} операций')
 # Guard cycles from malformed or ambiguous logs.
 for n in nodes:
  seen={n['id']};p=n['parent']
  while p is not None:
   if p in seen:n['parent']=None;break
   seen.add(p);p=nodes[p]['parent']
 base=min([n['start'] for n in nodes]+([log_start] if log_start is not None else [0]));end=max([n['end'] for n in nodes]+([log_end] if log_end is not None else [base+1]))
 for n in nodes:
  n['log_time']=f"{int(n['start']//3600000)%24:02}:{int(n['start']//60000)%60:02}:{int(n['start']//1000)%60:02}.{int(n['start'])%1000:03}"
  n['start']-=base;n['end']-=base
  for error in n.get('call_errors',[]):error['time']-=base
  n['appearance']='ui' if n['visible'] else 'background' if harfiles else 'log-only'
 meta=dict(span=max(1,end-base),files=len(files),har=len(harfiles),count=len(nodes),errors=errors,source=str(folder),origin=datetime.datetime.fromordinal(int(base//86400000)).strftime('%Y-%m-%d')+' '+f'{int(base//3600000)%24:02}:{int(base//60000)%60:02}:{int(base//1000)%60:02}',originMs=base- datetime.date(1970,1,1).toordinal()*86400000,logStart=datetime.datetime.fromordinal(int(base//86400000)).strftime('%Y-%m-%d')+' '+f'{int(base//3600000)%24:02}:{int(base//60000)%60:02}:{int(base//1000)%60:02}.{int(base)%1000:03}',logEnd=datetime.datetime.fromordinal(int(end//86400000)).strftime('%Y-%m-%d')+' '+f'{int(end//3600000)%24:02}:{int(end//60000)%60:02}:{int(end//1000)%60:02}.{int(end)%1000:03}',threshold=a.long_task_ms,console_markers=[dict(time=n['start'],node=n['id'],**n['console_marker']) for n in nodes if 'console_marker' in n],error_markers=[dict(time=e['time']-base,node=e['target']['id'],file=e['file'],line=e['line'],message=e['message'],label=e.get('label','error')) for e in error_records])
 progress('Создание HTML',f'{len(nodes):,} операций')
 page=HTML.replace('__THRESHOLD__',str(a.long_task_ms)).replace('__DATA__',json.dumps(nodes,ensure_ascii=False).replace('</','<\\/')).replace('__META__',json.dumps(meta,ensure_ascii=False).replace('</','<\\/'));out=folder/a.output;out.write_text(page,encoding='utf-8');print(f'Files: {len(files)}; operations: {len(nodes)}; roots: {sum(n["parent"] is None for n in nodes)}; report: {out}')
 progress('Готово',str(out))
 if a.serve:
  progress('Открытие отчёта','Локальный HTTP-сервер; адрес откроется в браузере')
  code="""import http.server,functools,sys,threading,webbrowser
from urllib.parse import quote
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=sys.argv[1]))
threading.Timer(.5,lambda:webbrowser.open('http://127.0.0.1:'+str(s.server_port)+'/'+quote(sys.argv[2]))).start()
threading.Timer(7200,s.shutdown).start()
s.serve_forever()
s.server_close()
"""
  subprocess.Popen([sys.executable,'-c',code,str(out.parent),out.name],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
if __name__=='__main__':
 stop=threading.Event();threading.Thread(target=heartbeat,args=(stop,),daemon=True).start()
 try:main()
 except KeyboardInterrupt:progress('Остановлено','Пользователь нажал Ctrl+C');sys.exit(130)
 except Exception:
  progress('Ошибка','Подробности ниже');traceback.print_exc();sys.exit(1)
 finally:stop.set()
