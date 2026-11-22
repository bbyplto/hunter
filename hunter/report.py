"""Отчёт: HTML-страница с фильтрами + CSV для Excel."""
import csv
import html
import json


def to_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["приз", "оценка", "регион", "источник", "дата", "автор", "заголовок", "ссылка", "флаги", "текст"])
        for r in rows:
            w.writerow([r["prize"], r["score"], r["region"], r["source"], (r["published"] or r["found_at"])[:16],
                        r["author"], r["title"], r["url"], " | ".join(r["flags"]),
                        (r["text"] or "").replace("\n", " ")[:500]])


def to_html(rows, path):
    data = [{k: r[k] for k in ("url", "source", "title", "text", "author", "published", "found_at",
                               "score", "flags", "region", "prize", "prizes")} for r in rows]
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    with open(path, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.replace("__DATA__", payload).replace("__COUNT__", html.escape(str(len(rows)))))


TEMPLATE = """<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Розыгрыши GTA 6 / PS5</title>
<style>
:root{--bg:#f6f5f2;--card:#fff;--ink:#1c1b19;--mute:#6b6862;--line:#e3e0da;--good:#1f7a4d;--bad:#b3261e;--mid:#a86b00}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--card:#1e1e1c;--ink:#ecebe8;--mute:#9c9890;--line:#33322f;--good:#5cc28b;--bad:#f2786d;--mid:#e0a63a}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,sans-serif}
header{padding:20px 16px 8px;max-width:1000px;margin:auto}h1{margin:0 0 4px;font-size:22px}
.bar{display:flex;flex-wrap:wrap;gap:8px;padding:8px 16px;max-width:1000px;margin:auto;position:sticky;top:0;background:var(--bg)}
input,select{font:inherit;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}
input{flex:1;min-width:180px}main{max-width:1000px;margin:auto;padding:8px 16px 40px}
.c{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:10px 0}
.top{display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:13px;color:var(--mute)}
.s{font-weight:700;border-radius:6px;padding:1px 7px;color:#fff}.g{background:var(--good)}.m{background:var(--mid)}.b{background:var(--bad)}
a{color:inherit;font-weight:600}.t{white-space:pre-wrap;margin-top:6px;max-height:7.5em;overflow:hidden;color:var(--mute)}
.f{font-size:12px;margin-top:6px;color:var(--mute)}
</style></head><body>
<header><h1>Розыгрыши GTA 6 / PS5</h1><div style="color:var(--mute)">Всего в базе: __COUNT__. Оценка — грубая антискам-проверка, не гарантия.</div></header>
<div class="bar"><input id="q" placeholder="Поиск по тексту…">
<select id="pz"><option value="">PS5 и GTA 6</option><option value="ps5">🎮 Только PS5</option><option value="gta6">🚗 Только GTA 6</option></select>
<select id="src"><option value="">Все источники</option></select>
<select id="min"><option value="0">Любая оценка</option><option value="50">≥ 50</option><option value="70">≥ 70</option></select>
<select id="reg"><option value="">Любой регион</option><option>весь мир</option><option>?</option><option>ограничен</option></select></div>
<main id="list"></main>
<script>
const D=__DATA__;const $=id=>document.getElementById(id);
[...new Set(D.map(x=>x.source))].sort().forEach(s=>{const o=document.createElement('option');o.textContent=s;$('src').append(o)});
const esc=s=>(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function draw(){const q=$('q').value.toLowerCase(),s=$('src').value,m=+$('min').value,r=$('reg').value,p=$('pz').value;
const L=D.filter(x=>(!p||x.prizes.includes(p))&&(!s||x.source==s)&&x.score>=m&&(!r||x.region==r)&&(!q||(x.title+' '+x.text+' '+x.author).toLowerCase().includes(q)));
$('list').innerHTML=L.slice(0,1500).map(x=>{const k=x.score>=70?'g':x.score>=45?'m':'b';
const safe=/^https?:/.test(x.url)?x.url:'#';
return `<div class="c"><div class="top"><span class="s ${k}">${x.score}</span><b>${x.prizes.includes('ps5')?'🎮 ':''}${x.prizes.includes('gta6')?'🚗 ':''}${esc(x.prize)}</b><b>${esc(x.source)}</b><span>${esc((x.published||x.found_at).slice(0,16).replace('T',' '))}</span><span>${esc(x.author)}</span><span>регион: ${esc(x.region)}</span></div>
<div><a href="${esc(safe)}" target="_blank" rel="noopener noreferrer">${esc(x.title||x.url)}</a></div><div class="t">${esc(x.text)}</div>
${x.flags.length?`<div class="f">${x.flags.map(esc).join(' · ')}</div>`:''}</div>`}).join('')||'<p>Ничего не найдено.</p>'}
['q','pz','src','min','reg'].forEach(i=>$(i).addEventListener('input',draw));draw();
</script></body></html>"""
