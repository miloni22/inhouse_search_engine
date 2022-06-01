import re
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
 
def read_article(file_name):
    file = open(file_name, "r")
    filedata = file.readlines()
    #article = filedata[0].split("\n")
    sentences = []

    for sentence in filedata:
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    sentences.pop() 
    
    return sentences

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []
 
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
 
    all_words = list(set(sent1 + sent2))
 
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
 
    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
 
    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
 
    return 1 - cosine_distance(vector1, vector2)
 
def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
 
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue 
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix

def read_text(fn):
    document=[]
    group_size= 10
    with open(fn,"r") as f: #("./static/Data/text/"+fn+".txt", "r") as f:
        for line in f:
            sentences=[]
            if line ==  '':
                continue
             #line contains key moment info (eg: "0:")
            if line.__contains__(':'):
                 continue
            sentences=line.replace("[^a-zA-Z]", " ").split(" ")[:-1]
            document.append([list(x) for x in list(zip(*(iter(sentences),) * group_size))])
    return document


def generate_summary_modified(file_name,top_n=5):
    document = read_text(file_name)
    res={}
    for idx,sent in enumerate(document):
        res[idx] = generate_summary(sent,1)
    return res

def generate_summary(sentences, top_n=5):
    stop_words = stopwords.words('english')
    summarize_text = []
    #print("Actual sentence: ",sentences)

    # Step 1 - Read text anc split it
    #sentences =  read_article(file_name)
    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
    #print("Indexes of top ranked_sentence order are ", ranked_sentence)    

    for i in range(top_n):
      summarize_text.append(" ".join(ranked_sentence[i][1]))

    # Step 5 - Offcourse, output the summarize texr
    #edit next line if top_n is not 1
    #print(summarize_text[0])
    #summarize_text = re.sub('(\s+)(a|an|and|of|will|with|the)(\s+)', ' ', summarize_text[0])
    #print("Summarize Text: \n",summarize_text)

    #print("Summarize Text: \n", ". ".join(summarize_text))
    return ' '.join(summarize_text[0].split(' ')[:5])

