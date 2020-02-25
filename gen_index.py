import os 
import json 

root_dir = "./PMC/"
server_root_dir = "./brat/data/PMC/"
web_url = "http://sahana.cedar.buffalo.edu/"

with open("./index_pmc.html", 'w') as h_f:
    h_f.write(
        '''
<p style="font-size:26pt">PMC:</p>
        '''
    )

    for sub_dir in os.listdir(root_dir):
        sub_dir_path = os.path.join(root_dir, sub_dir)
        

        h_f.write(
            '''
    <a style="font-size:18pt" href = "{}">[{}]</a>
            '''.format(server_root_dir+ sub_dir + "/" + sub_dir + ".html", sub_dir)
        )

    
    h_f.write(
        '''
<p><br><br><br><br><a style="font-size:16pt; text-decoration:underline; color:red" href = "./index.html"> [back] </a></p>
        '''
    )