import functions_framework
from google.cloud import storage

def parse_bank_statement(request):
    """Function to parse bank statement and return the parsed results.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    request_json = request.get_json()

    print('Request: {}'.format(request_json))
    
    bucket_name = request_json['bucket']
    source_blob_name = request_json['blob']

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    destination_file_name = '/tmp/doc_to_process.pdf'
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    
    return process_pdf(destination_file_name)

# code to parse pdf and return data

import os
import tabula
import locale
from datetime import date, datetime
from typing import List, NamedTuple
from pandas import DataFrame

def process_pdf(pdf_path):
    infos = []
    
    def read_pdf(pdf_path):
        res: list[DataFrame] = tabula.read_pdf(pdf_path ,pages='all', stream=True)
        if res and len(res) and not res[0].empty and res[0].columns.values[0] == 'Date':
            return get_debit_infos(res)
        else:
            return get_credit_infos(res)

    if os.path.isfile(pdf_path):
        infos = read_pdf(pdf_path)
    else: 
        files = [f for f in os.listdir(pdf_path)]
        files = filter(lambda f: f.endswith(('.pdf','.PDF')), files)
        for f in files:
            infos.extend(read_pdf(os.path.join(pdf_path, f)))

    return infos

class Transaction(NamedTuple):
    received: date
    details: str
    amount: float
    transaction_type: str

class TransactionWithRewards(NamedTuple):
    received: date
    details: str
    amount: float
    transaction_type: str
    rewards: float

def get_credit_infos(res: list[DataFrame]) -> List[Transaction]:
    return list(yield_credit_infos(res))

def get_debit_infos(res: list[DataFrame]) -> List[Transaction]:
    return list(yield_debit_infos(res))

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# HDFC Dinner 10X rewards
DINERS_SMARTBUY_PARTNERS = [
  'SMARTBUYBANGALORE',
  'FLIPKART PAYMENTSBANGALORE', 
  'WWW GYFTR COMGURGAON',
  'SMARTBUY VOUCHERSNEW DELHI',
  'IRCTC SMART BUYBANGALORE',
  'AMAZON SELLER SERVICES MUMBAI'
]

_DATE_FORMAT = "%d/%m/%Y"
_DATE_FORMAT_ALT = "%d/%m/%Y %H:%M:%S"

# Convert Amount to Number
def try_sanitize_amount(amnts):
    xxx = amnts.split()
    try:
        return locale.atof(xxx[0])
    except ValueError:
        return None

# Parse Date
def try_parse_date(ds: str):
    try:
        return datetime.strptime(ds, _DATE_FORMAT)
    except:
        try:
            return datetime.strptime(ds, _DATE_FORMAT_ALT)
        except:
            return None
    return None


# parses credit card statement
def yield_credit_infos(res: list[DataFrame]):
    def try_transaction(line):
        transaction_date = str(line[0]).replace("null ", "")
        amount = line[-1]
        details = line[1]

        transaction_date = try_parse_date(transaction_date)
        if transaction_date is None:
            # If start of line is not Date skip,
            # as it will not be Transaction
            return

        if 'Cr' in amount:
            transaction_type = 'credit'
        else:
            transaction_type = 'debit'

        amount = try_sanitize_amount(amount)

        if amount is None:
            return

        yield Transaction(
            received=transaction_date.date(),
            details=details,
            amount=amount,
            transaction_type=transaction_type,
        )

    for page in res:
      for line in page.values:
          for t in try_transaction(line):
              yield t

# parses debit card statement
def yield_debit_infos(res: list[DataFrame]):
    def try_transaction(line):
        transaction_date = str(line[0]).replace("null ", "")
        amount = line[-1]
        details = line[1]

        transaction_date = try_parse_date(transaction_date)
        if transaction_date is None:
            # If start of line is not Date skip,
            # as it will not be Transaction
            return

        if 'Cr' in amount:
            transaction_type = 'credit'
        else:
            transaction_type = 'debit'

        amount = try_sanitize_amount(amount)

        if amount is None:
            return

        yield Transaction(
            received=transaction_date.date(),
            details=details,
            amount=amount,
            transaction_type=transaction_type,
        )

    for page in res:
      for line in page.values:
          for t in try_transaction(line):
              yield t