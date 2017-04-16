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

def get_difficulty_name(folder_name):
    files = os.listdir(folder_name)
    diff_names = []
    for name in files:
        if '.osu' in name:
            i1 = name.find("[")
            i2 = name.find("]", i1)
            diff_names.append(name[i1+1:i2])
    return diff_names

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
diff_names = get_difficulty_name("572206 Yui Horie - Sweet & Sweet CHERRY")
print(diff_names)