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

class nxmlParser():
    def __init__(self):
        self.filename = ""
        self.tags_list = ["fig", "table"]
        # refID_attr is used to indicate the image refered by rid is a 
        # table or figure
        self.refID_attr = {}
        
        # markerKey_uid is used to find the sentences and link this sentences to unique id
        # which would be showed in brat (replace the num)
        self.markerkey_refID = {}

        self.refID_list = []
        # uid_refID is used to make markerkey --> refID --> uid, a closed circle
        self.refID_uid = {}

        # dref_json is a json file stores all direct reference with uid
        self.dref_json = []

        # caption_json is a json file stores all captions with corresponded uid
        self.caption_json = []

    def breakblankRemover(self, txtfile):
        txtfile = unidecode.unidecode(txtfile)
        nobreakline_txt = re.sub("[\n\r\t]", " ", txtfile)
        reduce_blank_txt = re.sub(" +", " ", nobreakline_txt)
        # print(reduce_blank_txt)
        reduce_blank_txt = str.encode(reduce_blank_txt)
        open(tmp_dir + "/nobreakblank.txt", 'wb').write(reduce_blank_txt)
        afterRemover_txt = open(tmp_dir + "/nobreakblank.txt", 'r').read()
        # writing and re-reading prevent small difference in brat 'rU' span error
        return afterRemover_txt

    
    def segmentPureText(self, txtfile):
        punkt_param = PunktParameters()
        abbreviation = ["U.S.A","u.s.a", "Fig", "fig", "Table", "table", "Eq", "eq", "equation", "et al","e.g", "i.e","Fig"]
        punkt_param.abbrev_types = set(abbreviation)
        tokenizer = PunktSentenceTokenizer(punkt_param)
        tokenized_output = tokenizer.tokenize(txtfile)
        # print(tokenized_output)

        return tokenized_output
    
    def addMarkersToXref(self):
        count = 1
        for ref in soup.find_all("xref"):
            # only count and add marker to table or fig
            try:
                ref["ref-type"]
            except KeyError:
                ref["ref-type"] = "NoRef"

            if ref["ref-type"] in ("table", "fig"):
                # marker_key is #directreference-head#{uid.:05}#
                marker_key = '#directreference-head#{:05}#'.format(count)

                if ref.string is None:
                    ref.string = marker_key
                else:
                    ref.string = ref.string + marker_key

                refID = ref["rid"]

                if refID not in self.refID_attr:
                    if ref["ref-type"] == "table":
                        self.refID_attr[refID] = "Table"
                    elif ref["ref-type"] == "fig":
                        self.refID_attr[refID] = "Figure"

                self.markerkey_refID[marker_key] = refID
                if refID not in self.refID_list:
                    self.refID_list.append(refID)

                count +=1
        
        # Creat the uid which is 1-1 matched with refID
        uid = 1
        for refID in self.refID_list:
            self.refID_uid[refID] = uid
            uid += 1 

    def getDirectReferences(self, sents_list):
        # get direct references and remove the direct references mark 
        # in the text or sentences list
        for idx, sent in enumerate(sents_list): 

            if "#directreference-head#" in sent:
                # Handle one sent has multi marker
                sameSent_Marker = []
                while(True):
                    if "#directreference-head#" in sent:
                        marker = sent[sent.find("#directreference-head#"):sent.find("#directreference-head#")+28]
                        sameSent_Marker.append(marker)
                        sent = sent.replace(marker,'')
                        sents_list[idx] = sent
                    else:
                        break
                print(sameSent_Marker)
                for marker in sameSent_Marker:
                    drsent_dic = {}
                    refID = self.markerkey_refID[marker]
                    refID_attr = self.refID_attr[refID]

                    drsent_dic["uid"] = self.refID_uid[refID]
                    drsent_dic["Type"] = refID_attr
                    drsent_dic["Text"] = sent
                    drsent_dic["refID"] = refID
                    # self.dref_json[uid] still needs the span
                    self.dref_json.append(drsent_dic)
        # print(sents_list)
        # print(json.dumps(self.dref_json,indent=4))
        return sents_list

        ## The sents_list now is without direct reference marker anymore.

    # Complete this two functions later to add caption markers to 
    def addMarkersToCaption(self):
        pass




    def getCaptions(self, sents_list):
        pass

    def getSpan_writeTxt(self, sents_list, finalTxt_path):
        with open(finalTxt_path, 'w') as f:
            for sent in sents_list:
                f.write(sent +"\n")
        
        finalTxt = open(finalTxt_path, 'r').read()

        for item in self.dref_json:
            item_sent = item["Text"]
            item_sent_length = len(item_sent)
            
            span_st = finalTxt.find(item_sent)
            span_ed = span_st + item_sent_length 

            item["Span"] = [span_st, span_ed]

            if span_st == -1:
                with open(log_dir + filename + ".txt", 'w') as f:
                    f.write(item_sent+"\n")

        print(json.dumps(self.dref_json,indent=4))

        ## Calculate the caption span with caption json
        # Adding Code......

    def writeANN(self, finalANN_path):
        t_num = 1
        a_num = 1
        with open(finalANN_path, "w") as f:
            for item in self.dref_json:
                T_line = "T{}\tReference {} {}\t{}\n".format(t_num, item["Span"][0], item["Span"][1], item["Text"])
                f.write(T_line)

                A1_line = "A{}\tRefType T{} Direct\n".format(a_num, t_num)
                a_num += 1
                f.write(A1_line)

                A2_line = "A{}\tType T{} {}\n".format(a_num,t_num,item["Type"])
                a_num += 1
                f.write(A2_line)

                A3_line = "A{}\tUID T{} {}\n".format(a_num, t_num, item["uid"])
                a_num += 1
                f.write(A3_line)

                t_num += 1
























