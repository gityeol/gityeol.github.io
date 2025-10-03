import csv
from pathlib import Path
import re


def generate_hotel_post(hotel_name: str, city: str, agoda_link: str) -> str:
	safe_title = f"{hotel_name} ({city})" if city else hotel_name
	link_html = f'<p><a href="{agoda_link}" target="_blank" rel="nofollow noopener">Agoda에서 가격 확인</a></p>' if agoda_link else ''
	return f"""
<article class="post">
  <h1>{safe_title}</h1>
  {link_html}
  <section>
    <h2>개요</h2>
    <p>{hotel_name}의 위치와 기본 정보를 간단히 정리했습니다.</p>
  </section>
  <section>
    <h2>추천 포인트</h2>
    <ul>
      <li>접근성 우수</li>
      <li>가성비 양호</li>
      <li>인근 편의시설 풍부</li>
    </ul>
  </section>
  <section>
    <h2>주의 사항</h2>
    <ul>
      <li>성수기 가격 변동</li>
      <li>객실 타입별 차이</li>
    </ul>
  </section>
</article>
""".strip()

csv_file = 'hotels.csv'
posts_dir = Path('posts')
posts_dir.mkdir(exist_ok=True)
index_file = Path('index.html')

with open(csv_file, newline='', encoding='utf-8') as f:
	reader = csv.DictReader((line for line in f if not line.startswith(("<<<<<<<", "=======", ">>>>>>>"))))
	post_links = []
	for row in reader:
		hotel_name = (row.get('hotel_name') or row.get('HotelName') or '').strip()
		city = (row.get('city') or row.get('Location') or '').strip()
		agoda_link = (row.get('agoda_link') or row.get('Link') or '').strip()
		if not hotel_name:
			continue
		filename = posts_dir / f"{hotel_name.replace(' ', '_')}.html"
		content = generate_hotel_post(hotel_name, city, agoda_link)
		with open(filename, 'w', encoding='utf-8') as out:
			out.write(content)
		post_links.append(f'<li><a href="posts/{filename.name}">{hotel_name} 비교</a></li>')

with open(index_file, 'r', encoding='utf-8') as f:
	index_html = f.read()

new_index_html = re.sub(r'(<ul id="post-list">)\s*(.*?)\s*(</ul>)', lambda m: f"{m.group(1)}\n{''.join(post_links)}\n{m.group(3)}", index_html, flags=re.S)

with open(index_file, 'w', encoding='utf-8') as f:
	f.write(new_index_html)

print('모든 글 생성 완료!')