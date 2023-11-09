import os
import re
import streamlit as st
import torch
import logging
import sys


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

# device = "cpu"
modelsBaseFolder = "models/"

@st.cache_data
def loadModel(model_name,device):
    logger.info(f"loading model {model_name}... [on {device}]")
    model = torch.load(os.path.join(modelsBaseFolder, model_name), map_location=device)
    model.device = device
    return model

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def convertText(f, window_size=3, labelID="demo", limit=1000):

    outString = ""

    book_sentences_list = []
    tmp_sentence = []
    index_to_print = dict()

    book_counter = 0

    for line in f:
        
        line = line.strip()
        if len(line) < 1:
            continue

        accented_chars = 'àèìòùÀÈÌÒÙáéíóúýÁÉÍÓÚÝâêîôûÂÊÎÔÛãñõÃÑÕäëïöüÿÄËÏÖÜŸçÇßØøÅåÆæœ'
        line = re.sub(r'([^a-zA-Z' + accented_chars + '0-9])', ' \\1 ', line)
        line = re.sub(r'\s+', ' ', line)
        line = line.strip()
        # line = re.sub(' +', ' ', line)
        parts = line.split(" ")

        for p in parts:
            tmp_sentence.append(p)

            if p == ".":
                book_sentences_list.append(tmp_sentence)
                tmp_sentence = []
    
    if len(tmp_sentence) > 0:
        book_sentences_list.append(tmp_sentence)

    for sentence in enumerate(book_sentences_list):
        lowlist= [x.lower() for x in sentence[1]]
        if sentence[0] - window_size < 0:
            for i in range(sentence[0], sentence[0] + window_size + 1):
                index_to_print[i] = True
        else:
            for i in range(sentence[0]-window_size, sentence[0] + window_size + 1):
                index_to_print[i] = True
    
    total_word_counter = 0
    for k in dict(sorted(index_to_print.items())):
        if limit > 0 and total_word_counter > limit:
            break

        sentence_counter = k
        word_counter = 0
        try:
            for token in book_sentences_list[k]:
                word_counter += 1
                total_word_counter += 1
                tokenID = str(sentence_counter) + "-" + str(word_counter)
                outString += labelID + str(book_counter) + "\t" + tokenID + "\t-\t" + token + "\tO\tO\tO\tO\tO\tO\tO\tO\tO\tO\n"
            outString += "\n"
        except:
            out_of_range = True

    return outString

def add_colors(mytuple):
    colorcodes = {
        "Smell Word": "#a3ccea",
        "Smell Source": "#76b7b2",
        "Evoked Odorant": "#59a14f",
        "Quality": "#b07aa1",
        "Location": "#edc949",
        "Time": "#bab0ad",
        "Odour Carrier": "#f28e2b",
        "Perceiver": "#e1575a",
        "Circumstances": "#bab0ad",
        "Effect": "#fbc0d2" 
    }

    tuples_colors = []
    for t in mytuple:
            if len(t) == 1:
                tuples_colors.append(t[0])
            else:
                try:
                    t = t + (colorcodes[t[1]], )
                except:
                    no_color = True
                
                tuples_colors.append(t)
    
    return tuples_colors

def predictions_to_tuples(myfile):
    file = open(myfile, 'r')
    prediction_list = []
    for line in file:
        line = line.strip("\n")
        parts = line.split("\t")
        if len(parts) == 1 :
            # print(prediction_list)
            prediction_list.append("\n")
        
        found = False
        for x in range(4, len(parts)):
            if parts[x].startswith("B-") or parts[x].startswith("I-") and not found:
                prediction_list.append([parts[3],parts[x]])
                found = True
        # print(found)
        if not found and len(parts) != 1:
            prediction_list.append([parts[3], "O"])
    

    prediction_list.append(["","O"])        
    frames_list = []
    inside_frame = False
    for x in range(0,len(prediction_list)):
        if len(prediction_list[x]) == 1: 
            frames_list.append([str(prediction_list[x][0])])
            continue
        if prediction_list[x][1] == "O":
            if inside_frame:
                frames_list.append(tmp_list)
                inside_frame = False
            frames_list.append([" " +str(prediction_list[x][0]) + " "])
        
        if prediction_list[x][1].startswith("B-"):
            if inside_frame:
                frames_list.append(tmp_list)
                tmp_list = [str(prediction_list[x][0]),prediction_list[x][1].replace("B-", "").replace("_", " ")]
            if not inside_frame:
                tmp_list = [str(prediction_list[x][0]),prediction_list[x][1].replace("B-", "").replace("_", " ")]
                inside_frame = True
        if prediction_list[x][1].startswith("I-") and inside_frame:
            tmp_list[0] = tmp_list[0] + " " + str(prediction_list[x][0])
    

    tuples = [tuple(x) for x in frames_list]
    # for count, item in enumerate(tuples):
    #     print(count, item)
    return(tuples)

