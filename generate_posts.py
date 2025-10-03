import csv
from pathlib import Path
import re
from html import escape

BASE_URL = 'https://gityeol.github.io'
PLACEHOLDER_IMG = 'https://via.placeholder.com/640x360?text=Hotel'

ANALYTICS_SNIPPET = """
<!-- Analytics placeholders -->
<!-- Google Analytics (replace with real GA tag) -->
<!-- <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js', new Date());gtag('config','G-XXXXXXX');</script> -->
<!-- Naver Analytics (replace with real script) -->
<!-- <script type="text/javascript">/* Naver Analytics */</script> -->
""".strip()


def wrap_html(title: str, body_html: str, root_prefix: str = '') -> str:
	return f"""<!DOCTYPE html>
<html lang=\"ko\">\n<head>\n<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n<title>{escape(title)}</title>\n<link rel=\"stylesheet\" href=\"{root_prefix}style.css\">\n{ANALYTICS_SNIPPET}\n</head>\n<body>\n<header>\n  <h1><a href=\"{root_prefix}index.html\">호텔 비교 블로그</a></h1>\n  <nav>\n    <a href=\"{root_prefix}index.html\">홈</a>\n    <a href=\"{root_prefix}about.html\">소개</a>\n    <a href=\"{root_prefix}contact.html\">문의</a>\n    <a href=\"{root_prefix}privacy.html\">개인정보처리방침</a>\n    <a href=\"{root_prefix}terms.html\">이용약관</a>\n  </nav>\n</header>\n<main>\n{body_html}\n</main>\n<footer><p>© 2025 호텔 비교 블로그</p></footer>\n</body></html>"""


def generate_hotel_post(hotel_name: str, city: str, agoda_link: str, image_url: str = "", price: str = "", rating: str = "", pros: str = "", cons: str = "") -> str:
	safe_title = f"{hotel_name} ({city})" if city else hotel_name
	img_src = image_url or PLACEHOLDER_IMG
	link_html = f'<p class=\"cta\"><a href=\"{agoda_link}\" target=\"_blank\" rel=\"nofollow noopener\">Agoda에서 가격 확인</a></p>' if agoda_link else ''
	img_html = f'<p><img src=\"{img_src}\" alt=\"{escape(hotel_name)}\" loading=\"lazy\"></p>'
	price_html = f'<p class=\"price\">가격대: {escape(price)}</p>' if price else ''
	# normalize rating to stars if numeric
	stars_html = ''
	try:
		if rating:
			r = float(str(rating).strip())
			rounded = max(0, min(5, int(round(r))))
			stars_html = '<p class=\"rating\">평점: ' + '★'*rounded + '☆'*(5-rounded) + f' ({escape(str(rating))})</p>'
	except Exception:
		stars_html = f'<p class=\"rating\">평점: {escape(str(rating))}</p>' if rating else ''

	pros_list = [p.strip() for p in (pros or '').split(';') if p.strip()]
	cons_list = [c.strip() for c in (cons or '').split(';') if c.strip()]
	pros_html = ('<section>\n    <h2>장점</h2>\n    <ul>\n' + '\n'.join(f'      <li>{escape(p)}</li>' for p in pros_list) + '\n    </ul>\n  </section>') if pros_list else ''
	cons_html = ('<section>\n    <h2>단점</h2>\n    <ul>\n' + '\n'.join(f'      <li>{escape(c)}</li>' for c in cons_list) + '\n    </ul>\n  </section>') if cons_list else ''

	article = f"""
<article class=\"post\">
  <h1>{escape(safe_title)}</h1>
  {img_html}
  {price_html}
  {stars_html}
  <section>
    <h2>개요</h2>
    <p>{escape(hotel_name)}의 위치와 기본 정보를 간단히 정리했습니다.</p>
  </section>
  {pros_html}
  {cons_html}
  {link_html}
</article>
""".strip()
	return article

