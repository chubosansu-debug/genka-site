"""飲食店の計算ツール（原価率・売価・歩留まり・FL比率・メニュー全体の原価率）を静的ページで出力する。

計算はすべてブラウザの中で行い、入力した数字はどこにも送らない。
"""
import html
import pathlib

SITE_URL = "https://genkaritsu.com"
SITE_NAME = "飲食店の原価計算"
OUT = pathlib.Path(__file__).parent / "site"

CSS = """
:root{--bg:#fbfaf7;--fg:#222;--muted:#666;--line:#e3e0d8;--accent:#b5541c;--card:#fff;--ok:#2e7d32;--ng:#c4301b}
@media (prefers-color-scheme:dark){:root{--bg:#1a1816;--fg:#eee;--muted:#aaa;--line:#38342f;--accent:#f0a06a;--card:#24211e;--ok:#7cc47f;--ng:#f07060}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif}
main,header,footer{max-width:760px;margin:0 auto;padding:0 16px}header{padding-top:16px}header a{color:var(--fg);text-decoration:none;font-weight:700}
nav{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:.9rem;margin-top:4px}
h1{font-size:1.5rem;line-height:1.4;margin:.6em 0 .3em}h2{font-size:1.15rem;margin:1.8em 0 .5em;border-left:4px solid var(--accent);padding-left:8px}
.muted{color:var(--muted);font-size:.9rem}a{color:var(--accent)}
.tool{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
label{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:6px 0;border-bottom:1px dashed var(--line)}
input,select{font:inherit;width:9em;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);text-align:right}
select{text-align:left;width:auto}.out{margin-top:10px;display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px}
.out div{background:var(--bg);border-radius:8px;padding:8px 10px}.out b{display:block;font-size:1.35rem}.ok{color:var(--ok)}.ng{color:var(--ng)}
table{width:100%;border-collapse:collapse;font-size:.95rem}th,td{padding:4px 6px;border-bottom:1px solid var(--line);text-align:right}
th:first-child,td:first-child{text-align:left}td input{width:100%}.ts{overflow-x:auto}
button{font:inherit;padding:6px 12px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);cursor:pointer}
footer{margin-top:40px;padding-bottom:40px;font-size:.85rem;color:var(--muted);border-top:1px solid var(--line)}
"""

# 共通の小さな関数。n() は空欄やカンマ入りを数値にする。
JS_COMMON = """<script>
const $=id=>document.getElementById(id);
const n=id=>{const v=parseFloat(String($(id).value).replace(/[,，円%％\\s]/g,''));return isFinite(v)?v:NaN};
const yen=v=>isFinite(v)?Math.round(v).toLocaleString()+'円':'—';
const pc=v=>isFinite(v)?(Math.round(v*10)/10).toFixed(1)+'%':'—';
const exTax=(p,mode)=>mode==='in'?p/1.1:p;
function bind(f){document.querySelectorAll('input,select').forEach(e=>e.addEventListener('input',f));f()}
</script>"""

PAGES = []


def page(path, title, desc, body, script):
    nav = " ".join(f'<a href="{p}">{t}</a>' for p, t, *_ in NAV)
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{SITE_URL}{path}">
<style>{CSS}</style></head><body>
<header><a href="/">{SITE_NAME}</a><nav>{nav}</nav></header><main>{body}</main>
<footer><p>計算はこのページの中だけで行い、入力した数字はどこにも送信・保存しません。</p>
<p>税込の売価は外食の消費税10%で税抜に直しています。軽減税率（持ち帰り8%）は対象外です。</p>
<p><a href="/about.html">このサイトについて</a></p></footer>{JS_COMMON}<script>{script}</script></body></html>"""


def field(id_, label, value="", unit=""):
    return f'<label>{label}<span><input id="{id_}" inputmode="decimal" value="{value}"> {unit}</span></label>'


TAX = '<label>売価の入れ方<select id="tax"><option value="in">税込で入れる</option><option value="ex">税抜で入れる</option></select></label>'

NAV = [
    ("/", "原価率・売価"),
    ("/budomari.html", "歩留まり"),
    ("/menu.html", "メニュー全体"),
    ("/fl.html", "FL比率"),
    ("/saji.html", "大さじ・小さじ"),
]

# ---------- 1. 原価率・売価 ----------
INDEX = f"""
<h1>原価率の計算と、目標原価率からの売価の逆算</h1>
<p class="muted">数字を入れるとすぐ計算します。原価率は税抜の売価で割っています。</p>