'''
---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------
                                            DRIVER'S CODE
---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------
''' 


rootdir = './data/'
img_ext = ('.jpg', '.gif', '.png', '.tif')

des_dir = "./PMC/"
tmp_dir = "./tmp/"

log_dir = "./log/"

if not os.path.exists(des_dir):
    os.mkdir(des_dir)
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

unsuccess_list = []

for subdir in os.listdir(rootdir):
    # subdir = "PMC116597"
    subdir_path = os.path.join(rootdir, subdir)
    for curr_file in os.listdir(subdir_path):
        curr_file_path = os.path.join(subdir_path, curr_file)

        curr_subdir = des_dir + subdir
        currPath = des_dir + subdir + "/annotation/"
        currImgPath = des_dir + subdir + "/images/"

        if not os.path.exists(curr_subdir):
            os.mkdir(curr_subdir)
        if not os.path.exists(currPath):
            os.mkdir(currPath)
        if not os.path.exists(currImgPath):
            os.mkdir(currImgPath)

        
        if curr_file.lower().endswith('.nxml'):  
            print('Processing file: ', curr_file_path, '\n')
            infile = open(curr_file_path, "r")
#subdir = 'PMC3016212/'
#curr_file = '228_2010_Article_901.nxml'
#print('Processing file: ', subdir + '/' + curr_file, '\n')
#infile = open(subdir + '/' + curr_file, "r")
            soup = BeautifulSoup(infile, 'xml')
            filename = os.path.splitext(curr_file)[0]
            
            curr_doc = nxmlParser()
            curr_doc.filename = filename
            
            curr_doc.addMarkersToXref()
            
            ## Get pure text

            parsed_doc_text = soup.get_text()

            ## Remove all the \n \r and multi blank and form it into a nearly perfect whole paragraph
            parsed_doc_text = curr_doc.breakblankRemover(parsed_doc_text)

            ## Segment the text into sentences level
            sentences_list = curr_doc.segmentPureText(parsed_doc_text)
            
            sentences_list = curr_doc.getDirectReferences(sentences_list)

            ##
            # Creating the final txt file. 
            # Find the corresponded span
            ##

            curr_doc.getSpan_writeTxt(sentences_list, currPath + filename + ".txt")

            curr_doc.writeANN(currPath + filename + ".ann")


        if curr_file.lower().endswith(('png', 'jpg', 'tif', 'gif', 'mov', 'mp4')):
            shutil.copy2(curr_file_path, currImgPath)
        if curr_file.lower().endswith(('nxml', 'xml', 'pdf')):
            shutil.copy2(curr_file_path, curr_subdir)

        print('\nFinished processing file: ', curr_file_path, '\n')
        print('----------------------------------------\n\n')

    # break