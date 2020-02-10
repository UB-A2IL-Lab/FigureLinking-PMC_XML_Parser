from bs4 import BeautifulSoup
import os
import shutil
import re
import json
import spacy
from nltk import tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
import sys

nlp = spacy.load('en_core_web_sm')

