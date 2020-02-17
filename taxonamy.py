from bs4 import BeautifulSoup
import os
import shutil
import re
import json
import spacy
from nltk import tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
import sys
import unidecode

nlp = spacy.load('en_core_web_sm')

rootdir = './data/'
img_ext = ('.jpg', '.gif', '.png', '.tif')

tag_all = []

for subdir in os.listdir(rootdir):
    subdir_path = os.path.join(rootdir, subdir)
    for curr_file in os.listdir(subdir_path):
        curr_file_path = os.path.join(subdir_path, curr_file)

        if curr_file.lower().endswith('.nxml'):  
            infile = open(curr_file_path, "r")
            soup = BeautifulSoup(infile, 'xml')

            for ref in soup.find_all("xref"):
                try:
                    ref["ref-type"]
                except KeyError:
                    ref["ref-type"] = "None"
                if ref["ref-type"] not in tag_all:
                    tag_all.append(ref["ref-type"])
            
            for caption in soup.find_all("table"):
                print(caption)

print(tag_all)