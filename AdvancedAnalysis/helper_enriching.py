import constants
import pandas as pd
import numpy as np
import ast
import os
import time
import hashlib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PyPDF2 import PdfReader
from io import BytesIO


CASE_ID_COL = 'case:concept:name'
TIMESTAMP_COL = 'time:timestamp'
ACTIVITY_COL = 'concept:name'

# downloaded PDFs are cached here so reruns don't hit the server again
PDF_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data-pdf-cache")
FAILED_PDF_URLS_FILE = os.path.join(PDF_CACHE_DIR, "failed_urls.txt")
# seconds to wait between live (non-cached) requests
PDF_REQUEST_DELAY = 1.0

# one shared session: reuses connections and retries transient errors (e.g. 503)
# with exponential backoff, honouring the server's Retry-After header
pdf_session = requests.Session()
pdf_session.headers["User-Agent"] = "academic-research-scraper (legislative process mining)"
pdf_session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    respect_retry_after_header=True,
    raise_on_status=False,
)))
pdf_session.mount("http://", pdf_session.adapters["https://"])



def add_case_attribute(df, id_value_obj, attribute_name):
    df[attribute_name] = df[CASE_ID_COL].map(id_value_obj)

def get_month_attribute(df):
    result_obj = {}
    for i in range(len(df)):
        case_id = df[CASE_ID_COL][i]
        month = df[TIMESTAMP_COL][i].month
        if case_id not in result_obj:
            result_obj[case_id] = month
    return result_obj

def get_weekday_attribute(df):
    result_obj = {}
    for i in range(len(df)):
        case_id = df[CASE_ID_COL][i]
        weekday = df[TIMESTAMP_COL][i].weekday()
        if case_id not in result_obj:
            result_obj[case_id] = weekday
    return result_obj

# just get the urheber of the first activity as a case attribute
def get_urheber_first_activity(df):
    result_obj = {}
    for i in range(len(df)):
        case_id = df[CASE_ID_COL][i]
        if case_id not in result_obj:
            urheber = df["Urheber"][i]
            result_obj[case_id] = urheber
    return result_obj

def get_urheber_count_first_activity(df):
    result_obj = {}
    for i in range(len(df)):
        case_id = df[CASE_ID_COL][i]
        urheber = df["Urheber"][i]
        if case_id not in result_obj:
            if (urheber == "nan"): # TODO: what does nan mean here??
                result_obj[case_id] = None
            else:
                result_obj[case_id] = urheber.count(',') + 1 if isinstance(urheber, str) else 0
    return result_obj


def get_case_times_helper(df):
    result_obj = {}
    for case_id in df[CASE_ID_COL].unique():
        case_df = df[df[CASE_ID_COL] == case_id]
        start_time = case_df[TIMESTAMP_COL].min()
        end_time = case_df[TIMESTAMP_COL].max()
        result_obj[case_id] = {'start_time': start_time, 'end_time': end_time}
    return result_obj

def get_is_election_year(df, bundesland):
    result_obj = {}
    for i in range(len(df)):
        case_id = df[CASE_ID_COL][i]
        year = df[TIMESTAMP_COL][i].year
        if case_id not in result_obj:
            if (year in constants.ELECTION_YEARS[bundesland.lower()]):
                result_obj[case_id] = 1
            else:
                result_obj[case_id] = 0
    return result_obj

def get_WIP_during_start(df):
    # Get start_time and end_time for each case
    case_times = get_case_times_helper(df)
    # Create a DataFrame from case_times
    case_df = pd.DataFrame.from_dict(case_times, orient="index").reset_index()
    case_df.columns = [CASE_ID_COL, "start_time", "end_time"]
    
    result_obj = {}
    for i in range(len(df)):
        case_id = df[CASE_ID_COL][i]
        start_time = df[TIMESTAMP_COL][i]
        if case_id not in result_obj:
            result_obj[case_id] = ((case_df["start_time"] <= start_time) & (case_df["end_time"] > start_time)).sum()
    return result_obj