csv_file = 'hotels.csv'
posts_dir = Path('posts')
posts_dir.mkdir(exist_ok=True)
index_file = Path('index.html')
cities_dir = Path('cities')
cities_dir.mkdir(exist_ok=True)
pages_dir = Path('pages')
pages_dir.mkdir(exist_ok=True)
sitemap_file = Path('sitemap.xml')

rows_data = []

with open(csv_file, newline='', encoding='utf-8') as f:
	reader = csv.DictReader((line for line in f if not line.startswith(("<<<<<<<", "=======", ">>>>>>>"))))
	for row in reader:
		hotel_name = (row.get('hotel_name') or row.get('HotelName') or '').strip()
		city = (row.get('city') or row.get('Location') or '').strip()
		agoda_link = (row.get('agoda_link') or row.get('Link') or '').strip()
		image_url = (row.get('image_url') or row.get('Image') or '').strip()
		price = (row.get('price') or row.get('Price') or '').strip()
		rating = (row.get('rating') or row.get('Rating') or '').strip()
		pros = (row.get('pros') or row.get('Pros') or '').strip()
		cons = (row.get('cons') or row.get('Cons') or '').strip()
		if not hotel_name:
			continue
		filename = posts_dir / f"{hotel_name.replace(' ', '_')}.html"
		content = generate_hotel_post(hotel_name, city, agoda_link, image_url, price, rating, pros, cons)
		full_html = wrap_html(hotel_name, content, root_prefix='../')
		with open(filename, 'w', encoding='utf-8') as out:
			out.write(full_html)
		rows_data.append({
			"hotel_name": hotel_name,
			"city": city,
			"agoda_link": agoda_link,
			"image_url": image_url or PLACEHOLDER_IMG,
			"price": price,
			"rating": rating,
			"post_path": f"posts/{filename.name}",
		})

# Build list items for legacy UL
post_links = [f'<li><a href="{d["post_path"]}">{escape(d["hotel_name"])} 비교</a></li>' for d in rows_data]

# Build card grid HTML with data attributes
card_items = []
for d in rows_data:
	img = f'<img src="{d["image_url"]}" alt="{escape(d["hotel_name"]) }" loading="lazy">'
	# compute numeric helpers
	def _rating_num(x):
		try:
			return float(str(x)) if str(x).strip() else 0.0
		except Exception:
			return 0.0
	def _price_num(x):
		m = re.search(r"(\d+(?:\.\d+)?)", (x or '').replace(',', ''))
		return float(m.group(1)) if m else 0.0
	price_num = _price_num(d["price"]) if d["price"] else 0.0
	rating_num = _rating_num(d["rating"]) if d["rating"] else 0.0
	price_html = f'<div class="meta price">{escape(d["price"])}</div>' if d["price"] else ''
	rating_html = ''
	try:
		if d["rating"]:
			r = float(str(d["rating"]))
			rounded = max(0, min(5, int(round(r))))
			rating_html = '<div class="meta rating">' + '★'*rounded + '☆'*(5-rounded) + f' ({escape(str(d["rating"]))})</div>'
	except Exception:
		rating_html = f'<div class="meta rating">{escape(str(d["rating"]))}</div>' if d["rating"] else ''
	city_meta = f'<div class="meta">{escape(d["city"])}</div>' if d["city"] else ''
	card_items.append(
		f'<a class="card" data-city="{escape(d["city"])}" data-rating="{rating_num}" data-price="{price_num}" href="{d["post_path"]}">{img}<div class="card-body"><div class="card-title">{escape(d["hotel_name"])}</div>{city_meta}{price_html}{rating_html}</div></a>'
	)

# Inject into index.html
with open(index_file, 'r', encoding='utf-8') as f:
	index_html = f.read()

# Add city nav at top of main
cities = {}
for d in rows_data:
	if d["city"]:
		cities.setdefault(d["city"], []).append(d)

