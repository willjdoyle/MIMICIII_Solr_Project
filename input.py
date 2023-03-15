# input.py
# William Doyle

# manages input GUI and posts query to Solr server

# -------
# Imports
# -------
# used for the GUI
import tkinter as tk
from tkinter import *
from tkcalendar import Calendar
# used for UMLS query expansion
import mysql.connector
from itertools import chain
# used for Solr server queries
import pysolr
from json import loads, dumps

# --------------------
# User Input Variables
# --------------------
handshake = '' # temp global variable for handshaking from callback functions
lowerDateLimit = ''
upperDateLimit = ''

# --------------
# User Input GUI
# --------------
# tkcalendar tutorial pulled from:
# https://www.geeksforgeeks.org/create-a-date-picker-calendar-tkinter/
root = tk.Tk()
root.title('MIMIC III Query Builder')
infoPrompt = StringVar()
label = Label(root, textvariable=infoPrompt)

# --------------------
# Function Definitions
# --------------------
globalFlag = 0

# get_date()
# sets date limit for call with tkinter calendar (for setting high and low date limits)
# passes date to temp global var in format mm/dd/yyyy
def get_date():
    global globalFlag # update flag to break out of while loop
    globalFlag += 1
    global handshake # pass to local variable via this global
    handshake = cal.get_date()

# radio_button()
# sets variable and increments globalFlag once radio option is selected
def radio_button():
    global globalFlag
    globalFlag += 1

# increment_globalFlag()
# simply increments globalFlag so that query can progress
def increment_globalFlag():
    global globalFlag
    globalFlag += 1

# --------
# GUI Code
# --------
# lower calendar limit prompt
# earliest date is 2100-06-07 00:00:00
infoPrompt.set("Enter lower date limit.\nKeep at default value (2100-06-07) for no limit.")
label.pack(pady=20, padx=20)
cal = Calendar(root, selectmode='day', year=2100, month=6, day=7, date_pattern = "yyyy-mm-dd")
cal.pack()

button = Button(root, text="Set Lower Date Limit", command=get_date)
button.pack(pady=10)

while(globalFlag == 0): # wait for first question to be answered
    root.update()
lowerDateLimit = handshake
cal.destroy()
button.destroy()

# upper calendar limit prompt
# latest date is 2210-08-24 00:00:00
infoPrompt.set("Enter upper date limit.\nKeep at default value (2210-08-24) for no limit.")
label.pack(pady=20, padx=20)
cal = Calendar(root, selectmode='day', year=2210, month=8, day=24, date_pattern = "yyyy-mm-dd")
cal.pack()

button = Button(root, text="Set Upper Date Limit", command=get_date)
button.pack(pady=10)

while(globalFlag == 1): # wait for second question to be answered
    root.update()
upperDateLimit = handshake
cal.destroy()
button.destroy()

# expiry flag prompt
expiryFlag = tk.StringVar()
infoPrompt.set("Would you like to specify the expiry flag?")
label.pack(pady=20, padx=20)

r1 = Radiobutton(root, text="Yes, alive.", variable=expiryFlag, value='0', command=radio_button)
r1.pack(pady=5)
r2 = Radiobutton(root, text="Yes, deceased.", variable=expiryFlag, value='1', command=radio_button)
r2.pack(pady=5)
r3 = Radiobutton(root, text="No, don't specify.", variable=expiryFlag, value='*', command=radio_button)
r3.pack(pady=5)

while(globalFlag == 2): # wait for third question to be answered
    root.update()
r1.destroy()
r2.destroy()
r3.destroy()

# icd9 code prompt
infoPrompt.set("Specify a single ICD9 code, or set as '*' to not specify.")
label.pack(pady=20, padx=20)
icd9code = StringVar()
currPrompt = Entry(root, textvariable=icd9code)
root.geometry(str(int(root.winfo_width()*1.3))+"x"+str(int(root.winfo_height()*0.7)))
currPrompt.place(x = int(root.winfo_width()/2), y=int(root.winfo_height()/3), width = 100, height = 20)

button = Button(root, text="Set ICD9 Code", command=increment_globalFlag)
button.pack(pady=15)

while(globalFlag == 3): # wait for fourth question to be answered
    root.update()
currPrompt.destroy()
button.destroy()

# note keyword prompt
infoPrompt.set("Specify a single keyword to search the note text for,\n or set as '*' to not specify.")
label.pack(pady=20, padx=20)
keyword = StringVar()
currPrompt = Entry(root, textvariable=keyword)
root.geometry(str(int(root.winfo_width()*1.3))+"x"+str(int(root.winfo_height()*1.2)))
currPrompt.place(x = int(root.winfo_width()/2), y=int(root.winfo_height()/2), width = 100, height = 20)