def fetch_pdf(url):
    # returns the PDF bytes, or None if the download failed
    os.makedirs(PDF_CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(PDF_CACHE_DIR, hashlib.md5(url.encode()).hexdigest() + ".pdf")
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return f.read()

    time.sleep(PDF_REQUEST_DELAY)
    try:
        print("getting file...")
        response = pdf_session.get(url, timeout=60)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

    if response.status_code != 200:
        print(f"Error getting PDF: {response.status_code}")
        return None

    print("got file...")
    with open(cache_path, "wb") as f:
        f.write(response.content)
    return response.content

def get_pdf_information_helper(url):
    # returns (bytes, word_count); (nan, nan) if the PDF could not be fetched or parsed,
    # so failures are not confused with PDFs that genuinely have no extractable text
    # handle case where there is a list of documents
    # for example pdf and docx
    if (url.startswith("[") and url.endswith("]")):
        print(url)
        filenames = ast.literal_eval(url)
        for filename in filenames:
            if filename.endswith(".pdf"):
                url = filename
                break

    pdf_bytes = fetch_pdf(url)
    if pdf_bytes is None:
        return np.nan, np.nan

    try:
        # Load PDF into PyPDF2 PdfReader
        pdf_reader = PdfReader(BytesIO(pdf_bytes))

        # Extract text and calculate word count
        total_word_count = 0
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:  # Ensure the page has extractable text
                total_word_count += len(text.split())
        return len(pdf_bytes), total_word_count
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return np.nan, np.nan

def get_pdf_information(df):
    result_obj_bytes = {}
    result_obj_word_count = {}
    failed_urls = []
    for i in range(len(df)):
        print("i/len(df):", i, "/", len(df))
        case_id = df[CASE_ID_COL][i]
        url = df["LokURL"][i]
        if case_id not in result_obj_bytes:
            # Catch real NaN, None, the string "nan", and empty strings
            if pd.isna(url) or url == "nan" or url == "":
                bytes_val, word_count = (0, 0)
            else:
                bytes_val, word_count = get_pdf_information_helper(url)
                if pd.isna(bytes_val):
                    failed_urls.append(f"{case_id}\t{url}")

            print({"bytes": bytes_val, "total_word_count": word_count})
            result_obj_bytes[case_id] = bytes_val
            result_obj_word_count[case_id] = word_count

    # failures are written out so they can be inspected; rerunning retries only these,
    # since successful downloads are served from the cache
    os.makedirs(PDF_CACHE_DIR, exist_ok=True)
    with open(FAILED_PDF_URLS_FILE, "w") as f:
        f.write("\n".join(failed_urls))
    print(f"{len(failed_urls)} PDFs failed, see {FAILED_PDF_URLS_FILE}")
    return result_obj_bytes, result_obj_word_count

def add_pdf_case_attributes(df, id_value_obj_bytes, id_value_obj_word_count, attribute_bytes, attribute_word_count):
    df[attribute_bytes] = df[CASE_ID_COL].map(id_value_obj_bytes)
    df[attribute_word_count] = df[CASE_ID_COL].map(id_value_obj_word_count)
    

             

def get_is_passed_bill(df):
    result_obj = {}
    for i in range(len(df)):
        case_id = df[CASE_ID_COL][i]
        activityType = df[ACTIVITY_COL][i]
        if activityType in constants.POSSIBLE_PASSED_BILL_ACTIVITIES:
            result_obj[case_id] = 1
        elif case_id not in result_obj:
            result_obj[case_id] = 0
    return result_obj
    


def get_half_year_attribute(df, electionPeriodStartDates):
    result_obj = {}
    n_periods = len(electionPeriodStartDates)

    for i in range(len(df)):
        case_id = df[CASE_ID_COL].iloc[i]
        timestamp = pd.to_datetime(df[TIMESTAMP_COL].iloc[i], utc=True)

        if case_id in result_obj:
            continue

        # find which election period this case belongs to
        for p in range(n_periods):
            start = pd.to_datetime(electionPeriodStartDates[p], dayfirst=True, utc=True)
            end = (
                pd.to_datetime(electionPeriodStartDates[p + 1], dayfirst=True, utc=True)
                if p < n_periods - 1
                else pd.Timestamp.now(tz='UTC')
            )

            if start <= timestamp < end:
                months_since_start = (
                    (timestamp.year - start.year) * 12
                    + (timestamp.month - start.month)
                )
                result_obj[case_id] = months_since_start // 6
                break

    return result_obj

def get_government_party_count_attribute(df, electionPeriodStartDates, coalitionsSorted):
    result_obj = {}
    n_periods = len(electionPeriodStartDates)

    for i in range(len(df)):
        case_id = df[CASE_ID_COL].iloc[i]
        if case_id in result_obj:
            continue

        timestamp = pd.to_datetime(df[TIMESTAMP_COL].iloc[i], utc=True)

        for p in range(n_periods):
            start = pd.to_datetime(electionPeriodStartDates[p], utc=True)
            end = (
                pd.to_datetime(electionPeriodStartDates[p + 1], utc=True)
                if p < n_periods - 1
                else pd.Timestamp.now(tz='UTC')
            )

            if start <= timestamp < end:
                result_obj[case_id] = len(coalitionsSorted[p][1]["government"])
                break

    return result_obj


def get_opposition_party_count_attribute(df, electionPeriodStartDates, coalitionsSorted):
    result_obj = {}
    n_periods = len(electionPeriodStartDates)

    for i in range(len(df)):
        case_id = df[CASE_ID_COL].iloc[i]
        if case_id in result_obj:
            continue

        timestamp = pd.to_datetime(df[TIMESTAMP_COL].iloc[i], utc=True)

        for p in range(n_periods):
            start = pd.to_datetime(electionPeriodStartDates[p], utc=True)
            end = (
                pd.to_datetime(electionPeriodStartDates[p + 1], utc=True)
                if p < n_periods - 1
                else pd.Timestamp.now(tz='UTC')
            )

            if start <= timestamp < end:
                result_obj[case_id] = len(coalitionsSorted[p][1]["opposition"])
                break

    return result_obj


def get_government_seat_percentage_attribute(df, electionPeriodStartDates, coalitionsSorted):
    result_obj = {}
    n_periods = len(electionPeriodStartDates)

    for i in range(len(df)):
        case_id = df[CASE_ID_COL].iloc[i]
        if case_id in result_obj:
            continue

        timestamp = pd.to_datetime(df[TIMESTAMP_COL].iloc[i], utc=True)

        for p in range(n_periods):
            start = pd.to_datetime(electionPeriodStartDates[p], utc=True)
            end = (
                pd.to_datetime(electionPeriodStartDates[p + 1], utc=True)
                if p < n_periods - 1
                else pd.Timestamp.now(tz='UTC')
            )

            if start <= timestamp < end:
                gov = coalitionsSorted[p][1]["government_seats"]
                opp = coalitionsSorted[p][1]["opposition_seats"]
                result_obj[case_id] = gov / (gov + opp)
                break

    return result_obj


def get_opposition_seat_percentage_attribute(df, electionPeriodStartDates, coalitionsSorted):
    result_obj = {}
    n_periods = len(electionPeriodStartDates)

    for i in range(len(df)):
        case_id = df[CASE_ID_COL].iloc[i]
        if case_id in result_obj:
            continue

        timestamp = pd.to_datetime(df[TIMESTAMP_COL].iloc[i], utc=True)

        for p in range(n_periods):
            start = pd.to_datetime(electionPeriodStartDates[p], utc=True)
            end = (
                pd.to_datetime(electionPeriodStartDates[p + 1], utc=True)
                if p < n_periods - 1
                else pd.Timestamp.now(tz='UTC')
            )

            if start <= timestamp < end:
                gov = coalitionsSorted[p][1]["government_seats"]
                opp = coalitionsSorted[p][1]["opposition_seats"]
                result_obj[case_id] = opp / (gov + opp)
                break

    return result_obj