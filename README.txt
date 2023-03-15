William Doyle
COMP.5520 Foundations of Digital Health Project #2: MIMIC III

GITHUB LINK:
https://github.com/willjdoyle/MIMICIII_Solr_Project

SUMMARY:
This project creates a Solr server and indexes the discharge summary notes from the MIMIC III database. Then, the user can use a GUI
to create a query and view each of the returned documents. The query GUI allows for user to change the lower and upper date bounds, 
expiration flag, ICD9 code, and keyword. It allows for AND and OR relations, as well as query expansion on the keyword via the UMLS 
database.

REQUIREMENTS:
The OS used for all testing and development was Ubunutu 20.04.5 LTS. Please note that you will need to connect to the UML VPN before 
running anything in this project. Apache Solr version 9.1.1 was used. Python 3.8.10 was used.

The following Python libraries are necessary:
psycopg2==2.9.5
pandas==1.5.3
pysolr==3.9.0
tqdm==4.64.1
tkinter==8.6
tkcalendar==1.6.1
mysql-connector-python=8.0.32
more-itertools=4.2.0

FILES:
index.py - This file will connect to UML's MIMIC III page, grab each discharge note (and the ICD9 codes associated with the hospital 
admission IDs), and index them to the Solr server (running on localhost:8983 and with a core name of "mimiciii". NOTE: this program 
will take some time to run at first, estimated at 25 minutes to query the data and re-post it to Solr. You should only need to run it 
once, as the Solr documents persist between restarts (unless you delete the documents). You will need to RESTART the Solr server after
running index.py to see the changes (using stop_solr.sh and start_solr.sh). This is because 'autocommit' is turned off, which reduced
indexing time from 1h40m to ~18m.

input.py - This file brings up a tkinter GUI for the user to build their query, one prompt at a time (example given in 'SAMPLE RUN' 
section). If query expansion was enabled, then the server will check for the first 30 synonyms on UML's UMLS server. When completed, 
the returned docs are stored as <row_id>.json files in the /results folder.

start_solr.sh - Will start the Solr server, assuming that this file is placed in your home folder. If not, run:
bin/solr start -s <file_path>/<name_of_this_folder>/solr/mimiciii/
from your Solr installation folder.

stop_solr.sh - Will stop the Solr server. It should be path independent, but if not, navigate to your Solr installation folder and run:
bin/solr stop

clear_solr.sh - THIS WILL DELETE ALL YOUR INDEXED SOLR DOCUMENTS. Only run if you want to rerun index.py and wait for it to complete
again. When the Solr server is running, clear_solr.sh will send a CURL to localhost:8983 and delete all docs from the mimiciii core.

/results - When running a query with input.py, all returned docs will be placed in this folder as .json files.

/solr - This folder contains various Solr server information for this project (core: 'mimiciii'), including solrconfig.xml and 
managed-schema.xml. The indexed data in stored in <project_path>/solr/mimiciii/data/index, and will be ~500MB.

/testing_results - For each of the five evaluation/testing conditions given towards the end of the project assignment document, a 
folder named 'eval1', 'eval2', etc has been created and contains the .json files from running that query.

/screenshots - Contains screenshots for query GUI input for testing condition #2 (note_text:'Car crash' AND hospital_expire_flag:1).

KNOWN ISSUES:
Not an error, but please note that indexing all the hospital discharge notes will take around 25 minutes in total, between pulling the 
data and uploading to Solr. Don't delete them until you no longer need them.

Some of the queries also don't respond exactly the same as performing the queries on the Solr server webpage, and I believe this has to 
do with the '\n' newline characters spread throughout the note texts, or with how Solr treats "exactness" and query expansion. 

I ran out of time to address the above two issues, but after a couple hours of testing, I couldn't find any more errors/issues.

SAMPLE RUN:
For this sample run, let's find the notes using testing condition #2, which is "Car crash" and hospital_expire_flag = 1. If this is the
first time running this project, the setup producedure will be:
1) Connect to the UML VPN
2) ./start_solr.sh
3) ./index.py
4) ./stop_solr.sh
5) ./start_solr.sh

Once this is done, run input.py. IF THERE ARE ANY RUNTIME ERRORS, please contact me-- it is likely due to a Solr directory/filepath issue.
The GUI from input.py will ask you the following prompts: lower date limit, upper date limit, expiry flag, (one) ICD9 code, (one) keyword,
confirming query expansion, and then the relational operators between the dates, expiry flag, ICD9 code, and keyword. So, if you had a
parameters set for each of those query values, writing '&|&' will become chartdate:<dates> AND expiry:<expiry> OR icd9_code:<icd9> AND
note_text:<keyword>.

The screenshots showing each of query answers for testing condition #2 are shown in the /screenshots folder. The two queries created 
(since query expansion was selected, even though the default option in the screenshot highlights "no") were:
"chartdate:[2100-06-07T00:00:00Z TO 2210-08-24T00:00:00Z] AND hospital_expire_flag:1 AND icd9_code:* AND note_text:('car accident',)"
"chartdate:[2100-06-07T00:00:00Z TO 2210-08-24T00:00:00Z] AND hospital_expire_flag:1 AND icd9_code:* AND note_text:('car crash',)"

The 18 resulting .json files are found in /testing_results/eval2.
