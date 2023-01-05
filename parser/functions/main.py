import functions_framework
from google.cloud import storage

def on_pdf_uploaded(event, context):
    """Background Cloud Function to be triggered by Cloud Storage.
       This generic function logs relevant data when a file is changed,
       and works for all Cloud Storage CRUD operations.
    Args:
        event (dict):  The dictionary with data specific to this type of event.
                       The `data` field contains a description of the event in
                       the Cloud Storage `object` format described here:
                       https://cloud.google.com/storage/docs/json_api/v1/objects#resource
        context (google.cloud.functions.Context): Metadata of triggering event.
    Returns:
        None; the output is written to Cloud Logging
    """

    print('Event ID: {}'.format(context.event_id))
    print('Event type: {}'.format(context.event_type))
    print('Bucket: {}'.format(event['bucket']))
    print('File: {}'.format(event['name']))
    print('Metageneration: {}'.format(event['metageneration']))
    print('Created: {}'.format(event['timeCreated']))
    print('Updated: {}'.format(event['updated']))

    bucket_name = event['bucket']
    source_blob_name = event['name']

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    destination_file_name = '/tmp/doc_to_process.pdf'

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    user_data = source_blob_name.split("_")
    user_id = user_data[0]
    timestamp = user_data[1]

    print('User id: {}'.format(user_id))
    print('Timestamp: {}'.format(timestamp))
    
    import_data = process_pdf(destination_file_name)

    save_import(user_id, timestamp, import_data)
    

# code to write to DB

from pymongo import MongoClient
import os

def save_import(user_id, timestamp, import_data):
    client = MongoClient(f"mongodb+srv://admin:{os.environ['MONGODB_PWD']}@cluster0.xclm49x.mongodb.net/?retryWrites=true&w=majority")
    db = client.test
    
    imports_collection = db["imports"]
    imports_collection.insert_one({
        "user_id": user_id,
        "timestamp": timestamp,
        "data": import_data,
    })


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