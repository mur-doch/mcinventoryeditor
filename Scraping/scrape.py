import requests
from bs4 import BeautifulSoup
import re 

# Before we do the request and parse the page, let's load our stripped css file
# into a dictionary
class_to_xy = {}
file = open('site_modified.css', 'r')
for line in file:
    class_name, raw_xy = line.split(':')
    raw_x, raw_y = raw_xy.strip().split(' ')
    class_to_xy[class_name] = (int(raw_x), int(raw_y))
file.close()

response = requests.get('https://minecraft-ids.grahamedgecombe.com/')
if response.status_code != 200:
    print("Error requesting page")
    exit()
else:
    content = response.content 

soup = BeautifulSoup(content, 'html.parser')
# Shows that we have 719 for all of these
# print(len(soup.find_all(class_='id')))
# print(len(soup.find_all(class_='row-icon')))
# print(len(soup.find_all(class_='text-id')))
# row_id_tags = soup.find_all(class_='id')
row_icon_tags = soup.find_all(class_='row-icon')
text_id_tags = soup.find_all(class_='text-id')

mcid_to_xy = {}

i1 = 0 
i2 = 0
while i1 < len(row_icon_tags) and i2 < len(text_id_tags):
    css_class = row_icon_tags[i1].find(name='div')['class'][1]
    mc_id = re.sub(r'[\(\)]', '', text_id_tags[i2].text)
    # print(class_to_xy[css_class])
    key = mc_id
    if key in mcid_to_xy:
        i = 1 
        new_key = f"{mc_id}-{i}"
        while new_key in mcid_to_xy:
            i += 1
            new_key = f"{mc_id}-{i}"
        key = new_key
    mcid_to_xy[key] = class_to_xy[css_class]
    
    # print(css_class, class_to_xy[css_class], mc_id)
    i1 += 1
    i2 += 1

# file = open('mcid_to_xy.csv', 'w')
# for mcid in mcid_to_xy:
#     x, y = mcid_to_xy[mcid]
#     file.write(f"{mcid},{x},{y}\n")
# file.close()

file = open('mcid_to_index.csv', 'w')
i = 0
for mcid in mcid_to_xy:
    x, y = mcid_to_xy[mcid]
    row = abs(y) // 32
    col = abs(x) // 32
    index = row * 27 + col
    file.write(f"{mcid},{index}\n")
    i += 1
file.close()