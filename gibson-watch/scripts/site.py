#!/usr/bin/env python3
"""Generate the Gibson Watch listings site (site/index.html) from database.json.

The page is published as a claude.ai Artifact (stable URL, redeployed each run).
Self-contained: no external requests; data embedded inline; light/dark themed.
Usage: python3 scripts/site.py
"""
import base64
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HERE, "database.json")
OUT = os.path.join(HERE, "site", "index.html")
THUMBS = os.path.join(HERE, "site", "thumbs")


def thumb_uri(gid):
    path = os.path.join(THUMBS, "%s.jpg" % gid)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("ascii")

# Spec target bands used for the in-target tick marks, per category.
BANDS = {
    "les_paul": {"weight": (8.3, 9.0), "nut": (1.68, 1.71), "f1": (0.79, 0.82), "f12": (0.89, 0.92)},
    "es_335": {"weight": (7.4, 8.0), "nut": (1.56, 1.60), "f1": (0.76, 0.82), "f12": (0.86, 0.94)},
}


US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
    "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
}


NYC_MARKERS = ("new york, ny", "manhattan", "brooklyn", "queens", "astoria",
               "long island city", "ridgewood, ny", "soho", "east village",
               "west village", "harlem", "williamsburg", "greenpoint", "bushwick")


def is_nyc(city_state):
    """Manhattan, Brooklyn, or Queens — not Long Island, Westchester, or NJ.
    Parentheticals often carry distance notes ('~1h from Manhattan'), but also
    real neighborhoods ('New York, NY (SoHo)') — so match the base location
    first, and let a parenthetical count only when the base names New York."""
    c = (city_state or "").lower()
    base = c.split("(")[0]
    if any(m in base for m in NYC_MARKERS):
        return True
    return "new york" in base and any(m in c for m in NYC_MARKERS)


def us_state(city_state):
    """Last valid two-letter state code in the free-text location."""
    import re
    codes = [t for t in re.findall(r"\b[A-Z]{2}\b", city_state or "") if t in US_STATES]
    return codes[-1] if codes else None


def finish_label(finish):
    """Canonical short finish name for the finish dropdown ('Washed Cherry
    Sunburst, nitro VOS' -> 'Washed Cherry Sunburst')."""
    f = (finish or "").split("(")[0].split(",")[0].strip().strip("'\"")
    return f or "Unstated"


def color_family(finish):
    """Bucket free-text finish names into filterable color families."""
    f = (finish or "").lower()
    if not f:
        return "other"
    if any(w in f for w in ("burst", "iced tea", "ice tea", "unburst", "lemon",
                            "tangerine", "tomato", "teaburst")):
        return "sunburst"
    if any(w in f for w in ("ebony", "black")):
        return "black"
    if "cherry" in f:
        return "cherry"
    if any(w in f for w in ("natural", "blonde")):
        return "natural"
    if any(w in f for w in ("walnut", "mocha", "brown")):
        return "walnut"
    if any(w in f for w in ("goldtop", "gold top")):
        return "gold"
    return "other"


def main():
    with open(DB) as f:
        db = json.load(f)
    meta = db["meta"]
    guitars = []
    for g in db["guitars"]:
        guitars.append({
            "id": g["id"], "cat": g["category"], "score": g.get("score"),
            "status": g.get("status", "ACTIVE"), "dealer": g.get("dealer"),
            "url": g.get("url"), "price": g.get("price_usd"),
            "condition": g.get("condition"), "loc": g.get("city_state"),
            "year": g.get("year"), "model": g.get("model"), "finish": g.get("finish"),
            "color": color_family(g.get("finish")),
            "finish_label": finish_label(g.get("finish")),
            "state": us_state(g.get("city_state")),
            "nyc": is_nyc(g.get("city_state")),
            "serial": g.get("serial"), "weight": g.get("weight_lbs"),
            "nut": g.get("nut_width_in"), "f1": g.get("fret1_depth_in"),
            "f12": g.get("fret12_depth_in"), "profile": g.get("neck_profile"),
            "shoulders": g.get("shoulder_description"), "radius": g.get("fingerboard_radius"),
            "pickups": g.get("pickups"), "case": g.get("case_included"),
            "mods": g.get("modifications"), "meas": g.get("measurements_source"),
            "found": g.get("date_discovered"), "confirmed": g.get("last_confirmed_active"),
            "notes": g.get("notes"), "research": g.get("research"),
            "breakdown": g.get("score_breakdown"),
            "thumb": thumb_uri(g["id"]),
            "offer": g.get("offer_intel"),
        })
    payload = json.dumps({"meta": meta, "bands": BANDS, "guitars": guitars},
                         ensure_ascii=False).replace("</", "<\\/")

    html = HTML_TEMPLATE.replace("__DATA__", payload)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(html)
    print("wrote %s (%d guitars)" % (OUT, len(guitars)))