city_links = [f'<a href="cities/{city.replace(" ", "_")}.html">{escape(city)}</a>' for city in sorted(cities.keys())]
if city_links:
	if re.search(r'<div id="city-nav">', index_html):
		index_html = re.sub(r'(<div id="city-nav">)\s*(.*?)\s*(</div>)', lambda m: f"{m.group(1)}{' | '.join(city_links)}{m.group(3)}", index_html, flags=re.S)
	else:
		index_html = index_html.replace('<main>', f"<main>\n<div id=\"city-nav\">{' | '.join(city_links)}</div>")

# Replace UL content
index_html = re.sub(r'(<ul id="post-list">)\s*(.*?)\s*(</ul>)', lambda m: f"{m.group(1)}\n{''.join(post_links)}\n{m.group(3)}", index_html, flags=re.S)
# Replace card grid content
index_html = re.sub(r'(<div id="post-grid"[^>]*>)\s*(.*?)\s*(</div>)', lambda m: f"{m.group(1)}\n{''.join(card_items)}\n{m.group(3)}", index_html, flags=re.S)

# Inject analytics snippet in head if missing
if 'Analytics placeholders' not in index_html:
	index_html = index_html.replace('</head>', ANALYTICS_SNIPPET + '\n</head>')

with open(index_file, 'w', encoding='utf-8') as f:
	f.write(index_html)

# City pages
for city, items in sorted(cities.items()):
	slug = city.replace(' ', '_')
	city_path = Path('cities') / f"{slug}.html"
	cards = []
	for d in items:
		img = f'<img src="{d["image_url"]}" alt="{escape(d["hotel_name"]) }" loading="lazy">'
		cards.append(f'<a class=\"card\" href=\"../{d["post_path\"]}\">{img}<div class=\"card-body\"><div class=\"card-title\">{escape(d["hotel_name"])}</div></div></a>')
	body = f"<h2>{escape(city)} 호텔 모음</h2><div class=\"grid\">{''.join(cards)}</div>"
	html = wrap_html(f"{city} 호텔 모음", body, root_prefix='../')
	with open(city_path, 'w', encoding='utf-8') as c:
		c.write(html)

# Sort pages
def rating_key(v: dict) -> float:
	try:
		return float(v.get('rating') or 0)
	except Exception:
		return 0.0

def price_key(v: dict) -> float:
	# very naive: extract leading digits
	m = re.search(r"(\d+[\.]?\d*)", (v.get('price') or '').replace(',', ''))
	return float(m.group(1)) if m else 0.0

sorted_by_rating = sorted(rows_data, key=rating_key, reverse=True)
sorted_by_price = sorted(rows_data, key=price_key)

for name, items in (('sort-rating.html', sorted_by_rating), ('sort-price.html', sorted_by_price)):
	cards = []
	for d in items:
		img = f'<img src="{d["image_url"]}" alt="{escape(d["hotel_name"]) }" loading="lazy">'
		cards.append(f'<a class=\"card\" href=\"../{d["post_path\"]}\">{img}<div class=\"card-body\"><div class=\"card-title\">{escape(d["hotel_name"])}</div></div></a>')
	label = '평점 순' if 'rating' in name else '가격 순'
	body = f"<h2>{label} 호텔 모음</h2><div class=\"grid\">{''.join(cards)}</div>"
	html = wrap_html(label, body, root_prefix='../')
	with open(Path('pages') / name, 'w', encoding='utf-8') as pf:
		pf.write(html)

# Write sitemap
urls = [f'{BASE_URL}/']
urls += [f'{BASE_URL}/{d["post_path"]}' for d in rows_data]
urls += [f'{BASE_URL}/cities/{city.replace(" ", "_")}.html' for city in cities.keys()]
urls += [f'{BASE_URL}/pages/sort-rating.html', f'{BASE_URL}/pages/sort-price.html']
with open('sitemap.xml', 'w', encoding='utf-8') as sm:
	sm.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	sm.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
	for u in urls:
		sm.write(f'<url><loc>{u}</loc></url>\n')
	sm.write('</urlset>')

print('모든 글 생성 완료! (카드/도시/정렬/사이트맵/애널리틱스/필터 반영)')