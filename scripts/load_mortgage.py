# -*- coding: utf-8 -*-

"""
Best tools for reading from PDF files:
* PDFMiner
  * project page:
    * https://github.com/euske/pdfminer
  * notes:
    * Mostly handles text data
  * recommended in:
    * https://medium.com/@umerfarooq_26378/python-for-pdf-ef0fac2808b0
    * http://theautomatic.net/2020/01/21/how-to-read-pdf-files-with-python/
* PyPDF2
  * project page:
    * https://github.com/mstamy2/PyPDF2
  * note:
    * actions on pdfs: read, write, edit, merge etc.
  * recommended in:
    * https://medium.com/@umerfarooq_26378/python-for-pdf-ef0fac2808b0
    * https://www.geeksforgeeks.org/working-with-pdf-files-in-python/
    * https://stackoverflow.com/a/45795353/1333305
    * https://www.codespeedy.com/read-pdf-file-in-python-line-by-line/
* Tabula-py
  * project page:
    * https://github.com/chezou/tabula-py
  * note:
    * Handles tables in pdfs!
  * recommended in:
    * https://medium.com/@umerfarooq_26378/python-for-pdf-ef0fac2808b0
* Slate
  * project page:
    * https://github.com/timClicks/slate
  * note:
    * wrapper for PDFMiner
  * recommended in:
    * https://medium.com/@umerfarooq_26378/python-for-pdf-ef0fac2808b0
* PDFQuery
  * project page:
    * https://github.com/jcushman/pdfquery
  * note:
    * wrapper for PDFMiner, lxml, pyquery. queries pdfs.
  * recommended in:
    * https://medium.com/@umerfarooq_26378/python-for-pdf-ef0fac2808b0
* Tika
  * project page:
    * https://github.com/chrismattmann/tika-python
  * note:
    * They keep saying how it's better than PyPDF2 and PDFMiner.
  * recommended in:
    * https://stackoverflow.com/a/48673754/1333305
    * https://stackoverflow.com/a/54936587/1333305
* pdftotext
  * project page:
    * https://github.com/jalan/pdftotext
  * note:
    * It's not python, it's a binary that needs to run as its own process, and reads its output (usage example in the recommendation link).
  * recommended in:
    * https://stackoverflow.com/a/49265359/1333305
    * https://stackoverflow.com/a/55494972/1333305
* PyMuPDF
  * project page:
    * https://pymupdf.readthedocs.io/en/latest/tutorial/
  * note:
    * Some claim it's the best out there.
  * recommended in:
    * https://stackoverflow.com/a/51687608/1333305
    * https://stackoverflow.com/a/47797074/1333305
* pdfrw
  * project page:
    * https://github.com/pmaupin/pdfrw
  * note:
    * Seems to have extensive features.
  * recommended in:
    * https://realpython.com/pdf-python/
"""

import os
import re
import pprint
import tabula
import datetime as D
import pandas as pd
import unittest

def to_float(s):
    return float(s.replace(",",""))

# A TestCase instance to call assertions on, for mroe elegant messages
T = unittest.TestCase()

REPORTS_FOLDER = r"/Users/oferbr/Documents/mortgage/reports"
MONTHLY_REPORT_FNAME_RE = r"(\d+)_monthly\.pdf"
DATE_RE = "%Y%m%d"
ALLOWED_SUM_DIFF_NIS = 1.0

