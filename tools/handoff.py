"""Writes the developer handoff of direction 7 into "HANDOFF BENTLEY/": the
mockup as Alex made it, cleaned, and only the files it uses.

   index7.html -> index.html, inventory7.html -> inventory.html,
   vehicles7/<stock>.html -> vehicles/<stock>.html

Cleaning, all mechanical — the rendered page does not change:
  - look 2 (Satin Linen, the client's choice) becomes the only look: every
    selector is resolved for data-look="2"; rules for looks 1, 3 and 4 go,
    and so does the ?look= switch in the head;
  - rules that only apply with the motion layer (.motion, .ready) go — the
    page is static (client, 2026-10-04) and nothing ever sets that class;
  - rules for the dashboard's framed preview (data-framed) go;
  - cache stamps (?v=), HTML comments and long working notes in the CSS go;
    short section headings stay;
  - files get plain names; assets are copied only when a page, a sheet or a
    script refers to them.
Run: python3 tools/handoff.py   (then verify against index7.html)"""
import os, re, shutil

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
OUT = ROOT + 'HANDOFF BENTLEY/'

CSS = {  # source -> handoff name, in the order the pages load them
    'css/system.css':     'css/tokens.css',
    'css/index7.css':     'css/site.css',
    'css/cards.css':      'css/cards.css',
    'css/inventory7.css': 'css/inventory.css',
    'css/vehicle7.css':   'css/vehicle.css',
    'css/day7.css':       'css/theme.css',
    'css/static7.css':    'css/static.css',
    'css/subpages7.css':  'css/subpages.css',
}
JS = {
    'js/page7.js':     'js/page.js',
    'js/index7.js':    'js/home.js',
    'js/inventory.js': 'js/inventory.js',
    'js/vehicle.js':   'js/vehicle.js',
    'js/sub7.js':      'js/sub.js',
}
PAGES = {'index7.html': 'index.html', 'inventory7.html': 'inventory.html',
         # the inner pages (tools/subpages7.py): about, contact, finance
         'about7.html': 'about.html', 'contact7.html': 'contact.html', 'finance7.html': 'finance.html',
         'parts7.html': 'parts.html', 'sell7.html': 'sell.html',
         'calculator7.html': 'calculator.html', 'bentayga-speed7.html': 'bentayga-speed.html',
         'flying-spur7.html': 'flying-spur.html', 'torcal7.html': 'torcal.html',
         'continental-gt7.html': 'continental-gt.html', 'continental-gtc7.html': 'continental-gtc.html'}

def read(p): return open(ROOT + p, encoding='utf-8').read()

# --- CSS ------------------------------------------------------------------
def keep_comment(m):
    t = m.group(0)
    # a short section heading ("/* --- 4 · Scenes ---- */") stays; notes go
    if len(t) < 120 and re.match(r'/\*\s*(-{2,}|={3,})', t) and '\n' not in t:
        return t
    return ''

def split_top(s, sep=','):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '([': depth += 1
        elif ch in ')]': depth -= 1
        if ch == sep and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return out

THEME = '.theme-satin'   # set on <html>: the look the client chose
def resolve(sel):
    """the selector as it applies on the handoff page, or None if it never does.
    Every condition that always holds there (look 2, no motion layer) becomes
    one .theme-satin on <html>, so the selector keeps exactly the weight it
    had and the cascade does not move."""
    s = sel.strip()
    # never true here: no motion layer, never framed — so :not() of them always is
    ALWAYS = (':not(.motion)', ':not(.ready)', ':not([data-framed])')
    held = sum(s.count(a) for a in ALWAYS)
    for a in ALWAYS: s = s.replace(a, '')
    if re.search(r'\.motion\b|\.ready\b|data-framed', s):
        return None
    for m in list(re.finditer(r':is\(([^()]*data-look[^()]*)\)', s)):
        looks = re.findall(r'data-look="(\d)"', m.group(1))
        if '2' not in looks: return None
        s = s.replace(m.group(0), '', 1); held += 1
    for m in list(re.finditer(r':not\(\[data-look="(\d)"\]\)', s)):
        if m.group(1) == '2': return None
        s = s.replace(m.group(0), '', 1); held += 1
    for m in list(re.finditer(r'\[data-look="(\d)"\]', s)):
        if m.group(1) != '2': return None
        s = s.replace(m.group(0), '', 1); held += 1
    s = re.sub(r'\s+', ' ', s).strip()
    if held:
        tag = THEME * held
        if s.startswith('html'):    s = 'html' + tag + s[4:]
        elif s.startswith(':root'): s = ':root' + tag + s[5:]
        elif s == '' or s[0] in ' >+~': s = 'html' + tag + (' ' + s if s else '')
        else: s = 'html' + tag + ' ' + s   # the condition sat on <html>
    return s

def blocks(css):
    """top-level (prelude, body) pairs"""
    i, n, out = 0, len(css), []
    while i < n:
        j = css.find('{', i)
        if j < 0:
            tail = css[i:].strip()
            if tail: out.append((tail, None))
            break
        pre = css[i:j]
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == '{': depth += 1
            elif css[k] == '}': depth -= 1
            k += 1
        out.append((pre, css[j + 1:k - 1]))
        i = k
    return out

