import os
import urllib, json
import sys
from flask import Flask, jsonify, request, Response, render_template
from flask_cors import CORS, cross_origin
import utils
import autocorrect
import time
import re
from cmath import isnan
import math
from tabnanny import NannyNag
from tarfile import XHDTYPE
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import inflect
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import vid_summarizer as vs

p = inflect.engine()
lemmatizer = WordNetLemmatizer()

#Class to hold video and key moment information
class seDoc:
    def __init__(self, docName, line, content, similarityScore):
        self.docName = docName
        self.line = line
        self.content = content
        self.similarityScore = similarityScore

    def myfunc(self):
        print("Video: \n" + self.docName)
        print("Minute: \n" + str(self.line))
        print("Content: \n" + self.content)
        print("SimilarityScore: \n" + str(self.similarityScore))
    def toDict(self):
        print ({"File":self.docName.split("/")[-1].split(".")[0], "Title": self.docName.split("/")[-1].split(".")[0].replace("_"," "),"Content":self.content,"Minute":self.line,"Score":self.similarityScore})
        return {"File":self.docName.split("/")[-1].split(".")[0], "Title": self.docName.split("/")[-1].split(".")[0].replace("_"," "),"Content":self.content,"Minute":self.line,"Score":self.similarityScore}

# Folder Path
#path = "C:\\Users\\muth\\InHouseEngine\\In-House-Search-Engine\\video-text\\video-captions"
cwd=os.getcwd()
captions_path= cwd+"/static/Data/text"
#Array of vidoes, type seDoc
videos = []  

# Change the directory
os.chdir(captions_path)


# Read text File
def read_text_file(file_path):
    i = 0
    with open(file_path, 'r') as f:
        while True:
            print  (file_path)
            line = f.readline()
            #eof
            if line ==  '':
                break
            #line contains key moment info (eg: "0:")
            if line.__contains__(':'):
                continue
            videos.append(seDoc(file_path, i, remove_stopwords(line.strip()), 0))
            i += 1

# remove stopwords function, convert numbers to numbers in words, lemmetize
def remove_stopwords(text):
    stop_words = set(stopwords.words("english"))
    word_tokens = word_tokenize(text.lower())
    filtered_text = []
    for w in word_tokens:
        if(w not in stop_words):
            if w.isdigit():
                w = p.number_to_words(w)
            w = lemmatizer.lemmatize(w, pos ='v')
            filtered_text.append(w)
    #filtered_text = [word for word in word_tokens if word not in stop_words]
    return ' '.join(filtered_text)


# iterate through all file
for file in os.listdir():
    # Check whether file is in text format or not
    if file.endswith(".txt"):
        file_path = f"{captions_path}/{file}"
  
        # call read text file function
        read_text_file(file_path)

#Correcting path
os.chdir(cwd)

# tf-idf score across all docs for the query string

def compute_tfidf_with_alldocs(videos , query):
    tf_idf = []
    index = 0
    query_tokens = query.split()
    df = pd.DataFrame(columns=['doc'] + query_tokens)
    for doc in videos:
        df['doc'] = np.arange(0 , len(videos))
        doc_num = tf_doc[index]
        sentence = doc.content.split()
        for word in sentence:
            for text in query_tokens:
                if(text == word):
                    idx = sentence.index(word)
                    tf_idf_score = doc_num[word] * idf_dict[word]
                    tf_idf.append(tf_idf_score)
                    df.iloc[index, df.columns.get_loc(word)] = tf_idf_score
        index += 1
    df.fillna(0 , axis=1, inplace=True)
    return tf_idf , df

#term -frequenvy :word occurences in a document
def compute_tf(videos):
    for video in videos:
        doc1_lst = video.content.split(" ")
        wordDict_1= dict.fromkeys(set(doc1_lst), 0)

        for token in doc1_lst:
            wordDict_1[token] +=  1
        df = pd.DataFrame([wordDict_1])
        idx = 0
        new_col = ["Term Frequency"]    
        df.insert(loc=idx, column='Document', value=new_col)
        print(df)

print("Term frequency")
compute_tf(videos)


def termFrequency(term, document):
    normalizeDocument = document.lower().split()
    return normalizeDocument.count(term.lower()) / float(len(normalizeDocument))

def compute_normalizedtf(videos):
    tf_doc = []
    for video in videos:
        sentence = video.content.split()
        norm_tf= dict.fromkeys(set(sentence), 0)
        for word in sentence:
            norm_tf[word] = termFrequency(word, video.content)
        tf_doc.append(norm_tf)
        df = pd.DataFrame([norm_tf])
        idx = 0
        new_col = ["Normalized TF"]    
        df.insert(loc=idx, column='Document', value=new_col)
        print(df)
    return tf_doc

tf_doc = compute_normalizedtf(videos)

def inverseDocumentFrequency(term, videos):
    numDocumentsWithThisTerm = 0
    for itr in range (0, len(videos)):
        if term.lower() in videos[itr].content.lower().split():
            numDocumentsWithThisTerm = numDocumentsWithThisTerm + 1
 
    if numDocumentsWithThisTerm > 0:
        return 1.0 + math.log(float(len(videos)) / numDocumentsWithThisTerm)
    else:
        return 1.0
    
def compute_idf(videos):
    idf_dict = {}
    for video in videos:
        sentence = video.content.split()
        for word in sentence:
            idf_dict[word] = inverseDocumentFrequency(word, videos)
    return idf_dict

idf_dict = compute_idf(videos)

#Normalized TF for query
def compute_query_tf(query):
    query_norm_tf = {}
    tokens = query.split()
    for word in tokens:
        query_norm_tf[word] = termFrequency(word , query)
    return query_norm_tf

