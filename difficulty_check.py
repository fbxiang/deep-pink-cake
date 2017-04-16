import urllib.request
import re
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import os

def get_difficulty_url(folder_name):
    num = [int(s) for s in folder_name.split() if s.isdigit()]
    map_id = num[0]
    map_url = "https://osu.ppy.sh/s/" + str(map_id)
    response = urllib.request.urlopen(map_url)
    html = response.read();
    soup = BeautifulSoup(html, 'lxml')

    difficulties = []
    urls = []
    for tab in soup.find_all('a', {'class': 'beatmapTab'}):
        difficulty = tab.find('span').text
        url = 'https://osu.ppy.sh' + tab.attrs['href']
        difficulties.append(difficulty)
        urls.append(url)
    return difficulties, urls

def get_star_difficulty(url):
    html = urllib.request.urlopen(url).read();
    soup = BeautifulSoup(html, 'lxml')

    number = None
    for tag in soup.find_all('div', 'starfield'):
        s = tag.nextSibling
        if s is not None:
            number = s
    return float(number.strip()[1:-1])

def get_difficulty_mapping(foldername):
    try:
        difficulties, urls = get_difficulty_url(foldername)
        mapping = []
        for d, url in zip(difficulties, urls):
            mapping.append((d, get_star_difficulty(url)))
        return mapping
    except Exception:
        print('Error: ', foldername)
        return []

def write_difficulty_file(foldername):
    if not os.path.isdir(foldername): return
    mapping_file = os.path.join(foldername, 'difficulty_mapping.txt')
    name = os.path.basename(foldername)
    mapping = get_difficulty_mapping(name)
    with open(mapping_file, 'w') as f:
        for d, n in mapping:
            f.write("{} -> {}\n".format(d, n))