<h2>原価率を出す</h2>
<div class="tool">
{TAX}
{field("p1", "売価", "980", "円")}
{field("c1", "1人前の原価", "300", "円")}
<div class="out"><div>原価率<b id="r1">—</b></div><div>粗利（税抜）<b id="g1">—</b></div><div>税抜の売価<b id="e1">—</b></div></div>
</div>

<h2>目標の原価率から売価を出す</h2>
<div class="tool">
{field("c2", "1人前の原価", "300", "円")}
{field("t2", "目標の原価率", "30", "%")}
<div class="out"><div>税抜の売価<b id="e2">—</b></div><div>税込の売価<b id="i2">—</b></div><div>粗利（税抜）<b id="g2">—</b></div></div>
<p class="muted">税込の売価は1円単位です。メニューに載せるときは、きりのいい値段に合わせてください。</p>
</div>

<h2>計算式</h2>
<ul>
<li>原価率 ＝ 原価 ÷ 税抜の売価 × 100</li>
<li>売価（税抜）＝ 原価 ÷ 目標の原価率</li>
<li>税抜の売価 ＝ 税込の売価 ÷ 1.1</li>
</ul>
<p><a href="/budomari.html">皮や骨を除いた分まで入れて1人前の原価を出す → 歩留まりの計算</a></p>
"""
INDEX_JS = """bind(()=>{
const e=exTax(n('p1'),$('tax').value),c=n('c1');
$('e1').textContent=yen(e);$('r1').textContent=pc(c/e*100);$('g1').textContent=yen(e-c);
const c2=n('c2'),t=n('t2')/100,e2=c2/t;
$('e2').textContent=yen(e2);$('i2').textContent=yen(e2*1.1);$('g2').textContent=yen(e2-c2);
});"""

# ---------- 2. 歩留まり ----------
BUDOMARI = f"""
<h1>歩留まりを入れた1人前の原価の計算</h1>
<p class="muted">仕入れた重さのうち、実際に料理に使える割合が歩留まりです。皮・骨・筋・芯などを除いた分、使える部分の単価は上がります。</p>
<div class="tool">
{field("u", "仕入れ単価（1kgあたり）", "1800", "円")}
{field("y", "歩留まり", "70", "%")}
{field("g", "1人前に使う量（下処理後）", "120", "g")}
<div class="out"><div>使える部分の1kg単価<b id="k">—</b></div><div>1人前の原価<b id="o">—</b></div><div>1人前に必要な仕入れ量<b id="b">—</b></div></div>
</div>
<h2>計算式</h2>
<ul>
<li>使える部分の1kg単価 ＝ 仕入れ単価 ÷ 歩留まり</li>
<li>1人前の原価 ＝ 使える部分の1kg単価 × 1人前の量（g）÷ 1000</li>
<li>1人前に必要な仕入れ量 ＝ 1人前の量 ÷ 歩留まり</li>
</ul>
<p class="muted">歩留まりは食材・部位・切り方・仕入れ先で大きく変わります。決まった数字はないので、自分の店で何回か量って入れてください。</p>
"""
BUDOMARI_JS = """bind(()=>{
const u=n('u'),y=n('y')/100,g=n('g');
$('k').textContent=yen(u/y);$('o').textContent=yen(u/y*g/1000);
$('b').textContent=isFinite(g/y)?Math.round(g/y)+'g':'—';
});"""

# ---------- 3. メニュー全体 ----------
MENU = """
<h1>メニュー全体の原価率（出数で平均）</h1>
<p class="muted">品ごとの原価率を単純に平均すると、よく出る品の影響が入りません。出数をかけて店全体の原価率を出します。売価は税込で入れてください。</p>
<div class="tool">
<div class="ts"><table><thead><tr><th>品名</th><th>売価(税込)</th><th>原価</th><th>出数</th><th>原価率</th></tr></thead><tbody id="rows"></tbody></table></div>
<p><button id="add" type="button">行を足す</button></p>
<div class="out"><div>全体の原価率<b id="tr">—</b></div><div>売上（税抜）<b id="ts">—</b></div><div>原価の合計<b id="tc">—</b></div></div>
</div>
<h2>計算式</h2>
<ul><li>全体の原価率 ＝ Σ（原価 × 出数）÷ Σ（税抜の売価 × 出数）× 100</li></ul>
"""
MENU_JS = """
const ex=[['からあげ定食',980,320,40],['焼き魚定食',1100,420,25],['日替わり',850,300,60]];
function row(v){const tr=document.createElement('tr');tr.innerHTML=`<td><input value="${v[0]}" style="text-align:left"></td><td><input inputmode="decimal" value="${v[1]}"></td><td><input inputmode="decimal" value="${v[2]}"></td><td><input inputmode="decimal" value="${v[3]}"></td><td class="r">—</td>`;
$('rows').appendChild(tr);tr.querySelectorAll('input').forEach(e=>e.addEventListener('input',calc))}
const num=e=>{const v=parseFloat(String(e.value).replace(/[,，円\\s]/g,''));return isFinite(v)?v:NaN};
function calc(){let s=0,c=0;$('rows').querySelectorAll('tr').forEach(tr=>{const i=tr.querySelectorAll('input');
const p=num(i[1])/1.1,k=num(i[2]),q=num(i[3]);tr.querySelector('.r').textContent=pc(k/p*100);
if(isFinite(p)&&isFinite(k)&&isFinite(q)){s+=p*q;c+=k*q}});
$('tr').textContent=s?pc(c/s*100):'—';$('ts').textContent=yen(s);$('tc').textContent=yen(c)}
ex.forEach(row);$('add').onclick=()=>{row(['','','','']);calc()};calc();
"""

# ---------- 4. FL比率 ----------
FL = f"""
<h1>人件費率とFL比率の計算</h1>
<p class="muted">F＝食材・ドリンクの原価（Food）、L＝人件費（Labor）。売上に対してこの2つでどれだけ使っているかを見ます。月の数字でも、1日の数字でも使えます。</p>
<div class="tool">
{TAX}
{field("s", "売上", "3000000", "円")}
{field("f", "食材・ドリンクの原価", "960000", "円")}
{field("l", "人件費", "870000", "円")}
<div class="out"><div>原価率（F）<b id="fr">—</b></div><div>人件費率（L）<b id="lr">—</b></div><div>FL比率<b id="flr">—</b></div><div>残り（税抜）<b id="rest">—</b></div></div>
</div>
<h2>計算式</h2>
<ul>
<li>原価率 ＝ 食材・ドリンクの原価 ÷ 税抜の売上 × 100</li>
<li>人件費率 ＝ 人件費 ÷ 税抜の売上 × 100</li>
<li>FL比率 ＝ 原価率 ＋ 人件費率</li>
</ul>
<p class="muted">FL比率は、ドリンクの原価も含めて55%が理想です。業態・家賃・席数で適正は変わります。人件費に社会保険料や賄いを含めるかで数字が変わるので、毎回同じ範囲で比べてください。</p>
"""
FL_JS = """bind(()=>{
const s=exTax(n('s'),$('tax').value),f=n('f'),l=n('l');
$('fr').textContent=pc(f/s*100);$('lr').textContent=pc(l/s*100);$('flr').textContent=pc((f+l)/s*100);$('rest').textContent=yen(s-f-l);
});"""


# ---------- 5. 大さじ・小さじの重さ ----------
# 出典：広島市「調味料 計量カップ・計量スプーンの重量換算表」（参考：厚生労働省 国民健康・栄養調査 食品番号表、
# 女子栄養大学出版部 調理のためのベーシックデータ）。(名前, 小さじ, 大さじ, 1カップ) 単位 g。None は表に記載なし
# (名前, 小さじg, 大さじg, 1カップg, 炭水化物g/100g, 食塩相当量g/100g, 成分表の食品名)
# 炭水化物・食塩相当量：文部科学省「日本食品標準成分表2020年版（八訂）」。None は種類で大きく違うので出さない
SAJI = [
    ("水", 5, 15, 200, 0, 0, ""), ("酒", 5, 15, 200, 4.9, 0, "清酒 普通酒"), ("酢", 5, 15, 200, 2.4, 0, "穀物酢"),
    ("レモン汁", 5, 15, 200, 8.6, 0, "レモン 果汁 生"),
    ("しょうゆ", 6, 18, 240, 7.9, 14.5, "こいくちしょうゆ"), ("みりん", 6, 18, 240, 43.2, 0, "本みりん"),
    ("ぽん酢しょうゆ", 6, 18, 240, 10.8, 7.8, "ぽん酢しょうゆ 市販品"), ("みそ", 6, 18, None, 21.9, 12.4, "米みそ 淡色辛みそ"),
    ("塩", 6, 18, None, 0, 99.5, "食塩"), ("砂糖", 3, 9, 130, 99.3, 0, "上白糖"), ("はちみつ", 7, 21, 280, 81.9, 0, "はちみつ"),
    ("植物油", 4, 12, 180, 0, 0, "調合油"), ("バター", 4, 12, 180, 0.2, 1.9, "有塩バター"),
    ("マヨネーズ", 4, 12, 190, 3.6, 1.9, "マヨネーズ 全卵型"), ("ドレッシング", 6, 17, None, None, None, ""),
    ("小麦粉", 3, 9, 110, 75.8, 0, "薄力粉 1等"), ("片栗粉", 3, 9, 130, 81.6, 0, "じゃがいもでん粉"),
    ("パン粉", 1, 3, 40, 63.4, 1.2, "パン粉 乾燥"), ("ごま", 3, 9, 130, 18.5, 0, "ごま いり"), ("きなこ", 2, 5, 65, 28.5, 0, "きな粉 黄大豆 全粒大豆"),
    ("顆粒コンソメ", 3, 9, None, None, None, ""), ("だしの素", 2, 6, None, 31.1, 40.6, "顆粒和風だし"),
    ("練りがらし", 6, None, None, 40.1, 7.4, "からし 練り"),
    # 味の素(株)の公表値：小さじ1＝約4g（お客様相談センター）、100gあたり 炭水化物24.1g・食塩相当量29.76g（業務用1kg袋）。大さじは小さじ×3で計算
    ("うま味調味料（ハイミー®）", 4, 12, None, 24.1, 29.76, ""),
    # 味の素®：小さじの重さは非公表。4〜5gという目安の真ん中4.5gで仮に計算。成分は70g瓶の表示（0.5gあたり 炭水化物0.12g・食塩相当量0.15g）
    ("うま味調味料（味の素®）※目安", 4.5, 13.5, None, 24.0, 30.0, ""),
]
_g = lambda v: "-" if v is None else str(v)
_r = lambda w, per: "-" if w is None or per is None else f"{w * per / 100:.1f}"
SAJI_ROWS = "".join(f"<tr><td>{a}</td><td>{_g(b)}</td><td>{_g(c)}</td><td>{_g(d)}</td><td>{_r(c, sa)}</td><td>{_r(c, ca)}</td></tr>"
                    for a, b, c, d, ca, sa, _ in SAJI)
SAJI_OPTS = "".join(f'<option value="{b}" data-o="{c}" data-s="{"" if sa is None else sa}" data-c="{"" if ca is None else ca}">{a}</option>'
                    for a, b, c, d, ca, sa, _ in SAJI if c)
SAJI_SRC = "、".join(f"{a}＝{f}" for a, b, c, d, ca, sa, f in SAJI if f and a != f)
SAJI_HTML = f"""
<h1>大さじ・小さじは何グラム？調味料の早見表</h1>
<p class="muted">大さじ1＝15ml、小さじ1＝5ml、1カップ＝200ml。すりきりで量ったときの重さと、大さじ1杯に入っている塩分・炭水化物の量です。</p>
<p class="muted">大さじ・小さじは、忙しいと山盛りや目分量になりやすく、味がぶれる原因になります。決まったレシピはgに直しておくと、誰が作っても同じ味に近づきます。</p>

