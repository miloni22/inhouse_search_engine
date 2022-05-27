import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
import time
#import tfidf

app = Flask('__name__')

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/do_search')
def do_search():
    query = request.args.get("q", '')
    print(query)
    #return tfidf.query_search(query)
    return   {"0": {
    "Content": "literally every time surf internet 's phone tv run ninety-five % supercomputers many devices use everyday linux everywhere helsinki-based programmer start orchestrate worldwide army developers home office portland oregon fellow linux foundation celebrate twenty years linux see story thank part first twenty years",
    "Minute": 3,
    "Score": 1.0,
    "Video": "/home/julian/Workspace/hayes/Search_Engine/Jesslin/video_captions/The_Story_of_Linux-en.txt"
  },
  "1": {
    "Content": "use linux every day whether know 850,000 android phone run lennox activate",
    "Minute": 0,
    "Score": 1.0,
    "Video": "/home/julian/Workspace/hayes/Search_Engine/Jesslin/video_captions/How_Linux_is_Built-en.txt"
  },
  "2": {
    "Content": "history compute justin 's two thousand and five 8,000 developers almost eight hundred company contribute linux kernel contributions result",
    "Minute": 1,
    "Score": 1.0,
    "Video": "/home/julian/Workspace/hayes/Search_Engine/Jesslin/video_captions/How_Linux_is_Built-en.txt"
  }
}


if __name__== '__main__':
    app.run(host='0.0.0.0',port=6000,debug=True)
