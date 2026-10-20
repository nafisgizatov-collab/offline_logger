#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saby timeline: Python 3.9+, no dependencies."""
import argparse,json,re,datetime,subprocess,sys,time,threading,traceback,base64,os
from pathlib import Path
HTML = (
 '<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>\u041e\u0442\u0447\u0435\u0442 \u043f\u043e \u043b\u043e\u0433\u0430\u043c \u043e\u0444\u0444\u043b\u0430\u0439\u043d</title><style>\n*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:#21354c;font:12px system-ui,Arial}main{padding:26px;max-width:1800px;margin:auto}h1{margin:0;font-size:28px}.sub{color:#708196;line-height:1.6}.panel{background:white;border:1px solid #dce5ee;border-radius:12px;padding:18px;margin:18px 0}.toolbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap}button,input,select{border:1px solid #cdd9e5;background:white;border-radius:6px;padding:8px;color:inherit}button{cursor:pointer}button.active,input.active,select.active{border-color:#2274cf;background:#e7f2ff;color:#1456a0}button.active{background:#2274cf;color:white}#chart{width:100%;height:150px;cursor:crosshair;display:block;touch-action:none}.scroll{height:calc(66vh + 150px);min-height:240px;overflow:auto;resize:vertical}table{width:100%;border-collapse:separate;border-spacing:0;table-layout:fixed}th{position:sticky;top:0;background:#edf3f9;z-index:2;text-align:left;padding:12px}td{padding:10px;border-bottom:1px solid #edf1f5;vertical-align:middle}th:first-child{width:39%}th:nth-child(2){width:45%}th:last-child{width:16%}.name{overflow-wrap:anywhere}.name.background,.name.log-only{color:#7b8796;font-style:italic}.branch{display:flex;align-items:center;gap:6px}.toggle{padding:0;width:22px;height:22px;flex-shrink:0}.leaf{width:22px;flex-shrink:0}.track{'
 'height:24px;position:relative;background:repeating-linear-gradient(to right,#f6f9fc 0,#f6f9fc calc(10% - 1px),#e4ebf3 calc(10% - 1px),#e4ebf3 10%)}.bar{position:absolute;top:5px;height:14px;min-width:2px;border-radius:3px;border-left:2px solid #183d60;border-right:2px solid #183d60}.small{font-size:11px;color:#8291a3}.selected td{border-top:2px solid #2581df;border-bottom:2px solid #2581df;background:#eff7ff}.selected td:first-child{border-left:2px solid #2581df}.selected td:last-child{border-right:2px solid #2581df}#details,#response,#params{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.7 Consolas,monospace}.legend{display:flex;gap:15px;flex-wrap:wrap;font-size:12px;margin:10px 0}.dot{display:inline-block;width:10px;height:10px;margin-right:5px;border-radius:2px}.axis{display:flex;justify-content:space-between;font-size:11px;font-weight:400}.hint{padding:8px 0;color:#60758d}#status{font-weight:600}.dur{font-variant-numeric:tabular-nums}\n .call-details{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,1fr);gap:24px}#response,#params{max-height:650px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere}@media(max-width:800px){.call-details{grid-template-columns:1fr}} .name.has-error,.has-error td.dur{color:#cc2435!important}.error-marker{cursor:pointer} .errors-hidden .error-marker{display:none} .name.console-event{color:#245b92;font-weight:600;font-style:normal} .filter-panel{display:flex;flex-direction:column;gap:12px}.filter-checkboxes{b'
 'order-top:1px solid #edf1f5;padding-top:10px}.filter-checkboxes label{display:inline-flex;align-items:center;gap:5px;white-space:nowrap} .report-heading{display:flex;align-items:baseline;gap:20px;flex-wrap:wrap}.report-heading h1,.report-heading #logPeriod{font:700 28px system-ui,Arial;color:inherit} .console-marker{cursor:pointer} .cloud-call{display:inline-flex;vertical-align:middle;margin-left:5px;width:15px;height:15px;color:#176aca}.cloud-call svg{width:15px;height:15px;display:block}</style><main><div class="report-heading"><h1>\u041e\u0442\u0447\u0435\u0442 \u043f\u043e \u043b\u043e\u0433\u0430\u043c \u043e\u0444\u0444\u043b\u0430\u0439\u043d</h1><span id="logPeriod"></span></div><div class="sub" id="subtitle"></div><div class="panel"><b>\u0410\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u044c \u0432\u043e \u0432\u0441\u0451\u043c \u0436\u0443\u0440\u043d\u0430\u043b\u0435</b><div class="hint">\u0412\u044b\u0434\u0435\u043b\u0438\u0442\u0435 \u0443\u0447\u0430\u0441\u0442\u043e\u043a \u043c\u044b\u0448\u044c\u044e, \u0447\u0442\u043e\u0431\u044b \u043e\u0442\u0444\u0438\u043b\u044c\u0442\u0440\u043e\u0432\u0430\u0442\u044c \u0436\u0443\u0440\u043d\u0430\u043b. \xab\u0412\u0435\u0441\u044c \u0436\u0443\u0440\u043d\u0430\u043b\xbb \u0441\u0431\u0440\u0430\u0441\u044b\u0432\u0430\u0435\u0442 \u0434\u0438\u0430\u043f\u0430\u0437\u043e\u043d. \u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u043d\u0430 \u043f\u0438\u043a: \u043a\u0430\u0441\u043a\u0430\u0434 \u043f\u0435\u0440\u0435\u0439\u0434\u0451\u0442 \u043a \u0430\u043a\u0442\u0438\u0432\u043d\u043e\u043c\u0443 \u0432\u044b\u0437\u043e\u0432\u0443 \u0438 \u0432\u044b\u0434\u0435\u043b\u0438\u0442 \u0435\u0433\u043e \u0440\u0430\u043c\u043a\u043e\u0439. \u0412\u044b\u0441\u043e\u0442\u0430 \u2014 \u0447\u0438\u0441\u043b\u043e \u043e\u0434\u043d\u043e\u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u044e\u0449\u0438\u0445\u0441\u044f \u043c\u0435\u0442\u043e\u0434\u043e\u0432 \u0411\u041b/RPC, \u0432\u043a\u043b\u044e\u0447\u0430\u044f \u043e\u0436\u0438\u0434\u0430\u043d\u0438\u044f; \u044d\u0442\u043e \u043d\u0435 \u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0430 CPU. \u0421\u0435\u0440\u044b\u0435 \u0441\u0435\u0440\u0438\u0438 \u0441 \u0441\u0443\u0444\u0444\u0438\u043a\u0441\u043e\u043c -background \u2014 \u0432\u044b\u0437\u043e\u0432\u044b \u0431\u0435\u0437 \u043d\u0430\u0439\u0434\u0435\u043d\u043d\u043e\u0433\u043e UI-\u0438\u043d\u0438\u0446\u0438\u0430\u0442\u043e\u0440\u0430 \u0432 \u0446\u0435\u043f\u043e\u0447\u043a\u0435 \u0440\u043e\u0434\u0438\u0442\u0435\u043b\u0435\u0439; \u043f\u0440\u0438 \u043d\u0435\u043f\u043e\u043b\u043d\u044b\u0445 \u043b\u043e\u0433\u0430\u0445 \u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a \u043c\u043e\u0436\u0435\u0442 \u0431\u044b\u0442\u044c \u043d\u0435\u0438\u0437\u0432\u0435\u0441\u0442\u0435\u043d.</div><div id="legend" class="legend"></div><svg id="chart" viewBox="0 0 1200 150"></svg><div id="chartaxis" class="axis"></div><div id="fpsPanel" hidden style="margin-top:18px;border-top:1px solid #dce5ee;padding-top:12px"><strong>FPS \xb7 0\u201364</strong><svg id="fpsChart" viewBox="0 0 1200 124" style="display:block;width:100%;height:124px" aria-label="FPS \u043f\u043e \u0432\u0440\u0435\u043c\u0435\u043d\u0438"></svg><div id="fpsAxis" class="axis"></div></div></div>\n<div class="panel filter-panel"><div class="toolbar filter-controls"><button id="all" class="active">\u0412\u0435\u0441\u044c \u0436\u0443\u0440\u043d\u0430\u043b</button><button id="near">\u041e\u043a\u043d\u043e \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0433\u043e \u0432\u044b\u0437\u043e\u0432\u0430</button><button id="period" title="\u0420\u0430\u0441\u0442\u044f\u043d\u0443\u0442\u044c \u0432\u044b\u0434\u0435\u043b\u0435\u043d\u043d\u044b\u0439 \u043f\u0435\u0440\u0438\u043e\u0434 \u043d\u0430 \u0432\u0441\u044e \u0448\u0438\u0440\u0438\u043d\u0443 \u0432\u0435\u0440\u0445\u043d\u0435\u0433\u043e \u0442\u0430\u0439\u043c\u043b\u0430\u0439\u043d\u0430">\u0412\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0439 \u043f\u0435\u0440\u0438\u043e\u0434</button><label title="\u041e\u0442\u0441\u0442\u0443\u043f \u0434\u043e \u043d\u0430\u0447\u0430\u043b\u0430 \u0438 \u043f\u043e\u0441\u043b\u0435 \u043a\u043e\u043d\u0446\u0430 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0433\u043e \u0432\u044b\u0437\u043e\u0432\u0430"><input id="windowMs" '
 'type="number" value="1000" min="0" step="100" style="width:90px" aria-label="\u041e\u0442\u0441\u0442\u0443\u043f \u043e\u043a\u043d\u0430 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0433\u043e \u0432\u044b\u0437\u043e\u0432\u0430 \u0432 \u043c\u0438\u043b\u043b\u0438\u0441\u0435\u043a\u0443\u043d\u0434\u0430\u0445"> \u043c\u0441</label><button id="collapse">\u0421\u0432\u0435\u0440\u043d\u0443\u0442\u044c \u0432\u0441\u0451</button><button id="expand">\u0420\u0430\u0437\u0432\u0435\u0440\u043d\u0443\u0442\u044c \u0432\u0441\u0451</button><input id="query" list="methodSuggestions" autocomplete="off" placeholder="\u041d\u0430\u0439\u0442\u0438 \u043c\u0435\u0442\u043e\u0434 \u0438 \u0435\u0433\u043e \u0432\u043b\u043e\u0436\u0435\u043d\u043d\u043e\u0441\u0442\u044c" style="min-width:300px"><datalist id="methodSuggestions"></datalist><button id="clearQuery" title="\u0441\u0431\u0440\u043e\u0441 \u043f\u043e\u0438\u0441\u043a\u0430" aria-label="\u0441\u0431\u0440\u043e\u0441 \u043f\u043e\u0438\u0441\u043a\u0430" style="width:34px;height:34px;padding:0;font-size:20px;flex-shrink:0">\xd7</button><select id="proc"><option value="">\u0412\u0441\u0435 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u044b</option></select><select id="callType" aria-label="\u0422\u0438\u043f \u0432\u044b\u0437\u043e\u0432\u043e\u0432"><option value="all">\u041b\u043e\u043a\u0430\u043b\u044c\u043d\u044b\u0435 \u0438 \u043e\u0431\u043b\u0430\u0447\u043d\u044b\u0435 \u0432\u044b\u0437\u043e\u0432\u044b</option><option value="local">\u0422\u043e\u043b\u044c\u043a\u043e \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u044b\u0435 \u0432\u044b\u0437\u043e\u0432\u044b</option><option value="cloud">\u0422\u043e\u043b\u044c\u043a\u043e \u043e\u0431\u043b\u0430\u0447\u043d\u044b\u0435 \u0432\u044b\u0437\u043e\u0432\u044b</option></select><select id="showErrors" aria-label="\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u043e\u0448\u0438\u0431\u043e\u043a"><option value="show">\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043e\u0448\u0438\u0431\u043a\u0438</option><option value="hide">\u041d\u0435 \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043e\u0448\u0438\u0431\u043a\u0438</option><option value="only">\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0442\u043e\u043b\u044c\u043a\u043e \u043e\u0448\u0438\u0431\u043a\u0438</option></select><select id="showFps" aria-label="\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 FPS" hidden><option value="show">\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c FPS</option><option value="hide">\u041d\u0435 \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c FPS</option></select><label>\u0414\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u0432\u0435\u0440\u0445\u043d\u0435\u0433\u043e \u0443\u0440\u043e\u0432\u043d\u044f \u043e\u0442 <input id="min" type="number" value="__THRESHOLD__" min="0" style="width:75px"> \u043c\u0441</label><button id="sort">\u041f\u043e \u043d\u0430\u0447\u0430\u043b\u0443 \u2193</button><button id="resetBlacklist" hidden>\u0421\u0431\u0440\u043e\u0441\u0438\u0442\u044c \u0427\u0421</button><span id="status"></span></div><div class="toolbar filter-checkboxes"><label id="visibleLabel" title="\u0421\u043d\u0438\u043c\u0438\u0442\u0435 \u043e\u0442\u043c\u0435\u0442\u043a\u0443, \u0447\u0442\u043e\u0431\u044b \u043f\u043e\u043a\u0430\u0437\u0430\u0442\u044c \u0432\u0441\u0435 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u044b" style="padding:7px;border-radius:6px"><input id="visibleOnly" type="checkbox" checke'
 'd> \u0422\u043e\u043b\u044c\u043a\u043e \u0432\u0438\u0434\u0438\u043c\u044b\u0435 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u044b</label><label style="padding:7px;border-radius:6px" id="diagnosticsLabel"><input id="showDiagnostics" type="checkbox"> \u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c \u043e\u0436\u0438\u0434\u0430\u043d\u0438\u044f \u0438 SQL</label><label id="consoleLabel"><input id="showConsole" type="checkbox" checked> \u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043b\u043e\u0433\u0438 UI-console</label></div></div>\n<div class="sub">\u041e\u0431\u044b\u0447\u043d\u044b\u0439 \u0448\u0440\u0438\u0444\u0442 \u2014 \u0437\u0430\u043f\u0440\u043e\u0441\u044b \u0438\u0437 HAR \u0438\u043b\u0438 invoke \u0431\u0435\u0437 \u044f\u0432\u043d\u043e\u0433\u043e \u0430\u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u043e\u0433\u043e \u0437\u0430\u043f\u0443\u0441\u043a\u0430. \u0421\u0435\u0440\u044b\u0439 \u043a\u0443\u0440\u0441\u0438\u0432 \u2014 \u043e\u0441\u0442\u0430\u043b\u044c\u043d\u044b\u0435 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0438 \u0438\u0437 events.log. Invoke \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0435\u0442 \u0437\u0430\u043f\u0440\u043e\u0441; \u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a UI \u043f\u0440\u0438 \u043d\u0435\u043f\u043e\u043b\u043d\u044b\u0445 \u043b\u043e\u0433\u0430\u0445 \u043c\u043e\u0436\u0435\u0442 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u0442\u044c \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438. \u0421\u0442\u0440\u0435\u043b\u043a\u0430 \u0440\u0430\u0441\u043a\u0440\u044b\u0432\u0430\u0435\u0442 \u0434\u043e\u0447\u0435\u0440\u043d\u0438\u0435 \u0432\u044b\u0437\u043e\u0432\u044b; \u0434\u043b\u0438\u043d\u043d\u044b\u0435 \u0437\u0430\u0434\u0430\u0447\u0438 \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u044b \u0432\u043d\u0443\u0442\u0440\u0438 \u0438\u043d\u0438\u0446\u0438\u0430\u0442\u043e\u0440\u0430. SQL \u0438 \u043e\u0436\u0438\u0434\u0430\u043d\u0438\u044f \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u044b \u0447\u0435\u0440\u0435\u0437 \u0447\u0435\u043a\u0431\u043e\u043a\u0441 \xab\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c \u043e\u0436\u0438\u0434\u0430\u043d\u0438\u044f \u0438 SQL\xbb. \u0412\u043b\u043e\u0436\u0435\u043d\u043d\u043e\u0441\u0442\u044c \u043f\u043e \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u0438 trace \u2014 \u0440\u0435\u043a\u043e\u043d\u0441\u0442\u0440\u0443\u043a\u0446\u0438\u044f, \u0441\u0432\u044f\u0437\u044c \u043f\u043e ruuid \u2014 \u044f\u0432\u043d\u0430\u044f \u0441\u0432\u044f\u0437\u044c \u0437\u0430\u043f\u0443\u0441\u043a\u0430.</div>\n<div class="panel scroll" id="scroll" title="\u0412\u044b\u0441\u043e\u0442\u0443 \u0441\u043f\u0438\u0441\u043a\u0430 \u043c\u043e\u0436\u043d\u043e \u043c\u0435\u043d\u044f\u0442\u044c: \u043f\u043e\u0442\u044f\u043d\u0438\u0442\u0435 \u043d\u0438\u0436\u043d\u0438\u0439 \u043f\u0440\u0430\u0432\u044b\u0439 \u0443\u0433\u043e\u043b"><div style="display:flex;justify-content:flex-end;margin-bottom:10px"><button id="downloadReport" type="button" title="\u0421\u043a\u0430\u0447\u0430\u0442\u044c \u043e\u0442\u0447\u0435\u0442" aria-label="\u0421\u043a\u0430\u0447\u0430\u0442\u044c \u043e\u0442\u0447\u0435\u0442">\U0001f4be</button></div><table><thead><tr><th>\u041c\u0435\u0442\u043e\u0434 / \u0438\u043d\u0438\u0446\u0438\u0430\u0442\u043e\u0440</th><th><div class="axis" id="axis"></div></th><th>\u0414\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c / \u043d\u0430\u0447\u0430\u043b\u043e</th></tr></thead><tbody id="body"></tbody></table></div><div class="panel call-details"><div><b>\u0412\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0439 \u0432\u044b\u0437\u043e\u0432</b><div id="details">\u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u043d\u0430 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043c\u0435\u0442\u043e\u0434\u0430.</div></div><div><b>\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u0432\u044b\u0437\u043e\u0432\u0430</b><div id="paramsSource" class="small"></div><pre id="params">\u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u043d\u0430 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043c\u0435\u0442\u043e\u0434\u0430.</pre></div><div><b>\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442 \u0432\u044b\u0437\u043e\u0432\u0430</b><div id="responseSour'
 'ce" class="small"></div><pre id="response">\u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u043d\u0430 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043c\u0435\u0442\u043e\u0434\u0430.</pre></div></div></main><script>\nconst rows=__DATA__,meta=__META__,$=id=>document.getElementById(id),esc=s=>String(s).replaceAll(\'&\',\'&amp;\').replaceAll(\'<\',\'&lt;\').replaceAll(\'>\',\'&gt;\').replaceAll(\'"\',\'&quot;\');\nconst children=rows.map(()=>[]),roots=[],expanded=new Set(),collapsed=new Set(),openBranches=new Set(),blacklist=new Set(),palette=[\'#367dba\',\'#9b75bd\',\'#22a58f\',\'#e39c45\',\'#c56c92\',\'#6d8a9a\'];let exportRows=[];let selected=null,range=[0,meta.span],sortDuration=false,rangeMode="all",chartDrag=null,suppressChartClick=false;\nrows.forEach(r=>r.parent===null?roots.push(r.id):children[r.parent].push(r.id));\nconst processes=[...new Set(rows.map(r=>r.process))].sort(),colors=Object.fromEntries(processes.map((p,i)=>[p,palette[i%palette.length]]));\nprocesses.forEach(p=>{const o=document.createElement(\'option\');o.value=p;o.textContent=p;$(\'proc\').append(o)});\n$(\'logPeriod\').textContent=`${meta.logStart||meta.origin} \u2014 ${meta.logEnd||logClock(meta.span,true)}`;\n$(\'subtitle\').textContent=`${meta.files} \u0436\u0443\u0440\u043d\u0430\u043b\u043e\u0432 \xb7 ${meta.count} \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0439 \xb7 ${roots.length} \u0438\u043d\u0438\u0446\u0438\u0430\u0442\u043e\u0440\u043e\u0432 \xb7 HAR: ${meta.har}. ${meta.errors.length?\'\u041e\u0448\u0438\u0431\u043a\u0438 HAR: \'+meta.errors.join(\'; \'):\'\'}`;\nif(meta.mainservice_selection)$(\'subtitle\').textContent+=` MainService-events: \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0435 ${meta.mainservice_selection.kept.length}; \u043e\u0442\u0431\u0440\u043e\u0448\u0435\u043d\u043e ${meta.mainservice_selection.skipped}. \u0414\u0438\u0430\u043f\u0430\u0437\u043e\u043d \u043f\u043e \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u043c \u0444\u0430\u0439\u043b\u0430\u043c.`;\n$(\'min\').value=meta.threshold;\nconst uiInitiated=ne'
 'w Map();function fromUI(id){if(uiInitiated.has(id))return uiInitiated.get(id);const path=[],seen=new Set();let result=false;while(id!==null&&!seen.has(id)){if(uiInitiated.has(id)){result=uiInitiated.get(id);break}seen.add(id);const r=rows[id];path.push(id);if(r.visible||r.kind===\'HAR\'){result=true;break}id=r.parent}path.forEach(i=>uiInitiated.set(i,result));return result}\nconst activityRows=rows.filter(r=>[\'\u0411\u041b\',\'RPC\',\'HAR\'].includes(r.kind)),activityKey=r=>r.process+(fromUI(r.id)?\'\':\'-background\'),activityGroups=processes.flatMap(p=>[p,p+\'-background\']).filter(key=>activityRows.some(r=>activityKey(r)===key)),activityColors=Object.fromEntries(activityGroups.map(key=>[key,key.endsWith(\'-background\')?\'#929ba5\':colors[key]]));\n$(\'legend\').innerHTML=activityGroups.map(p=>`<span><i class="dot" style="background:${activityColors[p]}"></i>${esc(p)}</span>`).join(\'\');\n$(\'methodSuggestions\').innerHTML=[...new Set(rows.filter(r=>![\'\u0414\u043b\u0438\u043d\u043d\u0430\u044f \u0437\u0430\u0434\u0430\u0447\u0430\',\'SQL\'].includes(r.kind)).map(r=>r.name))].sort().map(name=>`<option value="${esc(name)}"></option>`).join(\'\');\n$(\'clearQuery\').onclick=()=>{$(\'query\').value=\'\';render();$(\'query\').focus()};\nconst seconds=t=>(t/1000).toFixed(3)+\' \u0441\';\nfunction logClock(t,milliseconds=false){const origin=meta.originMs??Date.parse(meta.origin.replace(\' \',\'T\')+\'Z\');const date=new Date(origin+t);return date.toISOString().slice(11,milliseconds?23:19)}\nfunction matchesCallType(r,type=$(\'callType\').value){return type===\'all\'||(type===\'cloud\'?!!r.has_cloud_call:!r.has_c'
 "loud_call)}\nfunction matchesErrorMode(r){const mode=$('showErrors').value;return mode==='only'?!!r.has_error:mode==='hide'?!r.has_error:true}\nfunction render(){$('showFps').hidden=!(meta.fps_samples||[]).length;drawActivity();updateRangeOverlay();const [a,b]=range,pct=t=>(t-a)/(b-a)*100,q=$('query').value.toLowerCase(),proc=$('proc').value;const keep=new Set(),matched=new Set(),visibleOnly=$('visibleOnly').checked,showDiagnostics=$('showDiagnostics').checked,showErrors=($('showErrors').value!=='hide'),showConsole=$('showConsole').checked;const forced=new Set(),errorPaths=new Set();$('chart').classList.toggle('errors-hidden',!showErrors);const diagnostic=r=>r.kind==='SQL'||r.kind==='\u0414\u043b\u0438\u043d\u043d\u0430\u044f \u0437\u0430\u0434\u0430\u0447\u0430'||r.kind==='\u041e\u0436\u0438\u0434\u0430\u043d\u0438\u0435';\nconst matchCallType=matchesCallType;\nconst cloudDetail=r=>{if(!r.cloud_host)return false;let parent=r.parent;while(parent!==null){if(rows[parent].visible)return true;parent=rows[parent].parent}return false};\nconst searchScope=new Set();if(q){for(const r of rows){if(!r.name.toLowerCase().includes(q))continue;const todo=[r.id];while(todo.length){const id=todo.pop();if(searchScope.has(id))continue;searchScope.add(id);todo.push(...children[id])}}}const inSearch=r=>(!q||searchScope.has(r.id))&&(!proc||r.process===proc)&&matchCallType(r);\nif(showErrors){for(const r of rows){if(!inSearch(r)||!r.has_error||!(r.call_errors||[]).some(error=>error.time>=a&&error.time<=b))continue;forced.add(r.id);let id=r.id;while(id!==null&&!errorPaths.has(id)){errorPaths.add(id);keep.add(id);id=rows[id].parent}}}\nfor(const r of rows){if"
 "(!matchesErrorMode(r)||!matchCallType(r))continue;if(r.kind==='\u041a\u043e\u043d\u0441\u043e\u043b\u044c UI'&&!showConsole)continue;if((r.kind==='\u041e\u0448\u0438\u0431\u043a\u0430'||r.kind==='\u041e\u0448\u0438\u0431\u043a\u0430 UI')&&!showErrors)continue;if(diagnostic(r)&&!showDiagnostics)continue;if(visibleOnly&&!r.visible&&!forced.has(r.id)&&!cloudDetail(r)&&!(r.kind==='\u041e\u0436\u0438\u0434\u0430\u043d\u0438\u0435'&&showDiagnostics))continue;if(r.end<a||r.start>b)continue;if((!q||r.name.toLowerCase().includes(q))&&(!proc||r.process===proc)){matched.add(r.id);let id=r.id;while(id!==null&&!keep.has(id)){keep.add(id);id=rows[id].parent}}}\n// Include descendants of a matching method; expansion remains controlled by the plus button.\nif(!visibleOnly&&(q||proc)){const todo=[...matched];while(todo.length){const id=todo.pop();for(const child of children[id]){const r=rows[child];if(r.end<a||r.start>b||diagnostic(r)&&!showDiagnostics)continue;if(!keep.has(child)){keep.add(child);todo.push(child)}}}}\nfor(const id of expanded){if(!keep.has(id)||!inSearch(rows[id]))continue;for(const child of children[id]){const r=rows[child];if(r.end>=a&&r.start<=b&&(!diagnostic(r)||showDiagnostics))keep.add(child)}}\nopenBranches.clear();for(const r of rows){if(!collapsed.has(r.id)&&(expanded.has(r.id)||errorPaths.has(r.id)||((q||proc)&&!matched.has(r.id)&&children[r.id].some(child=>keep.has(child)))))openBranches.add(r.id)}let visible=[];function walk(ids,depth){const ordered=[...ids].sort((i,j)=>sortDuration?rows[j].duration-rows[i].duration:rows[i].start-rows[j].start);for(const id of ordered){if(!keep.has(id))continue;if(!"
 'matchesErrorMode(rows[id])){walk(children[id],depth);continue}if(!matchCallType(rows[id])){walk(children[id],depth);continue}if(visibleOnly&&!rows[id].visible&&!forced.has(id)&&!cloudDetail(rows[id])&&!(rows[id].kind===\'\u041e\u0436\u0438\u0434\u0430\u043d\u0438\u0435\'&&showDiagnostics)){walk(children[id],depth);continue}if(rows[id].kind===\'\u041a\u043e\u043d\u0441\u043e\u043b\u044c UI\'&&!showConsole)continue;if(depth===0&&rows[id].kind!==\'\u041a\u043e\u043d\u0441\u043e\u043b\u044c UI\'&&!errorPaths.has(id)&&rows[id].duration<Number($(\'min\').value))continue;const excluded=!errorPaths.has(id)&&(blacklist.has(rows[id].name)||(diagnostic(rows[id])&&!showDiagnostics));if(excluded){walk(children[id],depth);continue}visible.push([id,depth]);if(openBranches.has(id))walk(children[id],depth+1)}}walk(roots,0);const shownIds=new Set(visible.map(([id])=>id));for(const id of forced){if(!shownIds.has(id)){visible.push([id,0]);shownIds.add(id)}}\nexportRows=visible.map(([id])=>id);$(\'body\').innerHTML=visible.map(([id,depth])=>{const r=rows[id],left=Math.max(a,r.start),right=Math.min(b,r.end);return `<tr id="row-${id}" data-id="${id}" class="${selected===id?\'selected\':\'\'} ${showErrors&&r.has_error?\'has-error\':\'\'}"><td><div class="branch" style="padding-left:${depth*18}px">${children[id].length?`<button class="toggle" data-toggle="${id}" aria-expanded="${openBranches.has(id)}">${openBranches.has(id)?\'\u2212\':\'+\'}</button>`:\'<span class="leaf"></span>\'}<div class="name ${r.appearance} ${r.kind===\'\u041a\u043e\u043d\u0441\u043e\u043b\u044c UI\'?\'console-event\':\'\'} ${showErrors&&r.has_error?\'has-error\':\'\'}">${esc(r.name)}${r.has_cloud_call?\'<spa'
 'n class="cloud-call" title="\u043f\u0440\u0438\u0441\u0443\u0442\u0441\u0442\u0432\u0443\u0435\u0442 \u043e\u0431\u043b\u0430\u0447\u043d\u044b\u0439 \u0432\u044b\u0437\u043e\u0432" aria-label="\u043f\u0440\u0438\u0441\u0443\u0442\u0441\u0442\u0432\u0443\u0435\u0442 \u043e\u0431\u043b\u0430\u0447\u043d\u044b\u0439 \u0432\u044b\u0437\u043e\u0432"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 1 L19 18 H1 Z" fill="currentColor"/><path d="M10 6 V11" stroke="white" stroke-width="2" stroke-linecap="round"/><circle cx="10" cy="14.5" r="1.2" fill="white"/></svg></span>\':\'\'} <span class="small">${esc(r.log_time)}</span> <button data-blacklist="${id}" title="\u0421\u043a\u0440\u044b\u0442\u044c \u0432\u0441\u0435 \u0432\u044b\u0437\u043e\u0432\u044b \u044d\u0442\u043e\u0433\u043e \u043c\u0435\u0442\u043e\u0434\u0430" style="padding:1px 5px;font-size:11px;font-style:normal">\u0432 \u0427\u0421</button> <button type="button" data-filter="${id}" title="\u041d\u0430\u0439\u0442\u0438 \u044d\u0442\u043e\u0442 \u043c\u0435\u0442\u043e\u0434 \u0438 \u0435\u0433\u043e \u0432\u043b\u043e\u0436\u0435\u043d\u043d\u044b\u0435 \u0432\u044b\u0437\u043e\u0432\u044b" style="padding:1px 5px;font-size:11px;font-style:normal">\u0412 \u0444\u0438\u043b\u044c\u0442\u0440</button><div class="small">${esc(r.process)}${r.cloud_host?` \xb7 \u041e\u0431\u043b\u0430\u0447\u043d\u044b\u0439 \u0432\u044b\u0437\u043e\u0432 \u2192 ${esc(r.cloud_host)}`:\'\'}${r.kind===\'\u0414\u043b\u0438\u043d\u043d\u0430\u044f \u0437\u0430\u0434\u0430\u0447\u0430\'?\' \xb7 \u0434\u043b\u0438\u043d\u043d\u0430\u044f \u0437\u0430\u0434\u0430\u0447\u0430\':\'\'}${children[id].length?\' \xb7 \'+children[id].length+\' \u0432\u043b\u043e\u0436\u0435\u043d\u043d\u044b\u0445\':\'\'}${r.cloud_host?`<br>${esc(r.file)}:${r.line}`:\'\'}</div></div></div></td><td><div class="track"><div class="bar" style="left:${Math.max(0,pct(left))}%;width:${Math.max(.1,(right-left)/(b-a)*100)}%;background:${r.visible?colors[r.process]:\'#929ba5\'}" title="${seconds(r.start)} \u2192 ${seconds(r.end)}"></div></div></td><td class="dur">${r.kind===\'\u041a\u043e\u043d\u0441\u043e\u043b\u044c UI\'?\'\u0421\u043e\u0431\u044b\u0442\u0438\u0435 UI\':r.kind===\'\u041e\u0448\u0438\u0431\u043a\u0430 UI\'?\'UI-error\':Math.round(r.duration)+\' \u043c\u0441\'}<div class="small">${seconds(r.start)} \u2192 ${seconds(r.end)}</div></td></tr>`}).join(\'\');\n$(\'axis\').innerHTML=Array.from({length:6},(_,i)=>`<span>${seconds(a+(b-a)*i/5)}</span>`'
 ").join('');$('resetBlacklist').hidden=blacklist.size===0;$('resetBlacklist').textContent='\u0421\u0431\u0440\u043e\u0441\u0438\u0442\u044c \u0427\u0421 ('+blacklist.size+')';$('status').textContent=visible.length+' \u0441\u0442\u0440\u043e\u043a';$('all').classList.toggle('active',a===0&&b===meta.span);$('near').classList.toggle('active',rangeMode==='near');$('period').classList.toggle('active',rangeMode==='period');$('period').disabled=a===0&&b===meta.span;$('sort').classList.toggle('active',sortDuration);$('query').classList.toggle('active',!!q);$('clearQuery').disabled=!q;$('visibleLabel').style.background=visibleOnly?'#e7f2ff':'';$('visibleLabel').style.color=visibleOnly?'#1456a0':'';$('proc').classList.toggle('active',!!proc);$('diagnosticsLabel').style.background=showDiagnostics?'#e7f2ff':'';$('diagnosticsLabel').style.color=showDiagnostics?'#1456a0':'';}\nfunction decodeSaby(value){\n if(Array.isArray(value))return value.map(decodeSaby);\n if(!value||typeof value!=='object')return value;\n if(Array.isArray(value.s)&&Array.isArray(value.d)&&value.s.length&&value.s.every(field=>field&&typeof field.n==='string')){\n  const fields=value.s;\n  const record=data=>{if(!Array.isArray(data))return decodeSaby(data);const result=Object.create(null);fields.forEach((field,i)=>{if(i<data.length){let cell=data[i];const type=field.t;const schema=Array.isArray(type)?type:type&&typeof type==='object'&&Array.isArray(type.s)?type.s:null;if(schema&&Array.isArray(cell))cell={s:schema,d:cell,f:type.f};result[field.n]=decodeSaby(cell)}});if(data.length>fields.length)result['\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0435 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u044f']=data.slice(fields.length).map(decodeSaby);return result};\n  // f=0 is a r"
 'ecord, f=1 is a record set. Otherwise use the data shape.\n  const recordSet=value.f===1||(value.f!==0&&value.d.length>0&&value.d.every(row=>Array.isArray(row)&&row.length===fields.length));\n  return recordSet?value.d.map(record):record(value.d);\n }\n return Object.fromEntries(Object.entries(value).map(([key,child])=>[key,decodeSaby(child)]));\n}\n\nfunction prettyResponse(text){\n if(text===undefined||text===null)return \'\u0422\u0435\u043b\u043e \u043e\u0442\u0432\u0435\u0442\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e \u0432 \u043b\u043e\u0433\u0430\u0445. \u042d\u0442\u043e \u043d\u0435 \u043e\u0437\u043d\u0430\u0447\u0430\u0435\u0442, \u0447\u0442\u043e \u043c\u0435\u0442\u043e\u0434 \u0432\u0435\u0440\u043d\u0443\u043b \u043f\u0443\u0441\u0442\u043e\u0439 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442.\';\n text=String(text);try{return JSON.stringify(decodeSaby(JSON.parse(text)),null,2)}catch{}\n // Loggers may truncate JSON. Format its structure without changing string values.\n if(!/^[\\s]*[\\[{]/.test(text))return text;\n let output=\'\',depth=0,inString=false,escaped=false;\n const newline=()=>{output=output.replace(/[ \\t]+$/,\'\');if(!output.endsWith(\'\\n\'))output+=\'\\n\';output+=\'  \'.repeat(Math.max(0,depth))};\n for(let i=0;i<text.length;i++){const c=text[i];if(inString){output+=c;if(escaped)escaped=false;else if(c===\'\\\\\')escaped=true;else if(c===\'"\')inString=false;continue}\n if(c===\'"\'){inString=true;output+=c}else if(c===\'{\'||c===\'[\'){output+=c;depth++;newline()}else if(c===\'}\'||c===\']\'){depth=Math.max(0,depth-1);output=output.replace(/\\s+$/,\'\');newline();output+=c}else if(c===\',\'){output+=c;newline()}else if(c===\':\'){output+=\': \'}else if(!/\\s/.test(c)){output+=c}}\n return output.trimEnd();\n}\n\nfunction choose(id,scroll=true){selected=id;let p=rows[id].parent;while(p!==null){collapsed.de'
 "lete(p);expanded.add(p);p=rows[p].parent}render();updateMarker();const {response,response_source,params,params_source,...info}=rows[id];delete info.response_previous_source;delete info.params_previous_source;delete info.response_invalid;delete info.params_invalid;$('params').textContent=params===undefined?'\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u0432\u044b\u0437\u043e\u0432\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u044b \u0432 \u043b\u043e\u0433\u0430\u0445.':prettyResponse(params);$('paramsSource').textContent=params_source||'';$('details').textContent=JSON.stringify(info,null,2);$('response').textContent=prettyResponse(response);$('responseSource').textContent=response_source||'';if(scroll)document.getElementById('row-'+id)?.scrollIntoView({block:'center',behavior:'smooth'});}\n$('resetBlacklist').onclick=()=>{blacklist.clear();render()};\n$('body').onclick=e=>{const filter=e.target.closest('[data-filter]');if(filter){$('query').value=rows[Number(filter.dataset.filter)].name;render();$('scroll').scrollTop=0;return}const blocked=e.target.closest('[data-blacklist]');if(blocked){blacklist.add(rows[Number(blocked.dataset.blacklist)].name);if(selected!==null&&blacklist.has(rows[selected].name)){selected=null;$('selection-marker')?.remove();$('details').textContent='\u041c\u0435\u0442\u043e\u0434 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d \u0432 \u0427\u0421.'}render();return}const t=e.target.closest('[data-toggle]');if(t){const id=Number(t.dataset.toggle);if(openBranches.has(id)){expanded.delete(id);collapsed.add(id)}else{collapsed.delete(id);expanded.add(id)}render();return}const tr=e.target.closest('tr');if(tr)choose(Number(tr.dataset.id),false)};\n$('all').onclick=()"
 "=>{rangeMode='all';range=[0,meta.span];render()};function applySelectedWindow(){if(selected===null)return;rangeMode='near';const r=rows[selected],pad=Math.max(0,Number($('windowMs').value)||0);range=[Math.max(0,r.start-pad),Math.min(meta.span,r.end+pad)];if(range[1]<=range[0])range[1]=range[0]+1;render()}$('near').onclick=()=>{if(selected===null)return;$('query').value='';applySelectedWindow()};$('windowMs').oninput=()=>{if($('near').classList.contains('active'))applySelectedWindow()};$('collapse').onclick=()=>{expanded.clear();rows.forEach(r=>collapsed.add(r.id));render()};$('expand').onclick=()=>{collapsed.clear();rows.forEach(r=>expanded.add(r.id));render()};$('sort').onclick=()=>{sortDuration=!sortDuration;$('sort').textContent=sortDuration?'\u041f\u043e \u0434\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u0438 \u2193':'\u041f\u043e \u043d\u0430\u0447\u0430\u043b\u0443 \u2193';render()};['query','proc','callType','min','visibleOnly','showDiagnostics','showErrors','showConsole','showFps'].forEach(id=>$(id).oninput=render);\nconst bins=240,series=activityGroups.map(()=>Array(bins).fill(0));for(const r of activityRows){const lo=Math.max(0,Math.floor(r.start/meta.span*bins)),hi=Math.min(bins-1,Math.floor(r.end/meta.span*bins));for(let i=lo;i<=hi;i++)series[activityGroups.indexOf(activityKey(r))][i]+=Math.max(0,Math.min(r.end,(i+1)*meta.span/bins)-Math.max(r.start,i*meta.span/bins))/(meta.span/bins)}\nlet activityCache=null,timelineSearchCache=null;\nfunction timelineSearch(){const query=$('query').value.toLowerCase();if(!timelineSearchCache||timelineSearchCache.query!==query){const matched=n"
 'ew Set(rows.filter(r=>r.name.toLowerCase().includes(query)).map(r=>r.id)),context=new Set(matched);if(query){const todo=[...matched];while(todo.length){for(const id of children[todo.pop()]){if(!context.has(id)){context.add(id);todo.push(id)}}}}timelineSearchCache={query,matched,context}}return timelineSearchCache}\n\n$(\'period\').onclick=()=>{if(range[1]<=range[0]||(range[0]===0&&range[1]===meta.span))return;rangeMode=\'period\';render()};\nfunction chartRange(){return rangeMode===\'near\'||rangeMode===\'period\'?range:[0,meta.span]}\nfunction chartTime(x,bounds=chartRange()){return bounds[0]+(x-30)/1160*(bounds[1]-bounds[0])}\nfunction chartPosition(t){const [a,b]=chartRange();return 30+(t-a)/Math.max(1,b-a)*1160}\nfunction fpsColor(value){const t=Math.max(0,Math.min(64,value))/64;return `rgb(${Math.round(220*(1-t)+34*t)},${Math.round(45*(1-t)+160*t)},${Math.round(55*(1-t)+70*t)})`}\nfunction drawFps(){const visible=(meta.fps_samples||[]).length>0&&$(\'showFps\').value!==\'hide\';$(\'fpsPanel\').hidden=!visible;if(!visible)return;const [a,b]=chartRange(),samples=(meta.fps_samples||[]).filter(s=>s.time>=a&&s.time<=b);const y=v=>112-Math.max(0,Math.min(64,v))/64*96;let svg=\'<defs><linearGradient id="fpsGradient" gradientUnits="userSpaceOnUse" x1="0" y1="112" x2="0" y2="16"><stop offset="0" stop-color="rgb(220,45,55)"/><stop offset="1" stop-color="rgb(34,160,70)"/></linearGradient></defs>\';for(const value of [0,16,32,48,64])svg+=`<line x1="30" x2="1190" y1="${y(value)}" y2="${y(value)}" stroke="#e4ebf3"/><text x="24" y="${y(value)+4}" text-anchor="end" fill="${fpsColor(value)}" font-size="11">${value}</text>`;let previous=null;for(const sample of samples){const x=chartPosition(sample.time),cy=y(sample.value);if(previous&&sample.time-previous.time<=3000)svg+=`<line x1="${chartPosition(previous.time)}" y1="${y(previous.value)}" x2="${x}" y2="${cy}" stroke="url(#fpsGradient)" stroke-width="2"/>`;svg+=`<circle cx="${x}" cy="${cy}" r="2" fill="${fpsColor(sample.value)}"><title>${esc(logClock(sample.time,true)+\' \xb7 \'+sample.value+\' FPS\')}</title></circle>`;previous=sample}$(\'fpsChart\').innerHTML=svg;$(\'fpsAxis\').innerHTML=Array.from({length:7},(_,i)=>`<span>${logClock(a+(b-a)*i/6)}</span>`).join(\'\');}\nfunction drawActivity(){const [chartStart,chartEnd]=chartRange(),chartSpan=Math.max(1,chartEnd-chartStart),callType=$(\'callType\').value,errorMode=$(\'showErrors\').value,search=timelineSearch(),searchRows=search.query?rows.filter(r=>search.matched.has(r.id)&&[\'\u0411\u041b\',\'RPC\',\'HAR\',\'\u041c\u0435\u0442\u043e\u0434\',\'\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a\',\'\u041d\u0435\u0437\u0430\u0432\u0435\u0440\u0448\u0451\u043d\u043d\u044b\u0439 \u0432\u044b\u0437\u043e\u0432\'].includes(r.kind)):activityRows;let plotSeries=series;if(chartStart!==0||chartEnd!==meta.span||callType!==\'all\'||errorMode!==\'show\'||search.query){const key=JSON.stringify([chartStart,chartEnd,callType,errorMode,search.query]);if(!activityCache||activityCache.key!==key){const zoom=activityGroups.map(()=>Array(bins).fill(0));for(const r of searchRows){if(!matchesErrorMode(r)||!matchesCallType(r,callType)||r.end<chartStart||r.start>chartEnd)continue;const lo=Math.max(0,Math.floor((r.start-chartStart)/chartSpan*bins)),hi=Math.min(bins-1,Math.floor((r.end-chartStart)/chartSpan*bins));for(let i=lo;i<=hi;i++)zoo'
 'm[activityGroups.indexOf(activityKey(r))][i]+=Math.max(0,Math.min(r.end,chartStart+(i+1)*chartSpan/bins)-Math.max(r.start,chartStart+i*chartSpan/bins))/(chartSpan/bins)}activityCache={key,series:zoom}}plotSeries=activityCache.series}const showBackground=!$(\'visibleOnly\').checked||errorMode===\'only\',shown=activityGroups.map((key,index)=>index).filter(index=>(showBackground||!activityGroups[index].endsWith(\'-background\'))&&((callType===\'all\'&&errorMode===\'show\'&&!search.query)||plotSeries[index].some(value=>value>0)));const peak=Math.max(1,...Array.from({length:bins},(_,i)=>shown.reduce((sum,index)=>sum+plotSeries[index][i],0)));let svg=`<text x="0" y="15" fill="#789">${peak.toFixed(1)}</text>`;for(let i=0;i<bins;i++){let y=140;shown.forEach(p=>{const s=plotSeries[p];const h=s[i]/peak*120;y-=h;if(h)svg+=`<rect x="${30+i*1160/bins}" y="${y}" width="${1160/bins}" height="${h}" fill="${activityColors[activityGroups[p]]}"><title>${logClock(chartStart+i*chartSpan/bins,true)} \xb7 ${esc(activityGroups[p])} \xb7 ${s[i].toFixed(2)} \u0430\u043a\u0442\u0438\u0432\u043d\u044b\u0445</title></rect>`})}for(const marker of meta.console_markers||[]){const fullPass=marker.type===\'full-pass-start\'||marker.type===\'full-pass-end\';if(marker.time<chartStart||marker.time>chartEnd)continue;if(!fullPass&&(!$(\'showConsole\').checked||errorMode===\'only\'||!search.context.has(marker.node)||!matchesCallType(rows[marker.node],callType)))continue;const x=chartPosition(marker.time),init=marker.type===\'initialization\';if(fullPass){svg+=`<g class="console-marker full-pass-marker" data-console-id="${marker.node}"><title>${esc(logClock(marker.time,true)+\' \xb7 \'+rows[marker.node].name)}</title><line x1="${x}" x2="${x}" y1="22" y2="145" stroke="#16803c" stroke-width="2" stroke-dasharray="6 4"/><text x="${x>600?x-5:x+5}" y="16" fill="#16803c" font-size="12" font-weight="600" text-anchor="${x>600?\'end\':\'start\'}">${esc(marker.label)}</text></g>`;continue;}svg+=`<g class="console-marker" data-console-id="${marker.node}"><title>${esc(logClock(marker.time,true)+\' \xb7 \'+marker.label)}</title><line'
 ' x1="${x}" x2="${x}" y1="22" y2="145" stroke="#176aca" stroke-width="1.5"/>${init?\'\':`<text transform="translate(${x>1180?x-5:x+5} 24) rotate(90)" fill="#176aca" font-size="10" font-weight="400" text-anchor="start">${esc(marker.label)}</text>`}</g>`}for(const error of meta.error_markers||[]){if(!search.context.has(error.node)||!matchesCallType(rows[error.node],callType)||error.time<chartStart||error.time>chartEnd)continue;const x=chartPosition(error.time);svg+=`<g class="error-marker" data-error-id="${error.node}"><title>${esc(logClock(error.time,true)+\' \xb7 \'+error.file+\':\'+error.line+\' \xb7 \'+error.message)}</title><line x1="${x}" x2="${x}" y1="16" y2="145" stroke="#d92335" stroke-width="1.5"/><text x="${x}" y="12" fill="#d92335" font-size="10" text-anchor="middle">${esc(error.label||\'error\')}</text></g>`}drawFps();$(\'chartaxis\').innerHTML=Array.from({length:7},(_,i)=>`<span>${logClock(chartStart+chartSpan*i/6)}</span>`).join(\'\');$(\'chart\').innerHTML=svg;$(\'legend\').innerHTML=shown.map(index=>{const key=activityGroups[index];return `<span><i class="dot" style="background:${activityColors[key]}"></i>${esc(key)}</span>`}).join(\'\');updateMarker();updateRangeOverlay();$(\'chart\').classList.toggle(\'errors-hidden\',!($(\'showErrors\').value!==\'hide\'));}\n$(\'chartaxis\').innerHTML=Array.from({length:7},(_,i)=>`<span>${logClock(meta.span*i/6)}</span>`).join(\'\');\nfunction updateMarker(){ $(\'selection-marker\')?.remove(); if(selected===null||!matchesErrorMode(rows[selected])||!matchesCallType(rows[select'
 "ed])||!timelineSearch().matched.has(selected))return; const x=chartPosition(rows[selected].start);if(x<30||x>1190)return; const line=document.createElementNS('http://www.w3.org/2000/svg','line');line.id='selection-marker';line.setAttribute('x1',x);line.setAttribute('x2',x);line.setAttribute('y1',5);line.setAttribute('y2',145);line.setAttribute('stroke','#df263b');line.setAttribute('stroke-width','2');line.setAttribute('stroke-dasharray','6 4');line.style.pointerEvents='none';$('chart').append(line);}\n$('chart').onclick=e=>{if(suppressChartClick){suppressChartClick=false;return;}const milestone=e.target.closest('[data-console-id]');if(milestone){rangeMode='all';range=[0,meta.span];$('proc').value='';choose(Number(milestone.dataset.consoleId));return;}const error=e.target.closest('[data-error-id]');if(error){rangeMode='all';range=[0,meta.span];$('proc').value='';choose(Number(error.dataset.errorId));return;}const time=chartTime(chartX(e));let candidates=rows.filter(r=>matchesErrorMode(r)&&matchesCallType(r)&&timelineSearch().matched.has(r.id)&&['\u0411\u041b','RPC','HAR','\u041c\u0435\u0442\u043e\u0434','\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a'].includes(r.kind)&&r.start<=time&&r.end>=time);if(!candidates.length)candidates=rows.filter(r=>matchesErrorMode(r)&&matchesCallType(r)&&timelineSearch().matched.has(r.id)).sort((a,b)=>Math.abs(a.start-time)-Math.abs(b.start-time)).slice(0,1);if(!candidates.length)return;const r=candidates.sort((a,b)=>b.duration-a.duration)[0];rangeMode='all';range=[0,meta.span];$('proc').value='';choose(r.id)};render"
 "();\n\nfunction chartX(e){const chart=$('chart'),matrix=chart.getScreenCTM();if(!matrix)return 30;const point=chart.createSVGPoint();point.x=e.clientX;point.y=e.clientY;return Math.max(30,Math.min(1190,point.matrixTransform(matrix.inverse()).x))}\nfunction updateRangeOverlay(preview=null){$('range-overlay')?.remove();const bounds=preview||range,view=chartRange();if(!preview&&bounds[0]===view[0]&&bounds[1]===view[1])return;const box=document.createElementNS('http://www.w3.org/2000/svg','rect');box.id='range-overlay';box.setAttribute('x',chartPosition(bounds[0]));box.setAttribute('y',0);box.setAttribute('width',Math.max(1,(bounds[1]-bounds[0])/(view[1]-view[0])*1160));box.setAttribute('height',150);box.setAttribute('fill','#2274cf');box.setAttribute('fill-opacity','.15');box.setAttribute('stroke','#2274cf');box.style.pointerEvents='none';$('chart').append(box)}\n$('chart').onpointerdown=e=>{if(e.button!==0)return;suppressChartClick=false;chartDrag={x:chartX(e),moved:false,bounds:[...chartRange()]};$('chart').setPointerCapture(e.pointerId)};\n$('chart').onpointermove=e=>{if(!chartDrag)return;const x=chartX(e);if(Math.abs(x-chartDrag.x)>5)chartDrag.moved=true;if(chartDrag.moved)updateRangeOverlay([chartTime(Math.min(x,chartDrag.x),chartDrag.bounds),chartTime(Math.max(x,chartDrag.x),chartDrag.bounds)])};\n$('chart').onpointerup=e=>{if(!chartDrag)return;const x=chartX(e);if(chartDrag.moved&&Math.abs(x-chartDrag.x)>5){range=[chartTime(Math.min(x,chartDrag.x),chartDrag.bounds),chartTime(Ma"
 "th.max(x,chartDrag.x),chartDrag.bounds)];rangeMode=rangeMode==='period'?'period':'custom';suppressChartClick=true;render();$('scroll').scrollTop=0}chartDrag=null;updateRangeOverlay()};\n$('chart').onpointercancel=()=>{chartDrag=null;updateRangeOverlay()};\n\nfunction exportReport(){\n const ids=new Set(exportRows);for(const marker of meta.console_markers||[]){if((marker.type==='full-pass-start'||marker.type==='full-pass-end')&&marker.time>=range[0]&&marker.time<=range[1])ids.add(marker.node)}const todo=[...ids];\n while(todo.length){for(const id of children[todo.pop()]){if(rows[id].end<range[0]||rows[id].start>range[1]||ids.has(id))continue;ids.add(id);todo.push(id)}}\n const selectedRows=rows.filter(r=>ids.has(r.id)),mapping=new Map(selectedRows.map((r,i)=>[r.id,i]));\n const data=selectedRows.map(r=>{let parent=r.parent;while(parent!==null&&!mapping.has(parent))parent=rows[parent].parent;return {...r,id:mapping.get(r.id),parent:parent===null?null:mapping.get(parent)}});\n const metadata={...meta};metadata.fps_samples=(meta.fps_samples||[]).filter(s=>s.time>=range[0]&&s.time<=range[1]);for(const key of ['error_markers','console_markers'])metadata[key]=(meta[key]||[]).filter(m=>mapping.has(m.node)&&m.time>=range[0]&&m.time<=range[1]).map(m=>({...m,node:mapping.get(m.node)}));\n const controls={};for(const id of ['query','proc','callType','min','windowMs','visibleOnly','showDiagnostics','showErrors','showConsole','showFps'])controls[id]={value:$(id).value,checked:$(id).checked};\n const state={range:[...range],rangeMode,sortDuration,controls,expanded:[...expanded].filter(id=>mapping.has(id)).map(id=>mapping.get(id)),collapsed:[...collapsed].filter(id=>mapping.has(id)).map(id=>mapping.get(id)),blacklist:[...blacklist],selected:mapping.get(selected)??null};\n const json=value=>JSON.stringify(value).r"
 "eplaceAll('<','\\\\u003c');\n const clone=document.documentElement.cloneNode(true);clone.querySelector('#exportState')?.remove();clone.querySelector('#downloadReport')?.parentElement.remove();\n const script=[...clone.querySelectorAll('script')].find(el=>el.textContent.includes('const rows='));\n const source=script.textContent,start=source.indexOf('const rows='),end=source.indexOf(',$=id=>',start);\n script.textContent=source.slice(0,start)+'const rows='+json(data)+',meta='+json(metadata)+source.slice(end);\n const stateElement=document.createElement('script');stateElement.id='exportState';stateElement.type='application/json';stateElement.textContent=json(state);script.before(stateElement);\n const style=document.createElement('style');style.textContent='main> :not(#scroll):not(.call-details){display:none!important}#scroll{height:auto;min-height:400px;max-height:none;overflow:visible;resize:none}';clone.querySelector('head').append(style);\n const timestamp=t=>{const origin=meta.originMs??Date.parse(meta.origin.replace(' ','T')+'Z');return new Date(origin+t).toISOString().slice(0,23).replace('T','_').replaceAll(':','-')};\n const name='report-'+timestamp(range[0])+'--'+timestamp(range[1])+'.html';clone.querySelector('title').textContent=name;\n const url=URL.createObjectURL(new Blob(['<!doctype html>\\n'+clone.outerHTML],{type:'text/html;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTime"
 "out(()=>URL.revokeObjectURL(url),1000);\n}\nif($('downloadReport'))$('downloadReport').onclick=exportReport;\nif($('exportState')){const state=JSON.parse($('exportState').textContent);range=state.range;rangeMode=state.rangeMode;sortDuration=state.sortDuration;for(const [id,value] of Object.entries(state.controls)){ $(id).value=value.value;$(id).checked=value.checked}for(const id of state.expanded)expanded.add(id);for(const id of state.collapsed||[])collapsed.add(id);for(const name of state.blacklist)blacklist.add(name);render();if(state.selected!==null)choose(state.selected,false)}\n\n</script></html>"
)
def method(s):return re.sub(r'/\d+$','',s.strip().split('->')[-1])
START=time.monotonic()
STATE={'stage':'Запуск','detail':''}
def progress(stage,detail=''):
 STATE.update(stage=stage,detail=detail)
 print(f"[{time.monotonic()-START:7.1f} с] {stage}: {detail}",flush=True)
