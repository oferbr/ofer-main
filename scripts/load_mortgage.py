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
import time
import copy
import pprint
import random
import datetime as D
import operator as O
import itertools as I
import collections as C
import pandas as pd
import unittest
import tabula
import dictdiffer as DD
import dateutil

pd.set_option('min_rows', 35)
pd.set_option('max_rows', 35)

def to_float(s):
    return round(float(s.replace(",","")),8)
def to_percent(s):
    return round(to_float(s)/100.0,8)
def to_date(s):
    return D.datetime.strptime(s, "%d/%m/%Y").date()

# A TestCase instance to call assertions on, for mroe elegant messages
T = unittest.TestCase()

TOP_FOLDER = r"/Users/oferbr/Documents/mortgage"
DUMPS_FOLDER = os.path.join(TOP_FOLDER, "dumps")
REPORTS_FOLDER = os.path.join(TOP_FOLDER, "reports")
#REPORTS_FOLDER = os.path.join(TOP_FOLDER, "test_reports")

#MONTHLY_REPORT_FNAME_RE = r"(\d+)_monthly\.pdf"
#OVERVIEW_REPORT_FNAME_RE = r"(\d+)_overview\.pdf"
DATE_FILENAME_PATTERN = "%Y%m%d"
ALLOWED_SUM_DIFF_NIS = 1.0
DUMP_CSV_FNAME_PATTERN = "mortgage_%Y%m%d_%H%M%S.csv"
DUMP_XLSX_FNAME_PATTERN = "mortgage_%Y%m%d_%H%M%S.xlsx"

def choose_current_month(dateobj):
    return beginning_of_month(dateobj)

def choose_last_payment_month(dateobj):
    FORBIDDEN_DAYS = [15, 16]
    if dateobj.day in FORBIDDEN_DAYS:
        raise ValueError(f"Got file from {dateobj}, which is a forbidden day (too close to monthly payment day)")
    elif dateobj.day > 15:
        return beginning_of_month(dateobj)
    else: #dateobj.day < 15
        prev_month = get_date_in_previous_month(dateobj)
        return beginning_of_month(prev_month)

FILE_TYPES = [
    {"type_name": "monthly", "re": r"(\d+)_monthly\.pdf", "reported_month_func": choose_current_month},
    {"type_name": "overview", "re": r"(\d+)_overview\.pdf", "reported_month_func": choose_last_payment_month},
]