TRACK_INFO = [
  {"id": "6200349019546‬"},
  {"id": "6200349019645‬"},
  {"id": "6210349019248‬"},
  {"id": "6248349019427‬"},
  {"id": "6279349019323"},
]
TRACK_DICT = {ti["id"]:ti for ti in TRACK_INFO}
NUM_RE = r"\d+[\d\,]*\.?\d*"
TRACK_RE_CONFIG = [
  {"idx":0, "re":fr"15י *ום חיוב:(\d+)מספר הלוואה:", "groups":[(1, "track_id", str),]},
  {"idx":1, "re":fr"({NUM_RE})\s*ריבית:", "groups":[(1, "interest", to_float),]},
  {"idx":2, "re":fr"({NUM_RE})\s*הצמדת קרן:", "groups":[(1, "fund_indexing", to_float),]},
  {"idx":3, "re":fr"({NUM_RE})\s*קרן", "groups":[(1, "fund", to_float),]},
  {"idx":4, "re":fr"({NUM_RE})\s*ביטוח מבנה:", "groups":[(1, "building_insurance", to_float),]},
  {"idx":5, "re":fr"({NUM_RE})\s*ריבית בינים:", "groups":[(1, "mid_interest", to_float),]},
  {"idx":6, "re":fr"({NUM_RE})\s*הצמדת ריבית:", "groups":[(1, "interest_indexing", to_float),]},
  {"idx":7, "re":fr"({NUM_RE})\s*עמלות:", "groups":[(1, "commission", to_float),]},
  {"idx":8, "re":fr"({NUM_RE})\s*הוצאות משפט:", "groups":[(1, "legal_expense", to_float),]},
  {"idx":9, "re":fr"({NUM_RE})\s*ביטוח חיים:", "groups":[(1, "life_insurance", to_float),]},
  {"idx":10, "re":fr"({NUM_RE})", "groups":[(1, "total_pay", to_float),]},
  {"idx":11, "re":fr'סה"כ:', "groups":[]},
  {"idx":12, "re":fr"({NUM_RE})\s*הוצאות אחרות:", "groups":[(1, "other_expense", to_float),]},
  {"idx":13, "re":fr"({NUM_RE})\s*אגרת רישום:", "groups":[(1, "registration_fee", to_float),]},
]
TRACK_TOTAL_RE_CONFIG = [
  {"idx":0, "re":fr'({NUM_RE})סה"כ ללווה:', "groups":[(1, "total_pay", to_float),]},
  {"idx":1, "re":fr"({NUM_RE})\s*ריבית:", "groups":[(1, "interest", to_float),]},
  {"idx":2, "re":fr"({NUM_RE})\s*הצמדת קרן:", "groups":[(1, "fund_indexing", to_float),]},
  {"idx":3, "re":fr"({NUM_RE})\s*קרן", "groups":[(1, "fund", to_float),]},
  {"idx":4, "re":fr"({NUM_RE})\s*ביטוח מבנה:", "groups":[(1, "building_insurance", to_float),]},
  {"idx":5, "re":fr"({NUM_RE})\s*ריבית בינים:", "groups":[(1, "mid_interest", to_float),]},
  {"idx":6, "re":fr"({NUM_RE})\s*הצמדת ריבית:", "groups":[(1, "interest_indexing", to_float),]},
  {"idx":7, "re":fr"({NUM_RE})\s*עמלות:", "groups":[(1, "commission", to_float),]},
  {"idx":8, "re":fr"({NUM_RE})", "groups":[(1, "legal_expense", to_float),]},
  {"idx":9, "re":fr"הוצאות משפט:", "groups":[]},
  {"idx":10, "re":fr"({NUM_RE})\s*ביטוח חיים:", "groups":[(1, "life_insurance", to_float),]},
  {"idx":11, "re":fr"({NUM_RE})\s*הוצאות אחרות:", "groups":[(1, "other_expense", to_float),]},
  {"idx":12, "re":fr"({NUM_RE})\s*אגרת רישום:", "groups":[(1, "registration_fee", to_float),]},
]

ZERO_FIELDS = ["building_insurance", "commission", "legal_expense", "life_insurance", "mid_interest", "other_expense", "registration_fee"]

SUMMED_FIELDS = ["building_insurance", "commission", "fund", "fund_indexing", "interest", "interest_indexing", "legal_expense", "life_insurance", "mid_interest", "other_expense", "registration_fee", "total_pay"]

def split_rows_to_chunks(rows):
  chunks = []
  for row in rows:
    if pd.isnull(row[2]):
      chunks.append([])
    chunks[-1].extend(cell for key,cell in row.items() if pd.notnull(cell))
  return chunks