def heartbeat(stop):
 while not stop.wait(5):progress(STATE['stage'],STATE['detail'])
def is_cloud_host(value):
 # An arbitrary RPC may target a local service; require an explicit cloud host.
 from urllib.parse import urlsplit
 try:host=urlsplit(value if '://' in value else '//'+value).hostname or ''
 except ValueError:return False
 host=host.lower().rstrip('.')
 return (host in ('sbis.ru','saby.ru') or host.endswith(('.sbis.ru','.saby.ru'))
         or host.startswith('sbis-online-')
         or bool(re.fullmatch(r'sbis-[a-z0-9-]+-[0-9a-f]{8,10}-[a-z0-9]{5}',host)))

def select_recent_mainservice(files):
 # Rotation suffixes grow chronologically; filesystem mtimes change on extraction.
 pattern=re.compile(r'(?:^|_)MainService[-_]events(?:_(\d+))?\.log$',re.I)
 mainfiles=[p for p in files if pattern.search(p.name)]
 def order(p):
  date=re.search(r'\d{4}-\d{2}-\d{2}',p.name)
  return (date[0] if date else '',int(pattern.search(p.name)[1] or 0),str(p))
 selected=sorted(mainfiles,key=order)[-3:]
 skipped=set(mainfiles)-set(selected) if len(mainfiles)>3 else set()
 return [p for p in files if p not in skipped],selected,skipped