NESTED = ('@media', '@supports', '@container', '@layer')
def clean(css, stats):
    res = []
    for pre, body in blocks(css):
        p = pre.strip()
        if body is None:            # a bare statement such as @import ...;
            res.append(pre); continue
        lead = pre[:len(pre) - len(pre.lstrip())]
        # comments that sat before the prelude stay with it
        cm = ''.join(re.findall(r'/\*.*?\*/\s*', p, flags=re.S))
        q = re.sub(r'/\*.*?\*/', '', p, flags=re.S).strip()
        if q.startswith(NESTED):
            inner = clean(body, stats)
            indent = lead.split('\n')[-1]
            if inner.strip(): res.append(f'{lead}{cm}{q} {{{inner.rstrip()}\n{indent}}}')
        elif q.startswith('@'):
            res.append(f'{lead}{cm}{q} {{{body}}}')
        else:
            sel = q
            parts = [resolve(x) for x in split_top(sel)]
            kept = [x for x in parts if x]
            stats['selectors'] += len(parts) - len(kept)
            if not kept:
                stats['rules'] += 1; continue
            res.append(f'{lead}{cm}{", ".join(kept)} {{{body}}}')
    return ''.join(res)

def sheet(src):
    css = read(src)
    # the token file is the design system's source: its notes stay
    if src != 'css/system.css':
        css = re.sub(r'/\*.*?\*/', keep_comment, css, flags=re.S)
    stats = {'rules': 0, 'selectors': 0}
    css = clean(css, stats)
    css = re.sub(r'[ \t]+\n', '\n', css)
    css = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', css).strip() + '\n'
    return HEADS.get(src, '') + css, stats

HEADS = {
    'css/system.css': '',   # keeps its own header
    'css/index7.css': '/* Bentley Palm Beach — the site: header, hero, chapters, rails, footer.\n   Loads after tokens.css on every page. */\n\n',
    'css/cards.css': '/* Bentley Palm Beach — the vehicle card (home rail and the listing). */\n\n',
    'css/inventory7.css': '/* Bentley Palm Beach — the listing (SRP): filters, grid, sort. */\n\n',
    'css/vehicle7.css': '/* Bentley Palm Beach — the vehicle page (VDP): head, price plate, gallery,\n   360, lightbox, specification, enquiry. */\n\n',
    'css/day7.css': '/* Bentley Palm Beach — the theme: Satin Linen 40% (the client\'s choice).\n   <html class="theme-satin"> carries it. Where a selector repeats the class\n   (html.theme-satin.theme-satin) it keeps the weight the original look\n   switch had, so the cascade is exactly as approved — do not shorten it. */\n\n',
    'css/subpages7.css': '/* Bentley Palm Beach — the inner pages (about, contact, finance): the page\n   title, the picture band, the staff card, hours, location. Loads last on an\n   inner page, after static.css. */\n\n',
    'css/static7.css': '/* Bentley Palm Beach — the static page (client, 2026-10-04: no scroll\n   layer, no motion on arrival): last in the cascade, wins over the above. */\n\n',
}

# --- HTML -------------------------------------------------------------------
def relink(s):
    for a, b in list(CSS.items()) + list(JS.items()):
        s = re.sub(re.escape(a) + r'(\?v=[^"]*)?"', b + '"', s)
    s = s.replace('index7.html', 'index.html').replace('inventory7.html', 'inventory.html')
    for n in ('about', 'contact', 'finance', 'parts', 'sell', 'calculator', 'bentayga-speed', 'flying-spur', 'torcal', 'continental-gtc', 'continental-gt'): s = s.replace(f'{n}7.html', f'{n}.html')
    s = s.replace('vehicles7/', 'vehicles/')
    return s

HEAD_SCRIPTS = [
    re.compile(r'<script>\s*/\* Direction 7 keeps direction 6.s look.*?</script>\n', re.S),
    re.compile(r'<script>\s*/\* Motion is opt-in.*?</script>\n', re.S),
    re.compile(r'<script>if \(window\.top !== window\.self\).*?</script>\n', re.S),
]
def page(s):
    for rx in HEAD_SCRIPTS: s = rx.sub('', s)
    s = s.replace('<html lang="en">', '<html lang="en" class="theme-satin">', 1)
    s = re.sub(r'[ \t]*<!--.*?-->[ \t]*\n?', '', s, flags=re.S)
    s = relink(s)
    s = re.sub(r'(\.(?:css|js))\?v=[^"]*"', r'\1"', s)
    s = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', s)
    return s

# --- assets -----------------------------------------------------------------
ASSET = re.compile(r'(?:\.\./)?(assets/[^"\'\s,)?#]+)')
def assets_in(text): return set(ASSET.findall(text))

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT + 'css'); os.makedirs(OUT + 'js'); os.makedirs(OUT + 'vehicles')
    used = set(); report = []
    for src, dst in CSS.items():
        css, st = sheet(src)
        open(OUT + dst, 'w', encoding='utf-8', newline='\n').write(css)
        used |= assets_in(css)
        report.append(f'{dst}: {st["rules"]} rules and {st["selectors"]} selectors removed')
    for src, dst in JS.items():
        js = read(src)
        open(OUT + dst, 'w', encoding='utf-8', newline='\n').write(js)
        used |= assets_in(js)
    pages = dict(PAGES)
    for f in sorted(os.listdir(ROOT + 'vehicles7')):
        if f.endswith('.html'): pages['vehicles7/' + f] = 'vehicles/' + f
    for src, dst in pages.items():
        html = page(read(src))
        open(OUT + dst, 'w', encoding='utf-8', newline='\n').write(html)
        used |= assets_in(html)
    missing = []
    for a in sorted(used):
        if not os.path.isfile(ROOT + a): missing.append(a); continue
        os.makedirs(os.path.dirname(OUT + a), exist_ok=True)
        shutil.copy2(ROOT + a, OUT + a)
    shutil.copy2(ROOT + 'tools/HANDOFF-README.md', OUT + 'README.md')
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
    print('\n'.join(report))
    print(f'{len(pages)} pages, {len(used) - len(missing)} assets, {size / 1e6:.1f} MB')
    if missing: print('MISSING:', *missing, sep='\n  ')

if __name__ == '__main__':
    main()
