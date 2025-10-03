import csv
from pathlib import Path
from cursor_ai import generate_hotel_post
csv_file = 'hotels.csv'
posts_dir = Path('posts')
posts_dir.mkdir(exist_ok=True)
index_file = Path('index.html')
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    post_links = []
    for row in reader:
        hotel_name = row['hotel_name']
        city = row['city']
        agoda_link = row['agoda_link']
        content = generate_hotel_post(hotel_name, city, agoda_link)
        filename = posts_dir / f"{hotel_name.replace(' ', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as out:
            out.write(content)
        post_links.append(f'<li><a href=\"posts/{filename.name}\">{hotel_name} 비교</a></li>')
import re
with open(index_file, 'r', encoding='utf-8') as f:
    index_html = f.read()
new_index_html = re.sub(r'(<ul id="post-list">).*?(</ul>)', f"\1\n{''.join(post_links)}\n\2", index_html, flags=re.S)
with open(index_file, 'w', encoding='utf-8') as f:
    f.write(new_index_html)
print('모든 글 생성 완료!')