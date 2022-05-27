import os
import re
from flask import Flask, Response, jsonify, request, render_template
from flask_cors import CORS, cross_origin
import utils
import time
import urllib, json
import sys

app = Flask('__name__')
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/process_search')
def gen_search_json():
    start_time = time.time()
    query = request.args.get("q", '')
    query = utils.process_term(query)
    results = utils.get_results(query.strip())
    resp = jsonify(results=results[:10])  # top 10 results
    resp.headers['Access-Control-Allow-Origin'] = '*'
    end_time = time.time()
    #print("Response time : " + str(end_time - start_time))
    return resp

@app.route('/home', methods=['GET'])
def render_html():
    return render_template('index.html')


# @app.route('styles')
# def returncss():
#     return "C:\Users\milon\OneDrive\Desktop\Capstone\Project\venv\src\templates\styles\\.css"


@app.route('/do_search')
def do_search():
    query = request.args.get("q", '')
    print(query)
    #return tfidf.query_search(query)
    return   {"0": {
    "Content": "literally every time surf internet 's phone tv run ninety-five % supercomputers many devices use everyday linux everywhere helsinki-based programmer start orchestrate worldwide army developers home office portland oregon fellow linux foundation celebrate twenty years linux see story thank part first twenty years",
    "Minute": 3,
    "Score": 1.0,
    "Video": "/home/julian/Workspace/hayes/Search_Engine/Jesslin/video_captions/The_Story_of_Linux-en.txt",
    "Title": "The_Story_of_Linux-en"
  },
  "1": {
    "Content": "use linux every day whether know 850,000 android phone run lennox activate",
    "Minute": 0,
    "Score": 1.0,
    "Video": "/home/julian/Workspace/hayes/Search_Engine/Jesslin/video_captions/How_Linux_is_Built-en.txt",
    "Title": "How_Windows_is_Built-en"
  },
  "2": {
    "Content": "history compute justin 's two thousand and five 8,000 developers almost eight hundred company contribute linux kernel contributions result",
    "Minute": 1,
    "Score": 1.0,
    "Video": "/home/julian/Workspace/hayes/Search_Engine/Jesslin/video_captions/How_Linux_is_Built-en.txt",
    "Title": "How_-en 2"
  },
  "3": {
    "Content": "history compute justin 's two thousand and five 8,000 developers almost eight hundred company contribute linux kernel contributions result",
    "Minute": 1,
    "Score": 1.0,
    "Video": "/home/julian/Workspace/hayes/Search_Engine/Jesslin/video_captions/How_Linux_is_Built-en.txt",
    "Title": "How_-en 2"
  },
    "4": {
    "Content": "history compute justin 's two thousand and five 8,000 developers almost eight hundred company contribute linux kernel contributions result",
    "Minute": 1,
    "Score": 1.0,
    "Video": "/home/julian/Workspace/hayes/Search_Engine/Jesslin/video_captions/How_Linux_is_Built-en.txt",
    "Title": "How_-en 2"
  }
}

@app.route('/search', methods=['GET'])
def render_srhtml():
    query = request.args.get("q", '')
    print(query, file=sys.stdout)
    url = "http://192.168.0.37:5000/do_search?q=amazon"
    response = urllib.request.urlopen(url)
    data = response.read()
    # diction = data
    diction = json.loads(data)
    print(diction, file=sys.stdout)
    return render_template('searchResults.html', search_results = diction)

def get_chunk(full_path,byte1=None, byte2=None):
    file_size = os.stat(full_path).st_size
    start = 0

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size


@app.route('/video')
def get_file():
    range_header = request.headers.get('Range', None)
    fn = request.args.get("file", '')
    byte1, byte2 = 0, None
    if range_header:
        match = re.search('([0-9]+)-([0-9]*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])
    # fn = "/home/julian/Workspace/hayes/Search_Engine/Jesslin/videos/"+fn+".mp4"
    fn = "C:/Users/milon/OneDrive/Desktop/Capstone/sample.mp4"
    print(fn)
    chunk, start, length, file_size = get_chunk(fn,byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                      content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    print(resp.headers)
    return render_template('linkResult.html')
    # return resp

if __name__== '__main__':
    app.run(host='0.0.0.0',debug=True)
