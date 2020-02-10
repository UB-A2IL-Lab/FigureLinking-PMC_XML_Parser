import os 
import json 

root_dir = "PMC/"
web_url = "http://sahana.cedar.buffalo.edu/"

with open("./index_pmc.html", 'w') as h_f:
    h_f.write(
        '''
<p style="font-size:26pt">PMC:</p>
        '''
    )

    for sub_dir in os.listdir(root_dir):
        sub_dir_path = os.path.join(root_dir, sub_dir, "annotation")
        
        for file in os.listdir(sub_dir_path):
            if file.endswith('ann'):
                annfile_name = os.path.splitext(file)[0]

        h_f.write(
            '''
    <a style="font-size:18pt" href = "{}brat/index.xhtml#/{}">[{}]</a>
            '''.format(web_url, sub_dir_path + "/" + annfile_name, sub_dir)
        )

    
    h_f.write(
        '''
<p><br><br><br><br><a style="font-size:16pt; text-decoration:underline; color:red" href = "./index.html"> [back] </a></p>
        '''
    )