#idf score for the query string
def compute_query_idf(query):
    idf_dict_qry = {}
    sentence = query.split()
    for word in sentence:
        idf_dict_qry[word] = inverseDocumentFrequency(word ,videos)
    return idf_dict_qry

#tf-idf score for the query string
def compute_query_tfidf(query,query_norm_tf,idf_dict_qry):
    tfidf_dict_qry = {}
    sentence = query.split()
    for word in sentence:
        tfidf_dict_qry[word] = query_norm_tf[word] * idf_dict_qry[word]
    return tfidf_dict_qry



#Cosine Similarity(Query,Document1) = Dot product(Query, Document1) / ||Query|| * ||Document1||
def cosine_similarity(tfidf_dict_qry, df , query , doc_num):
    dot_product = 0
    qry_mod = 0
    doc_mod = 0
    tokens = query.split()
   
    for keyword in tokens:
        dot_product += tfidf_dict_qry[keyword] * df[keyword][df['doc'] == doc_num]
        #||Query||
        qry_mod += tfidf_dict_qry[keyword] * tfidf_dict_qry[keyword]
        #||Document||
        doc_mod += df[keyword][df['doc'] == doc_num] * df[keyword][df['doc'] == doc_num]
    qry_mod = np.sqrt(qry_mod)
    doc_mod = np.sqrt(doc_mod)
    #implement formula
    denominator = qry_mod * doc_mod
    cos_sim = dot_product/denominator
     
    return cos_sim

from collections.abc import Iterable
def flatten(lis):
     for video in lis:
        if isinstance(video, Iterable) and not isinstance(video, str):
             for x in flatten(video):
                yield x
        else:        
             yield video

def rank_similarity_docs(data,tfidf_dict_qry,df,query):
    cos_sim =[]
    for doc_num in range(0 , len(data)):
        data[doc_num].similarityScore = cosine_similarity(tfidf_dict_qry, df , query , doc_num).tolist()[0]
    return data

# Query below
def query_search(query,videos):
        query_norm_tf = compute_query_tf(query)
        idf_dict_qry = compute_query_idf(query)
        tfidf_dict_qry = compute_query_tfidf(query,query_norm_tf,idf_dict_qry)
        tf_idf , df = compute_tfidf_with_alldocs(videos , query)

        videos = rank_similarity_docs(videos,tfidf_dict_qry,df,query)
        relevantVideos= [v for v in videos if not isnan(v.similarityScore)]

        sortedResult = sorted(relevantVideos, key = lambda x: x.similarityScore, reverse = True)
        seen_titles = set()
        new_list= [] 
        for obj in sortedResult:
            if obj.docName not in seen_titles:
                new_list.append(obj)
                seen_titles.add(obj.docName)
        res={}
        for idx,video in enumerate(new_list[:10]):
            res[idx] = video.toDict()
            video.myfunc()
        return res


app = Flask('__name__',static_folder="static")
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/process_search')
def gen_search_json():
    start_time = time.time()
    query = request.args.get("q", '')
    q = utils.process_term(query)
    results = utils.get_results(q.strip())
    if(not results):
        results =  [{'id':0,'text':query}]
    resp = jsonify(results=results[:10])  # top 10 results
    resp.headers['Access-Control-Allow-Origin'] = '*'
    end_time = time.time()
    #print("Response time : " + str(end_time - start_time))
    return resp


@app.route('/home', methods=['GET'])
def render_html():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def render_srhtml():
    query = request.args.get("q", '').lower()
    # print(query)
    print(query, file=sys.stdout)
    url = "http://0.0.0.0:5000/do_search?q="+query
    url = url.replace(" ","%20")
    response = urllib.request.urlopen(url)
    data = response.read()
    #autocorrect
    ac = autocorrect.ac(query)
    # diction = data
    diction = json.loads(data)
    print(diction, file=sys.stdout)
    return render_template('searchResults.html', search_results = diction, autocorrect=ac)
    
    

@app.route('/video2')
def get_file2():
    fn = request.args.get("file", '')+".mp4"
    html_string='''<html><head><meta name="viewport" content="width=device-width"></head><body><video controls="" autoplay="" name="media"><source src=static/Data/videos/PLACEHOLDER type="video/mp4"></video></body></html>'''
    start = request.args.get("start", '')
    end = request.args.get("end", '')
    if(start):
    	fn=fn+"#t="+start
    	if(end):
    		fn=fn+","+end
    html_string= html_string.replace("PLACEHOLDER",fn)
    return html_string

@app.route('/video')
def get_file():
    range_header = request.headers.get('Range', None)
    fn = request.args.get("file", '')
    min = request.args.get("min", '')
    min = int(min)
    sec = min*60
    data = {'filename' : fn, 'second' : sec}
    return render_template('linkResult.html', data = data)

@app.route('/vid_summary')
def vid_summary():
    fn = request.args.get("file", '')
    res = vs.generate_summary_modified("./static/Data/text/"+fn+".txt")
    print(res)
    return res
@app.route('/text')
def serveResult():
    fn = request.args.get("file", '')
    s=""
    with open("./static/Data/text/"+fn+".txt", "r") as f:
        for line in f:
            if line ==  '':
                 break
             #line contains key moment info (eg: "0:")
            if line.__contains__(':'):
                 continue
            s+=line[:-1]
    return Response(s, mimetype='text/plain')

@app.route('/thumbnail')
def serveThumbnail():
    fn = request.args.get("file", '')
    fn = "./static/Data/videos/"+fn+".jpg"
    return send_file(filename, mimetype='image/gif')
    
@app.route('/do_search')
def do_search():
    query = request.args.get("q", '')
    print(query)
    return query_search(query,videos)

if __name__== '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