def build_chunk_info(chunk, configuration):
  info = {}
  for cfg in configuration:
    text = chunk[cfg["idx"]]
    m = re.match(cfg["re"], text)
    for group_num, group_name, group_cast in cfg["groups"]:
        try:
            val = m.group(group_num)
            info[group_name] = group_cast(val)
        except Exception as exc:
            print(f"Got exception {type(exc)}, text='{text}', cfg={cfg}")
            raise
  verify_zero_fields(info)
  return info

def verify_zero_fields(info):
    for field in ZERO_FIELDS:
        T.assertEqual(info[field], 0.0, f"field={field}")

def verify_summed_fields(tracks):
    for field in SUMMED_FIELDS:
        total_val = tracks["total"][field]
        tracks_sum = sum(info[field] for info in tracks["by_id"].values())
        T.assertAlmostEqual(total_val, tracks_sum, msg=f"field={field}", delta=ALLOWED_SUM_DIFF_NIS)

def add_track(tracks, chunk):
  info = build_chunk_info(chunk, TRACK_RE_CONFIG)
  tracks["by_id"][info["track_id"]] = info

def add_track_total(tracks, chunk):
  info = build_chunk_info(chunk, TRACK_TOTAL_RE_CONFIG)
  tracks["total"] = info

def build_tracks(chunks):
  tracks = {"by_id": {}}
  for chunk in chunks[:-1]:
    add_track(tracks, chunk)
  num_tracks = len(tracks['by_id'])
  assert num_tracks==len(TRACK_INFO), f'num_tracks={num_tracks}, len(TRACK_INFO)={len(TRACK_INFO)}'
  add_track_total(tracks, chunks[-1])
  verify_summed_fields(tracks)
  return tracks

def parse_filename_as_monthly(fname):
    m = re.match(MONTHLY_REPORT_FNAME_RE, fname)
    if not m:
        return None
    datestr = m.group(1)
    try:
        dateobj = D.datetime.strptime(datestr, DATE_RE)
    except Exception as exc:
        raise ValueError(f"Error parsing date in *monthly* fname='{fname}'", exc)
    return {"dateobj":dateobj, "fname":fname}

def get_all_files_info():
    path, dirs, files = os.walk(REPORTS_FOLDER).__next__()
    file_info = {"monthly":[], "remainder":[]}
    for fname in files:
        monthly_info = parse_filename_as_monthly(fname)
        if monthly_info:
            file_info["monthly"].append(monthly_info)
            continue
        # TODO add here more report types if relevant
        file_info["remainder"].append(monthly_info)
    T.assertEqual(file_info["remainder"], [])
    return file_info

def load_chunks(folder, fname):
    path = os.path.join(folder, fname)
    print(path)
    tables = tabula.read_pdf(path, pandas_options={"header": None}, pages='all')
    T.assertEqual(len(tables), 1, msg=f"fname={fname}")
    rows = tables[0].to_dict("records")
    chunks = split_rows_to_chunks(rows)
    return chunks

def parse_monthly_file(folder, fname):
    chunks = load_chunks(folder, fname)
    tracks = build_tracks(chunks)
    return tracks

def parse_all_files(file_info):
    for monthly_info in file_info["monthly"]:
        monthly_info["data"] = parse_monthly_file(REPORTS_FOLDER, monthly_info["fname"])

def run():
    file_info = get_all_files_info()
    parse_all_files(file_info)
    print(pprint.pformat(file_info))

def start_time_count():
    start = D.datetime.now()
    print(f"{start} Starting")
    return start

def print_time_summary(start):
    end = D.datetime.now()
    seconds = (end - start).total_seconds()
    minutes = seconds/60
    print("%s Finished after %.2g seconds (%.2g minutes)" %\
            (end, seconds, minutes))

def main():
    start = start_time_count()
    try:
        run()
    finally:
        print_time_summary(start)

if __name__ == "__main__":
  main()
