import urllib.request
import re
from bs4 import BeautifulSoup

def get_html(folder_name):
    num = [int(s) for s in folder_name.split() if s.isdigit()]
    map_id = num[0]
    map_url = "https://osu.ppy.sh/s/" + str(map_id)
    response = urllib.request.urlopen(map_url)
    html = response.read()
    return html

def get_difficulty(folder_name):
    html_data = get_html(folder_name)
    str_html = str(html_data)
    i1 = str_html.find("Star Difficulty")
    i2 =str_html.find("(", i1)
    tar_str = str_html[i2:i2+10]
    num = re.findall("\d+\.\d+", tar_str)
    return num[0]

html_data = get_difficulty("572206 Yui Horie - Sweet & Sweet CHERRY")
print(html_data)
# str_html = str(html_data)
# i1 = str_html.find("Star Difficulty")
# i2 =str_html.find("(", i1)
# print(str_html[i2:i2+10])
# html_data.encode('utf-8', 'ignore')
# print(html_data)
# soup = BeautifulSoup(html_data, 'lxml')
# print(soup.prettify())