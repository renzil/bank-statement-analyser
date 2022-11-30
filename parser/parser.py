#!/usr/bin/env python3
import argparse
import csv
import locale
import os
from datetime import date, datetime
from typing import List, NamedTuple
from pandas import DataFrame

import tabula

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

def get_credit_infos(res: list[DataFrame]) -> List[Transaction]:
    return list(yield_credit_infos(res))

def get_debit_infos(res: list[DataFrame]) -> List[Transaction]:
    return list(yield_debit_infos(res))

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--statement-path', type=str,
                        help='path to statements pdf file or directory')

    return parser.parse_args()

def main(pdf_path):
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

    with open('output.csv', 'w') as f:
        writer = csv.writer(f , lineterminator='\n')
        writer.writerow(('Date', 'Transaction', 'Amount', 'Type'))
        for tup in infos:
            writer.writerow(tup)

if __name__ == '__main__':
    arguments = parse_arguments()
    
    statement_path = arguments.statement_path
    statement_path = "oct-2022.pdf"
    if not statement_path:
        statement_path = input("Enter statement path: ")

    main(statement_path)
    