<h2>早見表（単位 g）</h2>
<div class="ts"><table><thead><tr><th>調味料</th><th>小さじ1</th><th>大さじ1</th><th>1カップ</th><th>塩分<br><small>大さじ1</small></th><th>炭水化物<br><small>大さじ1</small></th></tr></thead><tbody>{SAJI_ROWS}</tbody></table></div>

<h2>杯数とグラムを換算する</h2>
<div class="tool">
<label>調味料<select id="it">{SAJI_OPTS}</select></label>
{field("os", "大さじ", "2", "杯")}
{field("ks", "小さじ", "0", "杯")}
<div class="out"><div>合計の重さ<b id="sg">—</b></div><div>塩分<b id="ss">—</b></div><div>炭水化物<b id="sc">—</b></div></div>
{field("gg", "逆に、グラムから", "30", "g")}
<div class="out"><div>大さじだと<b id="so">—</b></div><div>小さじだと<b id="sk">—</b></div></div>
</div>

<h2>大さじ1杯の原価</h2>
<div class="tool">
<p class="muted">上で選んだ調味料で計算します。</p>
{field("bp", "1本（1袋）の値段", "450", "円")}
{field("bq", "中身の量", "1000", "")}
<label>中身の単位<select id="bu"><option value="ml">ml</option><option value="g">g</option></select></label>
<div class="out"><div>大さじ1の原価<b id="co">—</b></div><div>小さじ1の原価<b id="ck">—</b></div></div>
<p class="muted">mlで入れたときは、表の重さ（大さじ1の重さ÷15ml）でグラムに直しています。</p>
</div>

