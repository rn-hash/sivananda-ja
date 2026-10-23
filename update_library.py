#!/usr/bin/env python3
"""library.html（訳書ライブラリ目次）自動再生成スクリプト。
新しい訳書が repo に置かれたら、このスクリプトが catalog.json の定義と
実ファイルの有無を突き合わせて library.html を再生成する。
catalog.json に無い新規HTMLが repo 直下・サブフォルダにあれば「未登録」として
警告リストに出す（人間またはRelmesがcatalogへ追加するまでメニューに出ない）。

使い方:
  python3 update_library.py           # 再生成 + 未登録チェック
  python3 update_library.py --check   # 再生成せず未登録チェックのみ
"""
import json, os, re, sys

REPO = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(REPO, 'catalog.json')
LIB = os.path.join(REPO, 'library.html')

# catalog.json: {"sections": [{"title": ..., "items": [{"page": "path/relative.html", "title": ..., "desc": ...}]}]}
cat = json.load(open(CATALOG, encoding='utf-8'))

CSS = open(os.path.join(REPO, 'library_css.html'), encoding='utf-8').read().strip()

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

parts = [f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>シヴァナンダ 日本語訳ライブラリ — 目次</title>
{CSS}
</head>
<body>
<div class="wrap">
<h1>シヴァナンダ 日本語訳ライブラリ<small>DLS聖典・実践書・一覧 — 全訳と実践書の目次</small></h1>
<div class="meta">
DLS（神聖生活協会・シヴァナンダ本人創設の系統）の無料頒布原典を底本に、個人的学習用に作成した日本語訳・実践書・一覧の目次。すべて無料公開。<br>
iPhoneからはこのページをお気に入りに入れて、ここから各訳書へ入るのが早道です。
</div>
''']
n_items = 0
for sec in cat['sections']:
    items_html = []
    for it in sec['items']:
        page = it['page']
        if os.path.exists(os.path.join(REPO, page)):
            n_items += 1
            items_html.append(
                f'<li class="item"><a class="t" href="{esc(page)}">{esc(it["title"])}</a>'
                f'<div class="d">{esc(it["desc"])}</div></li>')
        else:
            items_html.append(f'<!-- MISSING: {page} -->')
    if items_html:
        parts.append(f'<h2>{esc(sec["title"])}</h2>\n<ul class="menu">\n' + '\n'.join(items_html) + '\n</ul>')

parts.append(f'''
<div class="foot">
著作権：(C) The Divine Life Trust Society ― 無償頒布は公式方針・商用出版は許諾制（本部書面申請）。<br>
訳出・作成：2026年・非商用の個人的学習用試訳。原著は DLS（dlshq.org）無料頒布版。<br>
この目次は catalog.json + update_library.py から自動生成されている。
</div>
</div>
</body>
</html>''')

open(LIB, 'w', encoding='utf-8').write('\n'.join(parts))

# ---- unregistered new HTML detection ----
catalog_pages = {it['page'] for sec in cat['sections'] for it in sec['items']}
known_ok = {'README.md'}
EXCLUDE = {'library.html', 'update_library.py'}
unreg = []
for root, dirs, files in os.walk(REPO):
    dirs[:] = [d for d in dirs if d not in ('.git', 'figures')]
    for f in files:
        if f.endswith('.html'):
            rel = os.path.relpath(os.path.join(root, f), REPO)
            if rel not in catalog_pages and rel not in EXCLUDE:
                # skip tiny fragments and old-version files
                size = os.path.getsize(os.path.join(root, f))
                if size > 5000:
                    unreg.append((rel, size))

if unreg:
    print("未登録のHTML（catalog.jsonへの追加が必要）:")
    for rel, size in sorted(unreg):
        print(f"  {rel}  ({size} bytes)")
else:
    print("未登録HTMLなし")

print(f"library.html 再生成: {n_items} items")
