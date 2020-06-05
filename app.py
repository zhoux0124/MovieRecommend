import re
from urllib import parse

import execjs
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/find/', methods=['GET'])
def find():
    query = request.args.get('movie')
    movie_items = []
    if query:
        url = 'https://search.douban.com/movie/subject_search?search_text=' + parse.quote(query) + '&cat=1002'
        response = requests.get(url)
        r = re.search('window.__DATA__ = "([^"]+)"', response.text).group(1)
        with open('static/douban.js', 'r', encoding='gbk') as f:
            decrypt_js = f.read()
        ctx = execjs.compile(decrypt_js)
        data = ctx.call('decrypt', r)
        items = data['payload']['items']
        for item in items:
            if 'title' in item and 'rating' in item:
                if item['title'].find(query) == 0:
                    movie_items.append(item)
        movie_items.sort(key=lambda k: k['rating']['value'], reverse=True)
    hot_movies = get_hot_movies()
    return render_template('find.html', **locals())

def get_hot_movies():
    r = requests.get('http://theater.mtime.com/China_Beijing/')
    hots = []
    for line in r.text.split('\n'):
        if line.find('M14_TheaterIndex_Hotplay_Text') > -1 and line.find('<dt>') > -1:
            title = line.split('>')[2].split('<')[0]
            title not in hots and hots.append(title)
            if len(hots) > 6:
                break
    return hots

if __name__ == '__main__':
    app.run(debug=True, port=5000)
