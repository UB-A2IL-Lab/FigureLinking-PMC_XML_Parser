import os 
import json 
import re 
import sys 
import multiprocessing 
from tqdm import tqdm 

root_dir = "./PMC/"
web_url = "http://sahana.cedar.buffalo.edu/"

def caption_html_gen(subdir):
    for file in os.listdir(os.path.join(root_dir, subdir, "annotation")):
        if file.endswith("ann"):
            annfile_name = os.path.splitext(file)[0]

    html_f = open(root_dir + subdir + "/{}.html".format(subdir), 'w')
    
    html_f.write(
        '''
<p><a style="font-size:28pt"><b>{}</b></a> &nbsp; &nbsp; &nbsp; <a style="font-size: 14pt; text-decoration: underline" href="{}brat/index.xhtml#/{}" target="_blank">[Brat Annotation Tool]</a>
    &nbsp; &nbsp; <a style="font-size: 14pt; text-decoration: underline" href="./{}.pdf" target="_blank">[PDF]</a></p>
    <hr>
        '''.format(subdir, web_url, "PMC" + "/" +subdir+ "/" + "annotation"+ "/"+annfile_name, annfile_name)
    )

    json_f = json.load(open(root_dir + subdir + "/annotation/" + annfile_name +".json", 'r'))
    
    for item in json_f["caption_json"]:
        uid = item["uid"]
        refID = item["refID"]
        caption_text = item["Text"]
        cap_type = item["Type"]

        if cap_type == "Figure":
            fig_href = json_f["imgXML_json"][refID]
            html_f.write(
                '''
<p>
<b>UID:{}</b>
<br>
<br>
Type:{}
<br>
<br>
{}
<br>
<br>
<img src = "./images/{}.jpg">
</p>
<hr>
                '''.format(uid, cap_type, ' '.join(caption_text), fig_href)
            )
        elif cap_type == "Table":
            table_xml = json_f["imgXML_json"][refID]
            html_f.write(
                '''
<p>
UID:{}
<br>
Type:{}
<br>
{}
<br>
<br>
-----------------------------
<br>
<br>
{}
</p>
<hr>
                '''.format(uid, cap_type, ' '.join(caption_text), table_xml)
            )

        

    html_f.close()

subdir_list = os.listdir(root_dir)
pool = multiprocessing.Pool()
for i in tqdm(pool.imap(caption_html_gen, subdir_list), total = len(subdir_list)):
    pass

# caption_html_gen("PMC116597")