def log_file_bounds(path):
 # Read boundary records without loading a large file or its JSON payloads.
 pattern=re.compile(rb'^(\d\d):(\d\d):(\d\d)\.(\d{3})(?=[ \t])',re.M)
 date=re.search(r'\d{4}-\d{2}-\d{2}',path.name)
 day=datetime.date.fromisoformat(date[0]).toordinal()*86400000 if date else 0
 with path.open('rb') as stream:
  first=None
  for line in stream:
   first=pattern.match(line.lstrip(b'\xef\xbb\xbf'))
   if first:break
  if first is None:return None
  stream.seek(0,2);offset=stream.tell();tail=b'';last=None
  while offset and last is None:
   size=min(offset,65536);offset-=size;stream.seek(offset)
   tail=stream.read(size)+tail
   matches=list(pattern.finditer(tail))
   if matches:last=matches[-1]
 def milliseconds(match):
  h,m,s,ms=map(int,match.groups());return ((h*60+m)*60+s)*1000+ms
 start=milliseconds(first);end=milliseconds(last or first)
 if start-end>43200000:end+=86400000
 return day+start,day+end

def main():
 ap=argparse.ArgumentParser(description='Иерархический каскад Saby logs + HAR')
 ap.add_argument('folder',nargs='?',default=str(Path(__file__).resolve().parent));ap.add_argument('--output',default='log_report.html');ap.add_argument('--recursive',action='store_true');ap.add_argument('--serve',action='store_true');ap.add_argument('--long-task-ms',type=int,default=100)
 ap.add_argument('--omitted-mainservice-files',type=int,default=0,help=argparse.SUPPRESS)
 a=ap.parse_args();folder=Path(a.folder).resolve();
 if not folder.is_dir():ap.error('Папка логов не существует: '+str(folder))
 progress('Поиск логов',str(folder));files=sorted(p for p in (folder.rglob('*.log') if a.recursive else folder.glob('*.log')) if re.search(r'(?:-|_)events(?:_\d+)?\.log$',p.name))
 progress('Найдены файлы',f'{len(files)} шт.; {sum(p.stat().st_size for p in files)/1048576:.1f} МБ')
 if not files:ap.error('Не найдены *events.log')
 files,selected_mainservice,skipped_mainservice=select_recent_mainservice(files)
 skipped_count=len(skipped_mainservice)+a.omitted_mainservice_files
 window=None
 if skipped_count:
  bounds=[bound for p in selected_mainservice if (bound:=log_file_bounds(p)) is not None]
  if not bounds:ap.error('В последних MainService-events нет временных отметок')
  window=(min(bound[0] for bound in bounds),max(bound[1] for bound in bounds))
  progress('Ограничение MainService',f'обрабатываем {len(selected_mainservice)} из {len(selected_mainservice)+skipped_count}; отброшено {skipped_count}: '+', '.join(p.name for p in selected_mainservice))
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
 nodes=[];edges={};async_traces=set();errors=[];log_start=None;log_end=None
 def add(process,trace,root,name,start,end,kind,file,line,thread='',visible=False,preserve_window=False):
  duration=end-start;original_interval=(start,end)
  if window and not preserve_window:start=max(start,window[0]);end=min(end,window[1])
  if end<start:return
  nodes.append(dict(process=process,trace=trace,root=root,name=method(name),start=start,end=end,duration=duration,kind=kind,file=file,line=line,thread=thread,visible=visible,parent=None))
  if original_interval!=(start,end):nodes[-1]['window_clipped']=True
 for file_index,p in enumerate(files,1):
  progress('Чтение',f'{file_index}/{len(files)} · {p.name} · {p.stat().st_size/1048576:.1f} МБ');file_size=p.stat().st_size;read_bytes=0;last_progress=time.monotonic()
  process=re.sub(r'^\d{4}-\d{2}-\d{2}_','',p.name).removesuffix('-events.log');process=re.sub(r'(?:-|_)events(?:_\d+)?\.log$','',process);process='Launcher' if re.fullmatch(r'events(?:_\d+)?\.log',process) else process
  dm=re.search(r'\d{4}-\d{2}-\d{2}',p.name);day=datetime.date.fromisoformat(dm[0]).toordinal()*86400000 if dm else 0;last=0;pending={};method_pending={}
  def event_records(stream):
   saved=None
   for line_number,line in enumerate(stream,1):
    if re.match(r'\d\d:\d\d:\d\d\.\d{3}(?=[ \t])',line):
     if saved is not None:yield saved
     saved=(line_number,line)
    elif saved is not None and ('[m][start]' in saved[1] or '[m][finish]' in saved[1]):saved=(saved[0],saved[1]+line)
   if saved is not None:yield saved
  for ln,l in event_records(p.open(encoding='utf-8-sig',errors='replace')):
   read_bytes+=len(l.encode('utf-8'))
   if time.monotonic()-last_progress>=2:
    progress('Чтение',f'{file_index}/{len(files)} · {p.name} · ~{min(100,read_bytes/max(1,file_size)*100):.0f}% · строк {ln:,} · операций {len(nodes):,}');last_progress=time.monotonic()
   tm=re.match(r'(\d\d):(\d\d):(\d\d)\.(\d{3})(?=[ \t])',l)
   if not tm:continue
   h,m,s,ms=map(int,tm.groups());raw=((h*60+m)*60+s)*1000+ms
   if last-raw>43200000:day+=86400000
   last=raw;t=day+raw
   if window and not window[0]<=t<=window[1]:continue
   log_start=t if log_start is None else min(log_start,t);log_end=t if log_end is None else max(log_end,t);c=l.rstrip().split('\t');msg=c[-1];thread=c[1] if len(c)>1 else ''
   trace=c[4] if len(c)>5 else '';root=c[5] if len(c)>9 else trace;ctx=c[8] if len(c)>9 else c[5] if len(c)>5 else ''
   child=re.search(r'\bruuid:([\w-]+)',msg)
   if child and '[async call]' in msg:async_traces.add(child[1])
   if child and ('[async call]' in msg or '[rpc call][start]' in msg):edges[child[1]]=(trace,t)
   key=(thread,trace)
   if '[w][start]' in msg:pending[key]=(t,ctx,ln)
   method_start=re.search(r'\[m\]\[start\]\s+([^\s(]+)\((.*)\)\s*$',msg,re.S)
   if method_start:
    raw_params=method_start[2];values=[];decoder=json.JSONDecoder();remaining=raw_params.strip()
    try:
     while remaining:
      value,offset=decoder.raw_decode(remaining);values.append(value);remaining=remaining[offset:].strip()
      if remaining:
       if not remaining.startswith(';'):raise ValueError('Argument separator')
       remaining=remaining[1:].strip()
     payload=json.dumps(values,ensure_ascii=False)
    except ValueError:payload=raw_params
    method_pending.setdefault((thread,trace,method_start[1]),[]).append((payload,ln))

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
   elif 'Ожидание завершения фоновых подзадач' in msg:
    name='Ожидание завершения фоновых подзадач';kind='Ожидание'
   elif 'Waiting for the GIL' in msg or 'waiting for future' in msg:
    name=msg.split('[exec_period]',1)[0].strip();kind='Длинная задача';start=t;end=t+dur
   if name:add(process,trace,root,name,start,end,kind,str(p.relative_to(folder)),ln,thread)
   if name and kind=='RPC':
    host_match=re.search(r'\bhost:([^\s]+)',msg)
    if host_match and is_cloud_host(host_match[1]):nodes[-1]['has_cloud_call']=True;nodes[-1]['cloud_host']=host_match[1]
   if name and kind=='Метод':
    stack=method_pending.get((thread,trace,name),[])
    if stack:
     payload,source_line=stack.pop();set_payload(nodes[-1],payload,str(p.relative_to(folder))+':'+str(source_line),'params')
    tail=msg[d.end():].strip()
    tail=re.sub(r'^(?:result|response|return|результат)\s*[:=]\s*','',tail,flags=re.I)
    if tail.startswith(('{','[','"')) or tail in ('null','true','false') or re.fullmatch(r'-?\d+(?:\.\d+)?',tail):set_response(nodes[-1],tail,str(p.relative_to(folder))+':'+str(ln))

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
     if window and (end<window[0] or start>window[1]):continue
     candidates=[n for n in nodes if n['name']==name and n['kind']=='БЛ' and abs(n['start']-start)<2000 and n['end']>=start-100]
     if candidates:
      n=min(candidates,key=lambda n:abs(n['start']-start));n['visible']=True;n['har']=p.name
     else:
      add('UI / HAR','har:'+str(harcount),'',name,start,end,'HAR',p.name,0,visible=True);n=nodes[-1]
     if is_cloud_host(req.get('url','')):n['has_cloud_call']=True;n['cloud_host']=req['url']
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
 fps_samples=[]
 console_pass_starts=set()
 for consolefile in consolefiles:
  relative=str(consolefile.relative_to(folder));dm=re.search(r'\d{4}-\d{2}-\d{2}',consolefile.name);day=datetime.date.fromisoformat(dm[0]).toordinal()*86400000 if dm else 0;previous=0;record=None
  def save_console(record):
   if record is None:return
   t,line_number,text,is_error=(record[key] for key in ('time','line','text','is_error'))
   text=re.sub(r'\s*\((?:resources/|https?://|file:)[^\r\n]*?:\d+(?::\d+)?\)\s*$','',text.strip())
   fps_match=re.fullmatch(r'fps\s+(\d+(?:[.,]\d+)?)',text,re.I)
   if fps_match and not is_error:
    fps_samples.append(dict(time=t,value=float(fps_match[1].replace(',','.'))))
    return
   full_pass=re.match(r'^(Начало|Конец) полного прохода(?:\s|$)',text,re.I)
   pass_id=re.search(r'\[RetailCycle\s+([^]\s]+)\]',text)
   outside=window and not window[0]<=t<=window[1]
   paired_end=full_pass and full_pass[1].casefold()=='конец' and pass_id and pass_id[1] in console_pass_starts
   if outside and not paired_end:return
   if full_pass and full_pass[1].casefold()=='начало' and pass_id:console_pass_starts.add(pass_id[1])
   if is_error:
    add('UI-console','console-error:'+relative+':'+str(line_number),'',text,t,t,'Ошибка UI',relative,line_number,visible=True)
    target=nodes[-1];target['name']=text;target['has_error']=True;target['call_errors']=[dict(time=t,file=relative,line=line_number,message=text)]
    ui_error_records.append(dict(time=t,file=relative,line=line_number,message=text,target=target,label='UI-error'))
    return
   if not full_pass and any(key in text.casefold() for key in console_ignore):return
   if not full_pass and not any(key in text.casefold() for key in console_keys):return
   add('UI-console','console:'+relative+':'+str(line_number),'',text,t,t,'Консоль UI',relative,line_number,visible=True,preserve_window=bool(full_pass))
   nodes[-1]['name']=text
   if full_pass:
    start=full_pass[1].casefold()=='начало'
    duration=re.search(r'\+\s*(\d+(?:[.,]\d+)?)\s*с\b',text) if not start else None
    label='Начало' if start else 'Конец'+(' · '+duration[1].replace('.',',')+' с' if duration else '')
    nodes[-1]['console_marker']=dict(label=label,type='full-pass-start' if start else 'full-pass-end')
    if duration:nodes[-1]['console_marker']['elapsed_seconds']=float(duration[1].replace(',','.'))
   section=re.search(r'id\s+раздела:\s*([^\s,;]+)',text,re.I)
   if section:nodes[-1]['console_marker']=dict(label=section[1],type='section')
   if 'инициализация оффлайн приложения' in text.casefold():nodes[-1]['console_marker']=dict(label='Инициализация оффлайн приложения',type='initialization')
  with consolefile.open(encoding='utf-8-sig',errors='replace') as stream:
   for ln,line in enumerate(stream,1):
    tm=re.match(r'(\d\d):(\d\d):(\d\d)\.(\d{3})(?=[ \t])',line)
    if not tm:
     if record is not None:record['text']+=line
     continue
    save_console(record);record=None;h,m,sec,ms=map(int,tm.groups());raw=((h*60+m)*60+sec)*1000+ms
    if previous-raw>43200000:day+=86400000
    previous=raw
    if not window or window[0]<=day+raw<=window[1]:
     log_start=day+raw if log_start is None else min(log_start,day+raw);log_end=day+raw if log_end is None else max(log_end,day+raw)
    # Both tab-separated and whitespace-aligned browser console records occur.
    payload=re.split(r'\[(?:INFO|WARNING|WARN|ERROR|DEBUG|LOG|TRACE)\]\s*',line,maxsplit=1,flags=re.I)
    if len(payload)==2:text=payload[1]
    else:
     columns=line.rstrip().split('\t')
     if len(columns)<8:continue
     text='\t'.join(columns[7:])
    record=dict(time=day+raw,line=ln,text=text,is_error=bool(re.search(r'\[ERROR\]',line,re.I)))
   save_console(record)
 # Error logs are small and read once; preserve multiline exception messages.
 error_records=ui_error_records;error_index={};error_threads={}
 for node in nodes:
  scope=(node['process'],str(Path(node['file']).parent))
  if node['trace']:error_index.setdefault((scope,node['trace']),[]).append(node)
  for name in set(('',node['name'])):error_threads.setdefault((scope,node['thread'],name),[]).append(node)
 # Max-end interval trees avoid scanning every operation for each untraced error.
 for key,items in error_threads.items():
  items.sort(key=lambda node:node['start']);size=1
  while size<len(items):size*=2
  ends=[float('-inf')]*(2*size)
  for i,node in enumerate(items):ends[size+i]=node['end']
  for i in range(size-1,0,-1):ends[i]=max(ends[i*2],ends[i*2+1])
  error_threads[key]=(items,size,ends)
 def error_candidates(index,t):
  if index is None:return []
  items,size,ends=index;found=[];todo=[(1,0,size)]
  while todo:
   pos,lo,hi=todo.pop()
   if lo>=len(items) or ends[pos]<t or items[lo]['start']>t:continue
   if hi-lo==1:found.append(items[lo]);continue
   mid=(lo+hi)//2;todo.extend(((pos*2,lo,mid),(pos*2+1,mid,hi)))
  return found
 errorfiles=sorted(p for p in (folder.rglob('*.log') if a.recursive else folder.glob('*.log')) if re.search(r'(?:-|_)errors(?:_\d+)?\.log$',p.name,re.I))
 progress('Чтение errors',str(len(errorfiles))+' файлов')
 for errorfile in errorfiles:
  progress('Чтение errors',errorfile.name)
  relative=str(errorfile.relative_to(folder));prefix=re.sub(r'(?:-|_)errors(?:_\d+)?\.log$','',errorfile.name,flags=re.I)
  process=re.sub(r'^\d{4}-\d{2}-\d{2}_?','',prefix) or 'Launcher'
  dm=re.search(r'\d{4}-\d{2}-\d{2}',errorfile.name);day=datetime.date.fromisoformat(dm[0]).toordinal()*86400000 if dm else 0
  previous=0;current=None;error_scope=(process,str(Path(relative).parent))
  def save_error(record):
   if record is None:return
   t,trace,ctx,thread,line_number,message=record
   if window and not window[0]<=t<=window[1]:return
   context=method(ctx) if ctx else ''
   candidates=[node for node in error_index.get((error_scope,trace),[]) if (not context or node['name']==context) and node['start']-100<=t<=node['end']+100]
   if not candidates and not trace:candidates=error_candidates(error_threads.get((error_scope,thread,context)),t)
   target=min(candidates,key=lambda node:node['duration']) if candidates else None
   detail=dict(time=t,file=relative,line=line_number,message=message.strip())
   if target is None:
    add(process,trace,trace,method(ctx) if ctx else 'Ошибка · '+message.splitlines()[0][:160],t,t,'Ошибка',relative,line_number,thread,visible=True);target=nodes[-1]
   target.setdefault('call_errors',[]).append(detail.copy());target['has_error']=True
   error_records.append(dict(time=t,file=relative,line=line_number,message=message.strip(),target=target))
  with errorfile.open(encoding='utf-8-sig',errors='replace') as stream:
   for ln,line in enumerate(stream,1):
    tm=re.match(r'(\d\d):(\d\d):(\d\d)\.(\d{3})(?=[ \t])',line)
    if not tm:
     if current:current[-1]+=line
     continue
    save_error(current);h,m,sec,ms=map(int,tm.groups());raw=((h*60+m)*60+sec)*1000+ms
    if previous-raw>43200000:day+=86400000
    previous=raw;current=None
    if window and not window[0]<=day+raw<=window[1]:continue
    log_start=day+raw if log_start is None else min(log_start,day+raw);log_end=day+raw if log_end is None else max(log_end,day+raw);c=line.rstrip().split('\t');trace=c[4] if len(c)>6 else '';ctx=c[8] if len(c)>9 else c[5] if len(c)>6 else '';thread=c[1] if len(c)>1 else ''
    current=[day+raw,trace,ctx,thread,ln,c[-1]+'\n']
   save_error(current)
 progress('Построение дерева',f'{len(nodes):,} операций; поиск инициаторов')
 # Build initiator tree: explicit trace edges first, then tight containment in the same trace/thread.
 nodes.sort(key=lambda n:(n['start'],-n['duration']));bytrace={}
 for i,n in enumerate(nodes):n['id']=i;bytrace.setdefault(n['trace'],[]).append(i)
 for i,n in enumerate(nodes):
  if i%2000==0:STATE['detail']=f'{i:,}/{len(nodes):,} операций'
  candidates=[j for j in bytrace.get(n['trace'],[]) if j!=i and nodes[j]['process']==n['process'] and nodes[j]['start']<=n['start'] and nodes[j]['end']>=n['end'] and (nodes[j]['duration']>n['duration'] or j<i) and nodes[j]['kind'] not in ('Длинная задача','SQL','Ожидание')]
  if candidates:n['parent']=min(candidates,key=lambda j:nodes[j]['duration']);n['relation']='Вложенность по trace и интервалу'
  elif n['trace'] in edges:
   parenttrace,launch=edges[n['trace']];candidates=[j for j in bytrace.get(parenttrace,[]) if j!=i and nodes[j]['start']<=launch<=nodes[j]['end'] and nodes[j]['kind'] not in ('Длинная задача','SQL','Ожидание')]
   if candidates:n['parent']=min(candidates,key=lambda j:nodes[j]['duration']);n['relation']='Инициатор по ruuid'
 progress('Проверка дерева',f'{len(nodes):,} операций')
 # Guard cycles from malformed or ambiguous logs.
 for n in nodes:
  seen={n['id']};p=n['parent']
  while p is not None:
   if p in seen:n['parent']=None;break
   seen.add(p);p=nodes[p]['parent']
 # Preserve the actual request as evidence and propagate it to ancestors.
 for node in nodes:
  if not node.get('cloud_host'):continue
  evidence=dict(method=node['name'],host=node['cloud_host'],file=node['file'],line=node['line'])
  node['cloud_evidence']=evidence;parent=node['parent']
  while parent is not None and not nodes[parent].get('cloud_evidence'):
   nodes[parent]['has_cloud_call']=True;nodes[parent]['cloud_evidence']=evidence;parent=nodes[parent]['parent']
 base=min([n['start'] for n in nodes]+([log_start] if log_start is not None else [0]));end=max([n['end'] for n in nodes]+([log_end] if log_end is not None else [base+1]))
 if window:base,end=window[0],max(window[1],end)
 for n in nodes:
  n['log_time']=f"{int(n['start']//3600000)%24:02}:{int(n['start']//60000)%60:02}:{int(n['start']//1000)%60:02}.{int(n['start'])%1000:03}"
  n['start']-=base;n['end']-=base
  for error in n.get('call_errors',[]):error['time']-=base
  n['appearance']='ui' if n['visible'] else 'background' if harfiles else 'log-only'
 meta=dict(span=max(1,end-base),files=len(files),har=len(harfiles),count=len(nodes),errors=errors,source=str(folder),origin=datetime.datetime.fromordinal(int(base//86400000)).strftime('%Y-%m-%d')+' '+f'{int(base//3600000)%24:02}:{int(base//60000)%60:02}:{int(base//1000)%60:02}',originMs=base- datetime.date(1970,1,1).toordinal()*86400000,logStart=datetime.datetime.fromordinal(int(base//86400000)).strftime('%Y-%m-%d')+' '+f'{int(base//3600000)%24:02}:{int(base//60000)%60:02}:{int(base//1000)%60:02}.{int(base)%1000:03}',logEnd=datetime.datetime.fromordinal(int(end//86400000)).strftime('%Y-%m-%d')+' '+f'{int(end//3600000)%24:02}:{int(end//60000)%60:02}:{int(end//1000)%60:02}.{int(end)%1000:03}',threshold=a.long_task_ms,console_markers=[dict(time=n['start'],node=n['id'],**n['console_marker']) for n in nodes if 'console_marker' in n],error_markers=[dict(time=e['time']-base,node=e['target']['id'],file=e['file'],line=e['line'],message=e['message'],label=e.get('label','error')) for e in error_records])
 meta['fps_samples']=[dict(time=x['time']-base,value=x['value']) for x in sorted(fps_samples,key=lambda x:x['time']) if base<=x['time']<=end]
 if window:meta['mainservice_selection']=dict(kept=[str(p.relative_to(folder)) for p in selected_mainservice],skipped=skipped_count)
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
