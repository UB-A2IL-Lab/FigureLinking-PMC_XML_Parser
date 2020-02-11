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
        self.markerkey_uid = {}

        # uid_refID is used to make markerkey --> uid --> refID, a closed circle
        self.uid_refID = {}

        # dref_json is a json file stores all direct reference with uid
        self.dref_json = {}

        # caption_json is a json file stores all captions with corresponded uid
        self.caption_json = {}




    def addMarkersToXref(self):
        count = 1
        for ref in soup.find_all("xref"):
            # only count and add marker to table or fig
            if ref["ref-type"] in ("table", "fig"):
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
                uid = count
                self.markerkey_uid[marker_key] = uid
                self.uid_refID[uid] = refID
                

                count +=1

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
        abbreviation = ["U.S.A","u.s.a", "Fig.", "fig.", "Table.", "table.", "Eq.", "eq.", "equation.","i.e.","e.g."]
        punkt_param.abbrev_types = set(abbreviation)
        tokenizer = PunktSentenceTokenizer(punkt_param)
        tokenized_output = tokenizer.tokenize(txtfile)
        # print(tokenized_output)

        return tokenized_output

    def getDirectReferences(self, sents_list):
        for idx, sent in enumerate(sents_list): 

            # Handle one sent has multi marker
            sameSent_Marker = []
            while(True):
                if "#directreference-head#" in sent:
                    marker = sent[sent.find("#directreference-head#"):sent.find("#directreference-head#")+28]
                    sameSent_Marker.append(marker)
                    sent = sent.replace(marker,'')
                else:
                    break
            print(sameSent_Marker)
            for marker in sameSent_Marker:
                uid = self.markerkey_uid[marker]
                refID =self.uid_refID[uid]
                refID_attr = self.refID_attr[refID]

                self.dref_json[uid] = {}
                self.dref_json[uid]["Type"] = refID_attr
                self.dref_json[uid]["Text"] = sent
                # self.dref_json[uid] still needs the span
        
        print(json.dumps(self.dref_json,indent=4))

            























'''
---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------
                                            DRIVER'S CODE
---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------
''' 


rootdir = './sample_data/'
img_ext = ('.jpg', '.gif', '.png', '.tif')
log_file = open('log_file.txt', 'w+', encoding = "utf8")

des_dir = "./PMC/"
tmp_dir = "./tmp/"

if not os.path.exists(des_dir):
    os.mkdir(des_dir)
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

unsuccess_list = []

for subdir in os.listdir(rootdir):
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
            soup_original = soup
            soup_copy = soup
            filename = os.path.splitext(curr_file)[0]
            
            curr_doc = nxmlParser()
            curr_doc.filename = filename
            
            curr_doc.addMarkersToXref()
            
            ## Get pure text
            soup_copy = soup_original
            parsed_doc_text = soup.get_text()

            ## Remove all the \n \r and multi blank and form it into a nearly perfect whole paragraph
            parsed_doc_text = curr_doc.breakblankRemover(parsed_doc_text)

            ## Segment the text into sentences level
            sentences_list = curr_doc.segmentPureText(parsed_doc_text)
            
            curr_doc.getDirectReferences(sentences_list)
            # curr_doc.getCaptions()
            
            # Verify that all three lists have the same size
            #            print (len(curr_doc.sent_ref_points), len(curr_doc.all_sent_parsed), len(curr_doc.all_sent_original) )
            
            '''
            Creating the all_sentences.txt file. 
            Segment the sentences and dump each sentence on one line of the file.
            '''
            # try: 
            #     os.mkdir(subdir + "/annotation") 
            # except(FileExistsError): 
            #     pass

            #            print(currPath,'\n')
            
            curr_doc.createAllSentencesFile(currPath)
            #            curr_doc.showCaptions()
            curr_doc.compileDRefCaptions(currPath)
            d = curr_doc.captions_DRef_dict
            print (d, '\n\n')
            
            # curr_doc.createLogFileDicts()
            # writeToLogFile(currPath, curr_doc.filename, curr_doc.log_file_references, curr_doc.log_file_caption)

            curr_doc.createJSONFile(soup_original, currPath, subdir)
            curr_doc.createANNfile(currPath)


        if curr_file.lower().endswith(('png', 'jpg', 'tif', 'gif', 'mov', 'mp4')):
            shutil.copy2(curr_file_path, currImgPath)
        if curr_file.lower().endswith(('nxml', 'xml', 'pdf')):
            shutil.copy2(curr_file_path, curr_subdir)

        print('\nFinished processing file: ', curr_file_path, '\n')
        print('----------------------------------------\n\n')