# William Doyle
# COMP.5520-201 Foundations in Digital Health
# Lab #2
# Due 3/15/23

# Lab #2 - MIMIC III
# -

# Used the following Github repo as base to understand code better:
# https://github.com/MIT-LCP/mimic-iii-paper/tree/master/notebooks

# -------
# Imports
# -------
import psycopg2
import pprint
import warnings
import pandas as pd
import pysolr
from json import loads
import tqdm

# ---------------------------
# Suppress Redundant Warnings
# ---------------------------
warnings.simplefilter(action='ignore', category=UserWarning)

# -------------
# Query Defines
# -------------
baseQuery = """
SELECT a.hadm_id, n.row_id, n.chartdate, n.text, a.hospital_expire_flag
FROM admissions a, noteevents n
WHERE a.hadm_id = n.hadm_id AND n.category = 'Discharge summary';
"""

icd9Query = """
SELECT i.icd9_code from diagnoses_icd d, d_icd_diagnoses i
WHERE d.icd9_code = i.icd9_code AND hadm_id = 
""" # specific hadm_id added when running the query

# -------------------
# Connect to Database
# -------------------
conn = psycopg2.connect(host="172.16.34.1", port="5432", user="mimic_demo", password="mimic_demo", database="mimic")
cur = conn.cursor()

cur.execute('SET search_path to mimiciii')

# ---------
# Run Query
# ---------
# query is split to save processing time-- first query is everything except icd9 codes
# thank you to Prof. Weisong for this idea; code reference:
# https://github.com/uml-digital-health/Labs/blob/main/IR_files/index_mimic.py
results = pd.read_sql_query(baseQuery,conn)

# first, create a list of the unique hadm_ids
hadm_ids = [*set(results['hadm_id'])]

# next, find the set of icd9 codes for each of the hadm_ids
icd9codes = {} # try to make this one query??? takes too long for 50k values
for i in tqdm.tqdm(range(len(hadm_ids))):
    icd9codes[hadm_ids[i]] = pd.read_sql_query(icd9Query + str(hadm_ids[i]) + ';', conn)

# ---------------
# Connect to Solr
# ---------------s
solr = pysolr.Solr('http://localhost:8983/solr/mimiciii', always_commit=False)
# note: NEED TO RESTART SOLR SERVER AFTER THIS

# ensure that Solr server is up
ping = loads(solr.ping()) # need to add some conditional here to check
if(ping['status'] != 'OK'):
    print("ERROR: Could not connect to Solr server. Have you tried running 'start_solr.sh'?")
    quit(0)

# -------------------
# Adding Docs to Solr
# -------------------
for i in tqdm.tqdm(range(len(results))):
    # need to convert from pandas to solr date format
    formattedDate = str(results['chartdate'][i])[0:10]
    formattedDate += 'T00:00:00Z'

    solr.add([
        {
            "id": int(results['row_id'][i]),
            "hadm_id": int(results['hadm_id'][i]),
            "chartdate": formattedDate,
            "note_text": str(results['text'][i]),
            "hospital_expire_flag": int(results['hospital_expire_flag'][i]),
            "icd9_code": str(icd9codes[int(results['hadm_id'][i])]),
        },
    ])

# ----------
# Disconnect
# ----------
cur.close()
conn.close()