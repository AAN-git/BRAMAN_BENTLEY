"""The 360: the retailer's listing carries a DealerMade Next HD turntable
   (~52 positions × three cameras). This asks the viewer's own API for each
   car's picture set (as the widget does, with its service header), picks
   FRAMES frames of the Middle camera evenly around the turn, saves them 1000
   wide (assets/img/spin/<slug>/NN.webp) and writes spin + spin_source into
   data/inventory.json. Needs .playwright-mcp/drop/dm-post.json — one
   LoadVehicle request body saved from a browser session — for the query.
   Run: python3 tools/spin.py [--only STOCK]"""
import json, os, sys, io, urllib.request, time
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
FRAMES = 24
post = json.load(open(ROOT + '.playwright-mcp/drop/dm-post.json'))
d = json.load(open(ROOT + 'data/inventory.json'))
only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None

def api(v):
    body = dict(post); body['variables'] = dict(post['variables'], vin=v['vin'], dealerWebsiteUrl=v['dealer_url'])
    req = urllib.request.Request('https://api.dealermade-next.com/v4/graphql', data=json.dumps(body).encode(), headers={
        'Content-Type': 'application/json', 'Origin': 'https://www.bramanbentleypalmbeach.com', 'Referer': 'https://www.bramanbentleypalmbeach.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36',
        'x-dealermade-system-service': 'dm-next-hd-viewer'})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=60).read()

for v in d['vehicles']:
    if only and v['stock'] != only: continue
    if v.get('spin') and not only: continue
    slug = v['stock'].lower()
    try:
        r = api(v)
        car = (r.get('data') or {}).get('createVehicleViewAndFetchVehicle')
        car = car and car['vehicle']
    except Exception as ex:
        print(v['stock'], 'API error', ex); continue
    if not car:
        print(v['stock'], 'no vehicle at DealerMade', json.dumps(r)[:200]); v['spin'] = []; v['spin_source'] = None; continue
    pics = [p for p in car.get('exterior360doorsclosed') or [] if p['vehiclePictureType']['cameraType']['name'] == 'Middle']
    pics.sort(key=lambda p: p['pictureSetPosition'])
    if len(pics) < 8:
        print(v['stock'], 'no turntable', len(pics)); v['spin'] = []; v['spin_source'] = None; continue
    n = len(pics)
    picks = [pics[round(i * n / FRAMES)] for i in range(FRAMES)]
    v['spin'] = []
    for i, p in enumerate(picks):
        dest = ROOT + f'assets/img/spin/{slug}/{i:02d}.webp'
        if not os.path.exists(dest):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            im = Image.open(io.BytesIO(fetch(f"https://dm-next-images.s3.us-east-2.amazonaws.com/vehicle-pictures/{p['id']}/3-2_large.jpg"))).convert('RGB')
            im = im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
            im.save(dest, 'WEBP', quality=78, method=6)
        v['spin'].append(f'assets/img/spin/{slug}/{i:02d}.webp')
    v['spin_source'] = {'viewer': 'DealerMade Next HD viewer on the retailer listing', 'vehicle_id': car['id'], 'positions': n, 'camera': 'Middle',
                        'picked': [[p['pictureSetPosition'], p['id']] for p in picks]}
    print(v['stock'], n, 'positions →', FRAMES, 'frames', flush=True)
    json.dump(d, open(ROOT + 'data/inventory.json', 'w'), indent=1, ensure_ascii=False)
    time.sleep(0.5)
print('done')