button = Button(root, text="Set Keyword", command=increment_globalFlag)
button.place(x = int(root.winfo_width()*31/64), y=int(root.winfo_height()*3/4)) # weird fraction to fix slight offset

while(globalFlag == 4): # wait for fifth question to be answered
    root.update()
currPrompt.destroy()
button.destroy()

# query expansion y/n prompt
queryExpansion = tk.IntVar()
infoPrompt.set("Would you like to perform query expansion via UMLS?")
label.pack(pady=20, padx=20)

r1 = Radiobutton(root, text="Yes.", variable=queryExpansion, value=1, command=radio_button)
r1.pack(pady=5)
r2 = Radiobutton(root, text="No.", variable=queryExpansion, value=0, command=radio_button)
r2.pack(pady=5)

while(globalFlag == 5): # wait for sixth question to be answered
    root.update()
r1.destroy()
r2.destroy()

# and/or question prompt
infoPrompt.set("Specify up 3 &'s (ANDs) or |'s (ORs) for relations between query params.\nFor example, &|&.\nRecall the order was: date limit, expiry flag, icd9 code, keyword.\nMore info and examples provided in the README.txt.")
label.pack(pady=20, padx=20)
operations = StringVar()
currPrompt = Entry(root, textvariable=operations)
root.geometry(str(int(root.winfo_width()*1.3))+"x"+str(int(root.winfo_height()*1.4)))
currPrompt.place(x = int(root.winfo_width()/2), y=int(root.winfo_height()*3/4), width = 100, height = 20)

button = Button(root, text="Set Operations", command=increment_globalFlag)
button.place(x = int(root.winfo_width()*61/128), y=int(root.winfo_height()*0.95)) # weird fraction to fix slight offset

while(globalFlag == 6): # wait for seventh (and final) question to be answered
    root.update()
root.destroy()

# --------------------
# UMLS Query Expansion
# --------------------
# reference code for these SQL queries from Prof. Yu and Prof. Weisong:
# https://github.com/uml-digital-health/Labs/blob/main/UMLS.sql

# connect to UMLS server
conn = mysql.connector.connect(host="172.16.34.1", port="3307", user="umls", password="umls", database="umls2022")
cur = conn.cursor(buffered=True)

if(queryExpansion.get()): # if query expansion enabled
    # query to get CUI for the user's string
    cur.execute("""
    select * 
        from 
            MRCONSO 
        where 
            STR='"""+keyword.get()+"""' 
            and LAT='ENG' 
            and SUPPRESS='N';
    """)

    tempList = cur.fetchall()    
    # check that at least one result was found
    if(len(tempList) == 0): # no matches
        print("No synonym matches found! Skipping query expansion.")
        #cui = []
        synonyms = []
        synonyms.append(keyword.get())
    else: # matches found
        cui = tempList[0][0]

        # query to find all synonyms using the found cui
        cur.execute("""
        select distinct STR 
            from MRCONSO 
            where 
                CUI='"""+cui+"""' 
                and LAT='ENG' 
                and SUPPRESS='N';
        """)
        tempList = cur.fetchall()
        synonyms = tempList

else: # query expansion not enabled
    synonyms = []
    synonyms.append(keyword.get())

# limit to 30 synonyms
synonyms = synonyms[0:30]

# -------------------------
# POST Query to Solr Server
# -------------------------
solr = pysolr.Solr('http://localhost:8983/solr/mimiciii')

# check that Solr Server is running
ping = loads(solr.ping()) # need to add some conditional here to check
if(ping['status'] != 'OK'):
    print("ERROR: Could not connect to Solr server. Have you tried running 'start_solr.sh'?")
    quit(0)

# process operators (convert & -> AND and | -> OR)
operationsProcessed = []
for i in range(len(operations.get())):
    if(operations.get()[i] == '&'):
        operationsProcessed.append('AND')
    else:
        operationsProcessed.append('OR')

# create Solr query
query = ""
# add date
query += f"chartdate:[{lowerDateLimit}T00:00:00Z TO {upperDateLimit}T00:00:00Z]"
query += f" {operationsProcessed[0]} "
# add expiry flag
query += f"hospital_expire_flag:{expiryFlag.get()}"
query += f" {operationsProcessed[1]} "
# add icd9 code
query += f"icd9_code:{icd9code.get()}"
query += f" {operationsProcessed[2]} "

# query for each synonym found
results = []
for synonym in synonyms:
    queryComplete = query + f"note_text:{synonym}"
    results.append(solr.search(queryComplete))
print(results)
# write results to results/<row_id>.json
for result in results:
    for doc in result:
        f = open(f"results/{doc['id']}.json", "w")
        f.write(dumps(doc, indent=4))
        f.close()

# ----------
# Disconnect
# ----------
print("All done! Please check the results folder for the retrieved docs!")
cur.close()
conn.close()