HTML_TEMPLATE = r"""<title>Gibson Watch</title>
<style>
:root{
  --bg:#FAF6EF; --bg-raise:#FFFDF8; --ink:#251E17; --ink-soft:#6B6054; --line:#E4DBCC;
  --amber:#B07818; --amber-soft:#F3E8D2; --cherry:#8A3033; --cherry-soft:#F2E2E0;
  --good:#4A6B4F; --good-soft:#E4EBE2; --warn:#9A6A1F;
  --chip-sold:#B5B0A6;
}
@media (prefers-color-scheme: dark){:root{
  --bg:#171210; --bg-raise:#211A16; --ink:#EDE4D6; --ink-soft:#A2937F; --line:#372D25;
  --amber:#D89A3C; --amber-soft:#3A2C14; --cherry:#C96B6E; --cherry-soft:#3B2323;
  --good:#8FB894; --good-soft:#25301F; --warn:#D2A24C; --chip-sold:#5A5248;
}}
:root[data-theme="dark"]{
  --bg:#171210; --bg-raise:#211A16; --ink:#EDE4D6; --ink-soft:#A2937F; --line:#372D25;
  --amber:#D89A3C; --amber-soft:#3A2C14; --cherry:#C96B6E; --cherry-soft:#3B2323;
  --good:#8FB894; --good-soft:#25301F; --warn:#D2A24C; --chip-sold:#5A5248;
}
:root[data-theme="light"]{
  --bg:#FAF6EF; --bg-raise:#FFFDF8; --ink:#251E17; --ink-soft:#6B6054; --line:#E4DBCC;
  --amber:#B07818; --amber-soft:#F3E8D2; --cherry:#8A3033; --cherry-soft:#F2E2E0;
  --good:#4A6B4F; --good-soft:#E4EBE2; --warn:#9A6A1F; --chip-sold:#B5B0A6;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
.serif{font-family:Charter,"Bitstream Charter",Cambria,Georgia,serif}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 64px}
header{padding:28px 0 18px;border-bottom:2px solid var(--ink);margin-bottom:14px}
.eyebrow{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--amber);font-weight:600}
h1{font-family:Charter,Cambria,Georgia,serif;font-size:clamp(26px,4vw,36px);margin:2px 0 6px;text-wrap:balance}
.substat{color:var(--ink-soft);font-size:13px}
.substat b{color:var(--ink);font-variant-numeric:tabular-nums}
.controls{display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:8px 0 14px;position:sticky;top:0;background:var(--bg);z-index:5;border-bottom:1px solid var(--line)}
.seg{display:flex;border:1px solid var(--line);border-radius:6px;overflow:hidden}
.seg button{border:0;background:var(--bg-raise);color:var(--ink-soft);padding:5px 9px;font:600 11px/1 system-ui;letter-spacing:.04em;text-transform:uppercase;cursor:pointer}
.seg button.on{background:var(--ink);color:var(--bg)}
select,input[type=search]{background:var(--bg-raise);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:5px 7px;font:12px system-ui;max-width:150px}
input[type=search]{flex:1;min-width:110px}
.toggle{border:1px solid var(--line);background:var(--bg-raise);color:var(--ink-soft);border-radius:6px;padding:5px 10px;font:600 11px/1 system-ui;letter-spacing:.04em;text-transform:uppercase;cursor:pointer}
.toggle.on{background:var(--amber);border-color:var(--amber);color:var(--bg)}
#drawerdot{color:var(--amber)}
#drawerbtn.on #drawerdot{color:inherit}
#scrim{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:19}
#drawer{position:fixed;top:0;right:0;height:100%;width:min(300px,85vw);background:var(--bg-raise);border-left:1px solid var(--line);z-index:20;padding:18px;display:flex;flex-direction:column;gap:14px;transform:translateX(100%);transition:transform .22s ease;box-shadow:-8px 0 24px rgba(0,0,0,.12)}
#drawer.open{transform:translateX(0)}
@media (prefers-reduced-motion: reduce){#drawer{transition:none}}
#drawer label{display:flex;flex-direction:column;gap:5px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft);font-weight:600}
#drawer select{max-width:none;width:100%;font-size:13px;padding:7px 8px}
.drawerhead{display:flex;align-items:center;justify-content:space-between;font-family:Charter,Georgia,serif;font-size:17px;border-bottom:2px solid var(--ink);padding-bottom:8px}
.count{font-size:12px;color:var(--ink-soft);margin-left:auto;font-variant-numeric:tabular-nums}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px;margin-top:16px}
.card{background:var(--bg-raise);border:1px solid var(--line);border-radius:8px;padding:0 0 14px;display:flex;flex-direction:column;gap:10px;overflow:hidden}
.card>*:not(.photo){margin-left:16px;margin-right:16px}
.card>.toprow{margin-top:12px}
.card.sold{opacity:.55}
.photo{width:100%;height:180px;background:var(--line);display:block}
.photo img{width:100%;height:100%;object-fit:cover;display:block}
.photo.none{display:flex;align-items:center;justify-content:center;color:var(--ink-soft);font-size:11px;letter-spacing:.12em;text-transform:uppercase}
.toprow{display:flex;gap:12px;align-items:flex-start}
.scoreblock{text-align:center;min-width:52px}
.scorenum{font:700 26px/1 Charter,Georgia,serif;font-variant-numeric:tabular-nums}
.scorenum.hi{color:var(--amber)} .scorenum.mid{color:var(--ink)} .scorenum.lo{color:var(--ink-soft)}
.scorelabel{font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft)}
.titleblock{flex:1;min-width:0}
.gname{font-family:Charter,Cambria,Georgia,serif;font-size:17px;line-height:1.25;margin:0;text-wrap:balance}
.gsub{font-size:12.5px;color:var(--ink-soft);margin-top:2px}
.chips{display:flex;flex-wrap:wrap;gap:5px}
.chip{font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:2px 8px;border-radius:99px}
.chip.lp{background:var(--amber-soft);color:var(--amber)}
.chip.es{background:var(--cherry-soft);color:var(--cherry)}
.chip.active{background:var(--good-soft);color:var(--good)}
.chip.pricedrop{background:var(--good-soft);color:var(--good)}
.chip.priceup{background:var(--cherry-soft);color:var(--cherry)}
.chip.sold{background:var(--chip-sold);color:var(--bg)}
.chip.newtoday{background:var(--ink);color:var(--bg)}
.chip.offers{background:var(--amber);color:var(--bg)}
.offerline{font-size:12px;border:1px dashed var(--amber);border-radius:6px;padding:6px 9px;color:var(--ink)}
.offerline b{color:var(--amber)}
.specs{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:8px 0}
.spec{text-align:center}
.spec .v{font-variant-numeric:tabular-nums;font-weight:600;font-size:14px}
.spec .k{font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft)}
.spec .v .tick{color:var(--good);font-size:11px}
.spec .v .cross{color:var(--warn);font-size:11px}
.meta{font-size:12.5px;color:var(--ink-soft);line-height:1.45}
.meta b{color:var(--ink);font-weight:600}
.price{font:700 18px/1 Charter,Georgia,serif;font-variant-numeric:tabular-nums}
.bottomrow{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:auto}
a.listing{color:var(--amber);font-weight:600;font-size:13px;text-decoration:none;border-bottom:1px solid currentColor}
a.listing:focus-visible,button:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid var(--amber);outline-offset:2px}
details{font-size:12.5px;color:var(--ink-soft)}
details summary{cursor:pointer;font-weight:600;color:var(--ink);font-size:12px;letter-spacing:.05em;text-transform:uppercase}
details ul{margin:6px 0 0;padding-left:16px}
details li{margin-bottom:4px}
.empty{color:var(--ink-soft);padding:40px 0;text-align:center;font-style:italic}
@media (max-width:480px){.specs{grid-template-columns:repeat(2,1fr)}}
</style>
<div class="wrap">
<header>
  <div class="eyebrow">Sourcing agent · daily sweep</div>
  <h1>Gibson Watch — Les Paul &amp; ES-335 Board</h1>
  <div class="substat" id="substat"></div>
</header>
<div class="controls">
  <button id="drawerbtn" class="toggle" type="button" aria-expanded="false" title="More filters">
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" style="vertical-align:-2px"><path d="M3 5h18M7 12h10M10 19h4"/></svg>
    Filters<span id="drawerdot" hidden> ●</span>
  </button>
  <div class="seg" id="catseg">
    <button data-cat="all" class="on">All</button>
    <button data-cat="les_paul">Les Paul</button>
    <button data-cat="es_335">ES-335</button>
  </div>
  <select id="sortsel">
    <option value="score">Sort: score</option>
    <option value="price">Sort: price (low → high)</option>
    <option value="weight">Sort: weight (low → high)</option>
    <option value="new">Sort: newest find</option>
  </select>
  <button id="offbtn" class="toggle" type="button" aria-pressed="false">Offers</button>
  <button id="nybtn" class="toggle" type="button" aria-pressed="false" title="Manhattan, Brooklyn, or Queens">NYC only</button>
  <select id="nutsel">
    <option value="any">Nut: any</option>
    <option value="narrow">Nut ≤ 1.60″</option>
    <option value="mid">Nut 1.60–1.69″</option>
    <option value="wide">Nut ≥ 1.69″</option>
    <option value="unknown">Nut n/a</option>
  </select>
  <input type="search" id="q" placeholder="Search model, finish, dealer…">
  <span class="count" id="count"></span>
</div>
<div class="grid" id="grid"></div>
<div class="empty" id="empty" hidden>No guitars match.</div>
</div>
<div id="scrim" hidden></div>
<aside id="drawer" aria-label="More filters">
  <div class="drawerhead"><span>Filters</span><button id="drawerclose" class="toggle" type="button">Close</button></div>
  <label>Listings
  <select id="statussel">
    <option value="live">Live listings</option>
    <option value="all">Include sold</option>
  </select></label>
  <label>Color family
  <select id="colorsel">
    <option value="any">Any</option>
    <option value="sunburst">Sunburst / burst</option>
    <option value="black">Black / Ebony</option>
    <option value="cherry">Cherry</option>
    <option value="natural">Natural / Blonde</option>
    <option value="walnut">Walnut / Brown</option>
    <option value="gold">Goldtop</option>
    <option value="other">Other colors</option>
  </select></label>
  <label>Finish
  <select id="finishsel"><option value="any">Any</option></select></label>
  <button id="drawerreset" class="toggle" type="button">Reset these</button>
</aside>
<script>
const DATA = __DATA__;
const bands = DATA.bands;
const money = v => v==null ? "—" : "$"+Math.round(v).toLocaleString("en-US");
const esc = s => String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
function tick(cat,key,v){
  if(v==null) return "";
  const b = bands[cat] && bands[cat][key];
  if(!b) return "";
  return (v>=b[0]&&v<=b[1]) ? ' <span class="tick" title="in target band">●</span>'
                            : ' <span class="cross" title="outside target band">○</span>';
}
function spec(cat,key,label,v,unit){
  const shown = v==null ? "—" : (typeof v==="number"? v : esc(v));
  return `<div class="spec"><div class="v">${shown}${v!=null&&unit?unit:""}${typeof v==="number"?tick(cat,key,v):""}</div><div class="k">${label}</div></div>`;
}
function fracIn(v){
  // Reverb-style fraction display: snap to the nearest 32nd; "≈" marks values
  // that aren't exactly on the fraction (exact decimal stays in the tooltip).
  const whole=Math.floor(v), n32=Math.round((v-whole)*32);
  const delta=Math.abs((whole+n32/32)-v);
  if(delta>0.012) return v+"″";                 // too far from any clean fraction
  const approx = delta>0.004 ? "≈" : "";
  if(n32===0) return approx+whole+"″";
  if(n32===32) return approx+(whole+1)+"″";
  let n=n32,d=32; while(n%2===0){n/=2;d/=2;}
  return `${approx}${whole} ${n}/${d}″`;
}
function nutSpec(g){
  if(g.nut==null) return `<div class="spec"><div class="v">—</div><div class="k">Nut</div></div>`;
  return `<div class="spec"><div class="v" title="${g.nut}&quot;">${fracIn(g.nut)}${tick(g.cat,"nut",g.nut)}</div><div class="k">Nut</div></div>`;
}
function chipStatus(s){
  const m={ACTIVE:["active","Active"],"PRICE DROP":["pricedrop","Price drop"],"PRICE INCREASE":["priceup","Price up"],SOLD:["sold","Sold"],EXCLUDED:["sold","Excluded"]};
  const [cls,label]=m[s]||["active",esc(s||"")];
  return `<span class="chip ${cls}">${label}</span>`;
}
function card(g){
  const cls = g.cat==="les_paul" ? ["lp","Les Paul"] : ["es","ES-335"];
  const isNew = g.found === DATA.meta.last_run;
  const stier = g.score>=88?"hi":(g.score>=75?"mid":"lo");
  const oi = g.offer || {};
  let offerline = "";
  if (oi.offers_enabled && oi.suggested_offer_usd) {
    const bits = [];
    if (oi.days_listed != null) bits.push(`listed ${oi.days_listed}d`);
    if (oi.over_market_pct != null && oi.over_market_pct >= 5) bits.push(`~${oi.over_market_pct}% over market`);
    offerline = `<div class="offerline">Open to offers${bits.length? " · "+bits.join(" · "):""} → try <b>${money(oi.suggested_offer_usd)}</b> (−${oi.discount_pct}%)<br><span style="opacity:.75">${esc(oi.rationale||"")}</span></div>`;
  }
  const research = g.research ? `<details><summary>Community research</summary><ul>${g.research.map(b=>`<li>${esc(b)}</li>`).join("")}</ul></details>` : "";
  const notes = g.notes ? `<details><summary>Agent notes</summary><div style="margin-top:6px">${esc(g.notes)}</div></details>` : "";
  const photo = g.thumb
    ? `<a class="photo" href="${esc(g.url)}" target="_blank" rel="noopener"><img src="${g.thumb}" alt="${esc(g.model||"")}" loading="lazy"></a>`
    : `<div class="photo none">No photo</div>`;
  return `<div class="card ${(g.status==="SOLD"||g.status==="EXCLUDED")?"sold":""}">
    ${photo}
    <div class="toprow">
      <div class="scoreblock"><div class="scorenum ${stier}">${g.score==null?"—":g.score}</div><div class="scorelabel">score</div></div>
      <div class="titleblock">
        <h2 class="gname">${g.year?esc(g.year)+" ":""}${esc(g.model||"")}</h2>
        <div class="gsub">${esc(g.finish||"")}</div>
      </div>
    </div>
    <div class="chips"><span class="chip ${cls[0]}">${cls[1]}</span>${chipStatus(g.status)}${isNew?'<span class="chip newtoday">New today</span>':""}${oi.offers_enabled?'<span class="chip offers">Offers</span>':""}</div>
    <div class="specs">
      ${spec(g.cat,"weight","Weight",g.weight," lb")}
      ${nutSpec(g)}
      ${spec(g.cat,"f1","1st fret",g.f1,"″")}
      ${spec(g.cat,"f12","12th fret",g.f12,"″")}
    </div>
    <div class="meta">
      <b>${esc(g.dealer||"")}</b>${g.loc?" · "+esc(g.loc):""}<br>
      ${g.profile?"Neck: "+esc(g.profile)+"<br>":""}
      ${g.pickups?"Pickups: "+esc(g.pickups)+"<br>":""}
      ${g.serial?"Serial: "+esc(g.serial)+" · ":""}${g.meas?esc(g.meas):""}
      ${g.mods&&g.mods!=="None"?"<br>Mods: "+esc(g.mods):""}
    </div>
    ${offerline}${research}${notes}
    <div class="bottomrow">
      <span class="price">${money(g.price)}</span>
      <a class="listing" href="${esc(g.url)}" target="_blank" rel="noopener">View listing ↗</a>
    </div>
  </div>`;
}
let cat="all";
function render(){
  const status=document.getElementById("statussel").value;
  const sort=document.getElementById("sortsel").value;
  const q=document.getElementById("q").value.trim().toLowerCase();
  const nut=document.getElementById("nutsel").value;
  const color=document.getElementById("colorsel").value;
  let gs=DATA.guitars.slice();
  if(cat!=="all") gs=gs.filter(g=>g.cat===cat);
  if(color!=="any") gs=gs.filter(g=>g.color===color);
  const finish=document.getElementById("finishsel").value;
  if(finish!=="any") gs=gs.filter(g=>g.finish_label===finish);
  if(nyOnly) gs=gs.filter(g=>g.nyc);
  if(offersOnly) gs=gs.filter(g=>g.offer&&g.offer.offers_enabled);
  const drawerActive = document.getElementById("statussel").value!=="live"
    || document.getElementById("colorsel").value!=="any"
    || document.getElementById("finishsel").value!=="any";
  document.getElementById("drawerdot").hidden = !drawerActive;
  if(status==="live") gs=gs.filter(g=>g.status!=="SOLD"&&g.status!=="EXCLUDED");
  if(nut!=="any") gs=gs.filter(g=>{
    if(nut==="unknown") return g.nut==null;
    if(g.nut==null) return false;
    if(nut==="narrow") return g.nut<=1.60;
    if(nut==="mid")    return g.nut>1.60&&g.nut<1.6875;
    return g.nut>=1.6875;               // wide
  });
  if(q) gs=gs.filter(g=>[g.model,g.finish,g.dealer,g.loc,g.pickups,g.year,g.profile].join(" ").toLowerCase().includes(q));
  const key={score:g=>-(g.score??-1),price:g=>g.price??1e9,weight:g=>g.weight??1e9,new:g=>g.found?-Date.parse(g.found):0}[sort];
  gs.sort((a,b)=>key(a)<key(b)?-1:key(a)>key(b)?1:0);
  document.getElementById("grid").innerHTML=gs.map(card).join("");
  document.getElementById("empty").hidden=gs.length>0;
  document.getElementById("count").textContent=gs.length+" shown";
}
document.getElementById("catseg").addEventListener("click",e=>{
  const b=e.target.closest("button"); if(!b) return;
  cat=b.dataset.cat;
  document.querySelectorAll("#catseg button").forEach(x=>x.classList.toggle("on",x===b));
  render();
});
function rebuildFinishOptions(){
  const fam=document.getElementById("colorsel").value;
  const sel=document.getElementById("finishsel");
  const prev=sel.value;
  const pool=DATA.guitars.filter(g=>fam==="any"||g.color===fam);
  const counts={};
  pool.forEach(g=>{counts[g.finish_label]=(counts[g.finish_label]||0)+1;});
  const names=Object.keys(counts).sort((a,b)=>a.localeCompare(b));
  sel.innerHTML='<option value="any">Finish: any</option>'+
    names.map(n=>`<option value="${esc(n)}">${esc(n)} (${counts[n]})</option>`).join("");
  sel.value=names.includes(prev)?prev:"any";
}
document.getElementById("colorsel").addEventListener("change",rebuildFinishOptions);
let nyOnly=false,offersOnly=false;
document.getElementById("nybtn").addEventListener("click",e=>{
  nyOnly=!nyOnly;
  e.currentTarget.classList.toggle("on",nyOnly);
  e.currentTarget.setAttribute("aria-pressed",String(nyOnly));
  render();
});
document.getElementById("offbtn").addEventListener("click",e=>{
  offersOnly=!offersOnly;
  e.currentTarget.classList.toggle("on",offersOnly);
  e.currentTarget.setAttribute("aria-pressed",String(offersOnly));
  render();
});
const drawer=document.getElementById("drawer"),scrim=document.getElementById("scrim");
function setDrawer(open){
  drawer.classList.toggle("open",open);
  scrim.hidden=!open;
  document.getElementById("drawerbtn").setAttribute("aria-expanded",String(open));
}
document.getElementById("drawerbtn").addEventListener("click",()=>setDrawer(!drawer.classList.contains("open")));
document.getElementById("drawerclose").addEventListener("click",()=>setDrawer(false));
scrim.addEventListener("click",()=>setDrawer(false));
document.addEventListener("keydown",e=>{if(e.key==="Escape")setDrawer(false);});
document.getElementById("drawerreset").addEventListener("click",()=>{
  document.getElementById("statussel").value="live";
  document.getElementById("colorsel").value="any";
  rebuildFinishOptions();
  document.getElementById("finishsel").value="any";
  render();
});
["statussel","sortsel","nutsel","colorsel","finishsel"].forEach(id=>document.getElementById(id).addEventListener("change",render));
rebuildFinishOptions();
document.getElementById("q").addEventListener("input",render);
const m=DATA.meta, live=DATA.guitars.filter(g=>g.status!=="SOLD"&&g.status!=="EXCLUDED").length;
document.getElementById("substat").innerHTML=
  `<b>${live}</b> live listings · <b>${DATA.guitars.length}</b> tracked all-time · last sweep <b>${esc(m.last_run)}</b> · run #<b>${m.run_count}</b> — ● spec in target band, ○ outside`;
render();
</script>
"""


if __name__ == "__main__":
    main()