TRACK_INFO = [
  {"id": "6200349019546", "name": "t546 - Small Katz"},
  {"id": "6200349019645", "name": "t645 - Big Katz"},
  {"id": "6210349019248", "name": "t248 - Prime"},
  {"id": "6248349019427", "name": "t427 - Kalatz"},
  {"id": "6279349019323", "name": "t323 - Matz"},
]
TRACK_DICT = {ti["id"]:ti for ti in TRACK_INFO}
NUM_RE = r"\d+[\d\,]*\.?\d*"
DATE_RE = r"\d\d/\d\d/\d\d\d\d"
TRACK_ID_RE = r"[\d\/]+"
MONTHLY_TRACK_RE_CONFIG = [
  {"idx":0, "re":fr"15י *ום חיוב:({TRACK_ID_RE})מספר הלוואה:", "groups":[(1, "track_id", str),]},
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
MONTHLY_TRACK_TOTAL_RE_CONFIG = [
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
OVERVIEW1_TITLES = {
  0: 'יתרה לסילוק',
  1: 'עמלת פירעון מוקדם',
  2: 'נלווים',
  3: 'ריבית נדחית\rוהצמדת ריבית\rנדחית',
  4: 'ריבית\rוהצמדת ריבית',
  5: 'פיגור / עודף',
  6: 'הצמדת קרן',
  7: 'קרן',
  8: 'מספר הלוואה\rומספר חשבון\rהלוואה משכן'
}
OVERVIEW1_TRACK_RE_CONFIG = [
  {"idx":0, "re":fr"({NUM_RE})", "groups":[(1, "to_pay+early_fee", to_float),]},
  {"idx":1, "re":fr"({NUM_RE})", "groups":[(1, "early_pay_fee", to_float),]},
  {"idx":2, "re":fr"({NUM_RE})", "groups":[(1, "additionals", to_float),]},
  {"idx":3, "re":fr"({NUM_RE})", "groups":[(1, "postponed", to_float),]},
  #{"idx":4, "re":fr"({NUM_RE})", "groups":[(1, "interest+indexing", to_float),]},
  {"idx":5, "re":fr"({NUM_RE})", "groups":[(1, "late_fee", to_float),]},
  {"idx":6, "re":fr"({NUM_RE})", "groups":[(1, "remaining_fund_indexing", to_float),]},
  {"idx":7, "re":fr"({NUM_RE})", "groups":[(1, "remaining_fund", to_float),]},
  {"idx":8, "re":fr"({TRACK_ID_RE})\r477122-628", "groups":[(1, "track_id", str),]},
]
OVERVIEW1_TRACK_TOTAL_RE_CONFIG = [
  {"idx":0, "re":fr"({NUM_RE})", "groups":[(1, "to_pay+early_fee", to_float),]},
  {"idx":1, "re":fr"({NUM_RE})", "groups":[(1, "early_pay_fee", to_float),]},
  {"idx":2, "re":fr"({NUM_RE})", "groups":[(1, "additionals", to_float),]},
  {"idx":3, "re":fr"({NUM_RE})", "groups":[(1, "postponed", to_float),]},
  #{"idx":4, "re":fr"({NUM_RE})", "groups":[(1, "interest+indexing", to_float),]},
  {"idx":5, "re":fr"({NUM_RE})", "groups":[(1, "late_fee", to_float),]},
  {"idx":6, "re":fr"({NUM_RE})", "groups":[(1, "remaining_fund_indexing", to_float),]},
  {"idx":7, "re":fr"({NUM_RE})", "groups":[(1, "remaining_fund", to_float),]},
  {"idx":8, "re":fr'סה"כ:', "groups":[]},
]
OVERVIEW2_TITLES = {
  0: 'מספר הלוואה ומספר מרכיב',
  1: 'סכום הלוואה מקורי',
  2: 'מועד ביצוע ההלוואה',
  3: 'מועד התשלום הראשון',
  4: 'מועד צפוי לתשלום\rאחרון / תאריך סילוק',
  5: 'סוג הלוואה',
  6: 'שיטת פירעון ההלוואה',
  7: 'סוג ריבית',
  8: 'בסיס לקביעת הריבית ותוספת /\rהפחתה )ריבית סיכון(',
  9: 'שיעור ריבית נומינלית\rליום מכתבנו זה',
  10: 'שיעור ריבית מתואמת\rליום מכתבנו זה',
  11: 'תדירות שינוי הריבית\rבחודשים',
  12: 'מועד שינוי הריבית\rהקרוב',
  13: 'בסיס ההצמדה',
  14: 'מדד / שער בסיס\rשל ההלוואה',
  15: 'מדד / שער\rאחרון ידוע',
}
OVERVIEW2_TRACK_RE_CONFIG = [
  {"idx":0, "re":fr"({TRACK_ID_RE})\r201", "groups":[(1, "track_id", str),]},
  {"idx":1, "re":fr"({NUM_RE})", "groups":[(1, "original_fund", to_float),]},
  {"idx":3, "re":fr"({DATE_RE})", "groups":[(1, "first_payment", to_date),]},
  {"idx":4, "re":fr"({DATE_RE})", "groups":[(1, "end_date", to_date),]},
  {"idx":5, "re":fr"בנק", "groups":[]},
  {"idx":6, "re":fr"שפיצר", "groups":[]},
  {"idx":9, "re":fr"({NUM_RE})\s*\%", "groups":[(1, "nominal_interest_rate", to_percent),]},
  {"idx":10,"re":fr"({NUM_RE})\s*\%", "groups":[(1, "adjusted_interest_rate", to_percent),]},
  {"idx":14, "re":fr"({NUM_RE})", "groups":[(1, "base_index", to_float),]},
  {"idx":15, "re":fr"({NUM_RE})", "groups":[(1, "curr_index", to_float),]},
]

MONTHLY_ZERO_FIELDS = ["building_insurance", "commission", "legal_expense", "life_insurance", "mid_interest", "other_expense", "registration_fee"]
MONTHLY_SUMMED_FIELDS = ["extras", "fund", "fund_indexing", "interest", "interest_indexing", "total_pay",   "_fund+interest", "_fund+indexing", "_interest+indexing", "_all_indexing"]
MONTHLY_FIELDS_FOR_DATAFRAME = ["extras", "fund", "fund_indexing", "interest", "interest_indexing", "total_pay",   "_fund+interest", "_fund+indexing", "_interest+indexing", "_all_indexing", "_fund_p", "_interest_p", "_fund_indexing_p", "_interest_indexing_p"]
MONTHLY_UNSTABLE_FIELDS = []
OVERVIEW1_ZERO_FIELDS = ["additionals", "postponed", "late_fee"]
OVERVIEW1_SUMMED_FIELDS = ["extras", "remaining_fund", "remaining_fund_indexing", "early_pay_fee", "to_pay+early_fee",   "_to_pay"] #, "interest+indexing"
OVERVIEW_FIELDS_FOR_DATAFRAME = ["extras", "remaining_fund", "remaining_fund_indexing", "early_pay_fee", "original_fund", "first_payment", "end_date", "nominal_interest_rate", "adjusted_interest_rate", "base_index", "curr_index",    "_to_pay", "_remaining_fund_indexing_p", "_index_increase", "_passed_months", "_remaining_months"]
OVERVIEW_UNSTABLE_FIELDS = ["early_pay_fee", "to_pay+early_fee", "_to_pay"] #, "interest+indexing"]

def split_rows_to_chunks(rows):
  chunks = []
  for row in rows:
    if pd.isnull(row[2]):
      chunks.append([])
    chunks[-1].extend(cell for key,cell in row.items() if pd.notnull(cell))
  return chunks

def months_diff(early_date, late_date, additional):
    early_beginning = beginning_of_month(early_date)
    late_beginning = beginning_of_month(late_date)
    diff = dateutil.relativedelta.relativedelta(late_beginning, early_beginning)
    months = diff.years*12 + diff.months
    final_months = months + additional
    return final_months

def enrich_monthly_fields(info, metadata):
    info["_fund+interest"] = info["fund"] + info["interest"]
    info["_fund+indexing"] = info["fund"] + info["fund_indexing"]
    info["_interest+indexing"] = info["interest"] + info["interest_indexing"]
    info["_all_indexing"] = info["fund_indexing"] + info["interest_indexing"]
    info["_fund_p"] = round(info["fund"] / info["_fund+interest"],8)
    info["_interest_p"] = round(info["interest"] / info["_fund+interest"],8)
    info["_fund_indexing_p"] = round(info["fund_indexing"] / info["fund"],8)
    info["_interest_indexing_p"] = round(info["interest_indexing"] / info["interest"],8)

def enrich_overview1_fields(info, metadata):
    info["_to_pay"] = round(info["to_pay+early_fee"] - info["early_pay_fee"],8)
    info["_remaining_fund_indexing_p"] = round(info["remaining_fund_indexing"] / info["remaining_fund"],8)

def enrich_overview2_fields(info, metadata):
    info["_index_increase"] = round(info["curr_index"] / info["base_index"] - 1.0,8) if info["base_index"] else None
    info["_passed_months"] = months_diff(info["first_payment"], metadata["reported_month"], 1)
    info["_remaining_months"] = months_diff(metadata["reported_month"], info["end_date"], 0)

def build_chunk_info(chunk, metadata, re_configuration, zero_fields, enrich_func):
  info = {}
  for cfg in re_configuration:
    text = chunk[cfg["idx"]]
    m = re.match(cfg["re"], text)
    for group_num, group_name, group_cast in cfg["groups"]:
        try:
            val = m.group(group_num)
            info[group_name] = group_cast(val)
        except Exception as exc:
            print(f"Got exception {type(exc)}, text='{text}', text:{list(text)}, cfg={cfg}")
            raise
  if zero_fields:
      handle_zero_fields(info, zero_fields)
  if enrich_func:
      enrich_func(info, metadata)
  return info

def handle_zero_fields(info, zero_fields):
    for field in zero_fields:
        T.assertEqual(info[field], 0.0, f"field={field}")
        del info[field]
    info["extras"] = 0.0

def verify_summed_fields(tracks, summed_fields):
    for field in summed_fields:
        total_val = tracks["tracks_total"][field]
        tracks_sum = sum(info[field] for info in tracks["by_id"].values())
        T.assertAlmostEqual(total_val, tracks_sum, msg=f"field={field}", delta=ALLOWED_SUM_DIFF_NIS)

def set_or_update_dict(dct, key, dict_val):
    if key in dct:
        dct[key].update(dict_val)
    else:
        dct[key] = dict_val

def add_track(tracks, chunk, metadata, re_configuration, zero_fields, enrich_func):
  info = build_chunk_info(chunk, metadata, re_configuration, zero_fields, enrich_func)
  info["track_id"] = info["track_id"].replace("/","")
  info["track_name"] = TRACK_DICT[info["track_id"]]["name"]
  #print(f"info={info}, TRACK_DICT={TRACK_DICT}")
  set_or_update_dict(tracks["by_id"], info["track_name"], info)

def add_track_total(tracks, chunk, metadata, re_configuration, zero_fields, enrich_func):
  info = build_chunk_info(chunk, metadata, re_configuration, zero_fields, enrich_func)
  tracks["tracks_total"] = info
  set_or_update_dict(tracks, "tracks_total", info)

def build_tracks(tracks, track_chunks, totals_chunk, metadata, track_config, track_total_config, zero_fields, summed_fields, enrich_func):
  for chunk in track_chunks:
    add_track(tracks, chunk, metadata, track_config, zero_fields, enrich_func)
  num_tracks = len(tracks['by_id'])
  assert num_tracks==len(TRACK_INFO), f'num_tracks={num_tracks}, len(TRACK_INFO)={len(TRACK_INFO)}'
  if totals_chunk:
      add_track_total(tracks, totals_chunk, metadata, track_total_config, zero_fields, enrich_func)
      verify_summed_fields(tracks, summed_fields)

def parse_filename_as_type(fname, file_type_info):
    m = re.match(file_type_info["re"], fname)
    if not m:
        return None
    datestr = m.group(1)
    try:
        dateobj = D.datetime.strptime(datestr, DATE_FILENAME_PATTERN).date()
    except Exception as exc:
        raise ValueError(f"Error parsing date in *{file_type_info['type_name']}* fname='{fname}'", exc)
    reported_month = file_type_info["reported_month_func"](dateobj)
    return {"fname":fname, "dateobj":dateobj, "reported_month":reported_month}

def get_all_files_info():
    path, dirs, files = os.walk(REPORTS_FOLDER).__next__()
    visible_files = [fname for fname in files if not fname.startswith(".")]
    remaining = list(visible_files)
    file_info = C.defaultdict(list)
    for fname in visible_files:
        for file_type_info in FILE_TYPES:
            metadata = parse_filename_as_type(fname, file_type_info)
            if metadata:
                info = {"metadata": metadata}
                file_info[file_type_info["type_name"]].append(info)
                remaining.remove(fname)
                break
    T.assertEqual(file_info["remainder"], [])
    return file_info

def read_pdf_tables(file_path):
    # https://stackoverflow.com/a/58350890/1333305
    java_options = [
        "-Dorg.slf4j.simpleLogger.defaultLogLevel=off",
        "-Dorg.apache.commons.logging.Log=org.apache.commons.logging.impl.NoOpLog"
    ]
    tables = tabula.read_pdf(file_path, pandas_options={"header": None},
                             java_options=java_options,
                             pages='all',
                             )
    return tables

def load_monthly_chunks(folder, fname):
    path = os.path.join(folder, fname)
    print(path)
    tables = read_pdf_tables(path)
    T.assertEqual(len(tables), 1, msg=f"fname={fname}")
    rows = tables[0].to_dict("records")
    chunks = split_rows_to_chunks(rows)
    return chunks

def screw_up_tracks(tracks):
    some_key = tracks["tracks_total"].keys().__iter__().__next__()
    tracks["tracks_total"][some_key] += random.randint(10,100)

def parse_monthly_file(folder, info):
    fname = info["metadata"]["fname"]
    chunks = load_monthly_chunks(folder, fname)
    tracks = {"by_id": {}}
    build_tracks(tracks, chunks[:-1], chunks[-1], info["metadata"],
        MONTHLY_TRACK_RE_CONFIG, MONTHLY_TRACK_TOTAL_RE_CONFIG,
        MONTHLY_ZERO_FIELDS, MONTHLY_SUMMED_FIELDS, enrich_monthly_fields)
    #screw_up_tracks(tracks)
    return tracks

def verify_titles(row, titles):
    T.assertEqual(row, titles)

def build_overview1(tables, tracks, metadata):
    rows = tables[0].to_dict("records")
    T.assertEqual(len(rows), len(TRACK_INFO)+2)
    verify_titles(rows[0], OVERVIEW1_TITLES)
    build_tracks(tracks, rows[1:-1], rows[-1], metadata,
        OVERVIEW1_TRACK_RE_CONFIG, OVERVIEW1_TRACK_TOTAL_RE_CONFIG,
        OVERVIEW1_ZERO_FIELDS, OVERVIEW1_SUMMED_FIELDS, enrich_overview1_fields)
    #screw_up_tracks(tracks)

def parse_overview2_tables(tables):
    rows1 = tables[1].T.to_dict("records")
    rows2 = tables[2].T.to_dict("records")

    # Hacky hack #1 (required)
    v1 = rows2[0].pop(1)
    T.assertEqual(v1, '201')
    rows2[0][0] += f"\r{v1}"

    # Hacky hack #2 (required)
    rows2_vals = [v for v in rows2[0].values() if pd.notnull(v)]
    rows2b = [{i:v for i,v in enumerate(rows2_vals)}]

    rows = rows2b + rows1
    return rows

def build_overview2(tables, tracks, metadata):
    rows = parse_overview2_tables(tables)
    T.assertEqual(len(rows), len(TRACK_INFO)+1)
    verify_titles(rows[-1], OVERVIEW2_TITLES)
    build_tracks(tracks, rows[:-1], None, metadata,
        OVERVIEW2_TRACK_RE_CONFIG, None,
        None, None, enrich_overview2_fields)
    #screw_up_tracks(tracks)

def parse_overview_file(folder, info):
    fname = info["metadata"]["fname"]
    path = os.path.join(folder, fname)
    print(path)
    tables = read_pdf_tables(path)
    T.assertGreaterEqual(len(tables), 3, msg=f"fname={fname}")
    tracks = {"by_id": {}}
    build_overview1(tables, tracks, info["metadata"])
    build_overview2(tables, tracks, info["metadata"])
    return tracks

def parse_all_files(file_info):
    for monthly_info in file_info["monthly"]:
        monthly_info["data"] = parse_monthly_file(REPORTS_FOLDER, monthly_info)
    for overview_info in file_info["overview"]:
        overview_info["data"] = parse_overview_file(REPORTS_FOLDER, overview_info)

############################ 2020-05-22 Add cross-file calculations
def cross_file_calc(moo, foo, bar):
    # This function should be somewhere around or before build_dataframes_from_records,
    # but perhaps on all "groups" and not on each one individually
    # maybe also get the by_month_year data as input
    # In this function, we calculate predictions for *this month*, based on
    # *previous month* and other inputs.
    # On what data from last month - real or predicted?
    # Let's say we *calc on real data if available, otherwise on predicted*
    ###inputs: p, SPITZER, ...
    for month in months:
        prediction_for_this_month["year_month"] = p["year_month"] - D.timedelta(days=1)
        prediction_for_this_month["spitzer_fund_p"] = SPIZER_FUNDER_P[prediction_for_this_month["year_month"]]
        prediction_for_this_month["spitzer_interest_p"] = 1 - prediction_for_this_month["spitzer_fund_p"]
############################

def all_equal_iter(items):
    first = items[0] #.__next__()
    return all(x==first for x in items)

def gen_diff(info1, data1, info2, data2):
    return (
        info1["metadata"]["fname"],
        info2["metadata"]["fname"],
        list(DD.diff(data1, data2)),
    )

def remove_bad_keys_nested_in_iterable(itr, bad_keys):
    for x in itr:
        if isinstance(x, (str, int, float, type(None), D.datetime, D.date)):
            pass
        elif isinstance(x, (list, tuple, set)):
            remove_bad_keys_nested_in_iterable(x, bad_keys)
        elif isinstance(x, dict):
            remove_bad_keys_from_dict(x, bad_keys)
        else:
            raise TypeError(f"Not supporting value {x} (type={type(x)}) when removing bad keys")

def remove_bad_keys_from_dict(dct, bad_keys):
    """
    Remove bad_keys from keys in the given dictionary, and all dictionaries nested in it (also in lists, tuples and sets).

    doctest:
    >>> remove_bad_keys_from_dict({
    ...   1:"hi",
    ...   2:[{"do":"hi", "zoo":[67, "hi"]}, "hi", ({"hi":"moo", "foo":"goo"})],
    ...   "hi":{"hello":"there", "to":{"every":"one"}}
    ...  }, {"hi"})
    {1: 'hi', 2: [{'do': 'hi', 'zoo': [67, 'hi']}, 'hi', {'foo': 'goo'}]}
    """
    for k,v in list(dct.items()):
        if k in bad_keys:
            del dct[k]
        elif isinstance(v, (str, int, float, type(None), D.datetime, D.date)):
            pass
        elif isinstance(v, (list, tuple, set)):
            remove_bad_keys_nested_in_iterable(v, bad_keys)
        elif isinstance(v, dict):
            remove_bad_keys_from_dict(v, bad_keys)
        else:
            raise TypeError(f"Not supporting value {v} (type={type(v)}) when removing bad keys")
    return dct #Not necessary, but nice for testing

def get_comparable_datas(infos, unstable_fields):
    comparable_datas = []
    for info in infos:
        data = info["data"]
        if unstable_fields:
            data = copy.deepcopy(data)
            remove_bad_keys_from_dict(data, unstable_fields)
        comparable_datas.append(data)
    return comparable_datas

def verify_all_infos_equivalent(year_month, infos, unstable_fields):
    #unique_pformats = set(pprint.pformat(info) for info in infos)
    #if len(unique_pformats)>1:
    #    raise ValueError(f"Got {len(infos)} infos for month={month}, left with {len(unique_pformats)} after deduping:\n{unique_pformats}")
    comparable_datas = get_comparable_datas(infos, unstable_fields)
    if not all_equal_iter(comparable_datas):
        all_diffs = [gen_diff(infos[0], comparable_datas[0], info, data)
                     for info,data in zip(infos[1:],comparable_datas[1:])]
        all_actual_diffs = [diff for diff in all_diffs if diff[2]!=[]]
        raise ValueError(f"Got {len(infos)} infos for year_month={year_month}, but have {len(all_actual_diffs)} actual diffs:\n{all_actual_diffs}")

def pick_month_info(year_month, infos, unstable_fields):
    verify_all_infos_equivalent(year_month, infos, unstable_fields)
    return infos[-1]

def build_records_for_fields(rows__month_cols, rows__month_rows, group, fields_for_df, year_month, track_name, fields):
    for field, value in sorted(fields.items()):
        if field in fields_for_df:
            if field.startswith("_"):
                source = "calc"
                field = field[1:]
            else:
                source = "orig"
            rows__month_cols[(track_name, group, source, field)][year_month] = value
            rows__month_rows[(year_month, track_name, group, source, field)]["val"] = value

def build_records_by_year_month(by_year_month, group, fields_for_df, rows__month_cols, rows__month_rows):
    for year_month, info in by_year_month.items():
        for track_name, fields in info["data"]["by_id"].items():
            build_records_for_fields(
                rows__month_cols, rows__month_rows, group, fields_for_df, year_month, track_name, fields)
        build_records_for_fields(
             rows__month_cols, rows__month_rows, group, fields_for_df, year_month, "Tracks Total", info["data"]["tracks_total"])

def build_dataframes_from_records(rows__month_cols, rows__month_rows):
    df__month_cols = pd.DataFrame.from_dict(rows__month_cols).T
    df__month_cols.index.names = ["Track", "Group", "Source", "Field"]
    df__month_rows = pd.DataFrame.from_dict(rows__month_rows).T
    df__month_rows.index.names = ["Month","Track", "Group", "Source", "Field"]
    dump_monthly_df(df__month_rows)
    return df__month_cols, df__month_rows

# def build_monthly_dataframes(by_year_month):
#     rows__month_cols = C.defaultdict(dict);
#     rows__month_rows = C.defaultdict(dict);
#     for year_month, info in by_year_month.items():
#         for track_name, fields in info["data"]["by_id"].items():
#             build_records_for_fields(
#                 rows__month_cols, rows__month_rows, year_month, track_name, fields)
#         build_records_for_fields(
#              rows__month_cols, rows__month_rows, year_month, "Tracks Total", info["data"]["tracks_total"])
#     df__month_cols = pd.DataFrame.from_dict(rows__month_cols).T
#     df__month_cols.index.names = ["Track", "Group", "Source", "Field"]
#     df__month_rows = pd.DataFrame.from_dict(rows__month_rows).T
#     df__month_rows.index.names = ["Month","Track", "Group", "Source", "Field"]
#     return df__month_cols, df__month_rows

def dump_monthly_df(monthly_df):
    fname = os.path.join(DUMPS_FOLDER, time.strftime(DUMP_CSV_FNAME_PATTERN))
    monthly_df.to_csv(fname)

    #fname = os.path.join(DUMPS_FOLDER, time.strftime(DUMP_XLSX_FNAME_PATTERN))
    #monthly_df.to_excel(fname, freeze_panes=(1,3))

    print(f"Dumped file: {fname}")

def build_info_by_year_month(file_info, file_type, unstable_fields):
    date_key = lambda info: info["metadata"]["dateobj"] #O.itemgetter("dateobj")
    sorted_dates = sorted(file_info[file_type], key=date_key)
    by_year_month = C.OrderedDict()
    year_month_key = lambda info: info["metadata"]["reported_month"].strftime("%Y-%m")
    for year_month, infos in I.groupby(sorted_dates, key=year_month_key):
        by_year_month[year_month] = pick_month_info(year_month, list(infos), unstable_fields)
    #print(f"Got *{file_type}* info for months: {list(by_year_month.keys())}:\n{pprint.pformat(by_year_month)}")
    print(f"Got *{file_type}* info for months: {list(by_year_month.keys())}")
    return by_year_month

def process_group(rows__month_cols, rows__month_rows, file_info, file_type, fields_for_df, unstable_fields):
    by_year_month = build_info_by_year_month(file_info, file_type, unstable_fields)
    build_records_by_year_month(by_year_month, file_type, fields_for_df, rows__month_cols, rows__month_rows)

# def process_monthly(file_info):
#     date_key = O.itemgetter("dateobj")
#     sorted_dates = sorted(file_info["monthly"], key=date_key)
#     by_year_month = C.OrderedDict()
#     year_month_key = lambda x: x["dateobj"].strftime("%Y-%m")
#     for year_month, infos in I.groupby(sorted_dates, key=year_month_key):
#         by_year_month[year_month] = pick_month_info(year_month, list(infos))
#     #print(f"Got monthlies for months: {list(by_year_month.keys())}:\n{pprint.pformat(by_year_month)}")
#     print(f"Got monthlies for months: {list(by_year_month.keys())}")
#     monthly_df__month_cols, monthly_df__month_rows = build_monthly_dataframes(by_year_month)
#     dump_monthly_df(monthly_df__month_rows)
#     return monthly_df__month_cols

def get_date_in_previous_month(dateobj):
    return dateobj - D.timedelta(days=dateobj.day+1)

def beginning_of_month(dateobj):
    return dateobj - D.timedelta(days=dateobj.day-1)

def process_all_files(file_info):
    rows__month_cols = C.defaultdict(dict);
    rows__month_rows = C.defaultdict(dict);
    process_group(rows__month_cols, rows__month_rows, file_info, "monthly",
                  MONTHLY_FIELDS_FOR_DATAFRAME, MONTHLY_UNSTABLE_FIELDS)
    process_group(rows__month_cols, rows__month_rows, file_info, "overview",
                  OVERVIEW_FIELDS_FOR_DATAFRAME, OVERVIEW_UNSTABLE_FIELDS)
    df__month_cols, df__month_rows = build_dataframes_from_records(rows__month_cols, rows__month_rows)
    return df__month_cols

def run():
    file_info = get_all_files_info()
    parse_all_files(file_info)
    print(pprint.pformat(file_info, compact=True))
    processed = process_all_files(file_info)
    print(pprint.pformat(processed))
    return processed #file_info

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