<p class="muted">出典：広島市「調味料 計量カップ・計量スプーンの重量換算表」（同表の参考資料：厚生労働省 国民健康・栄養調査 食品番号表、女子栄養大学出版部「調理のためのベーシックデータ」）。
銘柄・粒の大きさ・量り方で実際の重さは変わります。</p>
<p class="muted">うま味調味料（ハイミー®）：味の素株式会社の公表値（小さじ1＝約4g、100gあたり炭水化物24.1g・食塩相当量29.76g）。大さじは小さじ×3で計算しています。
「味の素®」は小さじの重さが公表されていないため、一般に言われる4〜5gの真ん中の4.5gで仮に計算した目安です。成分は商品の表示（5ふり＝0.5gあたり炭水化物0.12g・食塩相当量0.15g）から計算しています。なお1ふりは約0.1gです。</p>
<p class="muted">塩分（食塩相当量）・炭水化物：文部科学省「日本食品標準成分表2020年版（八訂）」の100gあたりの値から計算。使った食品：{SAJI_SRC}。
ドレッシング・顆粒コンソメは種類で大きく違うので出していません。商品の栄養成分表示があれば、そちらが正確です。
糖度（Brix）は成分表にないため、炭水化物の量を載せています。砂糖・みりんなど甘みの多い調味料ほど炭水化物が多くなります。</p>
"""
SAJI_JS = """bind(()=>{
const k=+$('it').value,o=+$('it').selectedOptions[0].dataset.o;const g=n('os')*o+n('ks')*k;
$('sg').textContent=isFinite(g)?Math.round(g*10)/10+'g':'—';
const op=$('it').selectedOptions[0].dataset,f=v=>v===''||!isFinite(g)?'—':(Math.round(g*v/100*10)/10)+'g';$('ss').textContent=f(op.s);$('sc').textContent=f(op.c);
const gg=n('gg');$('so').textContent=isFinite(gg)?Math.round(gg/o*10)/10+'杯':'—';$('sk').textContent=isFinite(gg)?Math.round(gg/k*10)/10+'杯':'—';
const per=$('bu').value==='ml'?n('bp')/(n('bq')*k/5):n('bp')/n('bq');
$('co').textContent=isFinite(per)?(Math.round(per*o*10)/10)+'円':'—';$('ck').textContent=isFinite(per)?(Math.round(per*k*10)/10)+'円':'—';
});"""

ABOUT = """
<h1>このサイトについて</h1>
<p>飲食店の現場でよく使う計算を、スマホでもすぐできるようにまとめたページです。原価表を作るほどでもないときの確かめ算に使ってください。</p>
<p>入力した数字はブラウザの中で計算するだけで、どこにも送信・保存しません。</p>
<p>計算結果は目安です。実際の値付けや経営判断は、ご自身の数字で確かめてください。</p>
"""


def main():
    OUT.mkdir(exist_ok=True)
    pages = [
        ("/", "index.html", "原価率の計算・売価の逆算｜飲食店の原価計算", "売価と1人前の原価から原価率を、目標の原価率から売価を計算します。税込・税抜どちらでも入力できます。", INDEX, INDEX_JS),
        ("/budomari.html", "budomari.html", "歩留まりを入れた原価の計算｜飲食店の原価計算", "仕入れ単価と歩留まりから、使える部分の単価と1人前の原価を計算します。", BUDOMARI, BUDOMARI_JS),
        ("/menu.html", "menu.html", "メニュー全体の原価率の計算（出数で平均）｜飲食店の原価計算", "品ごとの売価・原価・出数から、店全体の原価率を計算します。", MENU, MENU_JS),
        ("/fl.html", "fl.html", "FL比率・人件費率の計算｜飲食店の原価計算", "売上・食材とドリンクの原価・人件費から原価率・人件費率・FL比率を計算します。", FL, FL_JS),
        ("/saji.html", "saji.html", "大さじ・小さじは何グラム？調味料の早見表｜飲食店の原価計算", "しょうゆ・砂糖・塩・みりんなど調味料の大さじ・小さじ・1カップの重さの早見表と、杯数⇔グラムの換算、大さじ1杯の原価計算。", SAJI_HTML, SAJI_JS),
        ("/about.html", "about.html", "このサイトについて｜飲食店の原価計算", "飲食店の原価計算サイトについて。", ABOUT, ""),
    ]
    for path, fn, title, desc, body, js in pages:
        (OUT / fn).write_text(page(path, title, desc, body, js), encoding="utf-8")
    urls = "".join(f"<url><loc>{SITE_URL}{p}</loc></url>" for p, *_ in pages)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    main()
