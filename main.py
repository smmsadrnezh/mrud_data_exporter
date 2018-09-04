import csv
import re
import sys

import progressbar
import requests

import settings

current_city, current_transaction_type = dict(), dict()


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def remove_substrings(string, substrings):
    for substring in substrings:
        string = re.sub(substring, '', string)
    return string


def clean_transaction_data(transaction_constants, transaction_data):
    transaction_data = transaction_constants + transaction_data.split('</td><td')[:-1]
    return [remove_substrings(field, [".*?>", ","]) for field in transaction_data]


def extract_transactions(response):
    pattern = re.compile('dx-al">.*?<td class="dxgvHEC')
    transaction_constants = [current_transaction_type['label']] + [current_city['label']]
    transactions_data = [clean_transaction_data(transaction_constants, transaction_data) for transaction_data in
                         pattern.findall(response)]
    return transactions_data


def write_csv(data_rows):
    with open('out.csv', 'a', newline='') as output_csv_file:
        writer_csv_file_valid = csv.writer(output_csv_file, delimiter=',', quotechar='"')
        for data_row in data_rows:
            writer_csv_file_valid.writerow(data_row)


def write_to_database(transactions_data):
    pass


def extract_and_write_data():
    eprint("Exporting data for: {city} - {transaction_type}".format(city=current_city['name'],
                                                                    transaction_type=current_transaction_type['name']))

    # TODO: This section needs refactoring
    request_data = settings.GetTransactionsRequest(current_city['code'], 0, current_transaction_type)
    response = requests.post(**request_data.__dict__).text
    page_number_pattern = re.compile('pageCount\\\\\':(\d*)')
    max_page_number = int(page_number_pattern.findall(response)[0])
    transactions_data = extract_transactions(response)
    if not transactions_data:
        eprint("\nError: no transaction data")
    write_csv(transactions_data)
    write_to_database(transactions_data)
    bar = progressbar.ProgressBar()
    for page_number in bar(range(1, max_page_number)):
        request_data = settings.GetTransactionsRequest(current_city['code'], page_number, current_transaction_type)
        response = requests.post(**request_data.__dict__).text
        transactions_data = extract_transactions(response)
        if not transactions_data:
            eprint("\nError: no transaction data")
        write_csv(transactions_data)
        write_to_database(transactions_data)


def main():
    global current_city, current_transaction_type
    write_csv(
        [["نوع قرارداد", "شهر", "منطقه", "محله", "تاریخ عقد قرارداد", "مساحت", "سن (سال)", "قیمت کل (تومان)",
          "قیمت هر متر (تومان)", "قیمت رهن (تومان)"]])
    for transaction_type in settings.transaction_types:
        if transaction_type['do_extract']:
            current_transaction_type = transaction_type
            for city in settings.cities:
                if city['do_extract']:
                    current_city = city
                    request_data = settings.SetCityRequest(current_city['code'])
                    requests.post(**request_data.__dict__)
                    request_data = settings.SetTransactionsTypeRequest(current_city['code'], current_transaction_type)
                    requests.post(**request_data.__dict__)
                    extract_and_write_data()


if __name__ == '__main__':
    main()
