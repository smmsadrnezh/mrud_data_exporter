import csv
import re
import sys

import progressbar
import requests

import settings

current_city, current_transaction_type = dict(), dict()


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_request_data(city_code, page_number):
    current_request = settings.request_template
    current_request['params']['strTownship'] = current_request['params']['strTownship'].format(city_code=city_code)
    current_request['headers']['Referer'] = current_request['headers']['Referer'].format(city_code=city_code)
    current_request['data'] = current_request['data'].format(page_number=page_number,
                                                             **current_transaction_type['data'])
    return current_request


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


def extract_and_write_data():
    eprint("Exporting data for: {city} - {transaction_type}".format(city=current_city['name'],
                                                                    transaction_type=current_transaction_type['name']))
    bar = progressbar.ProgressBar()
    for page_number in bar(range(1, current_city['max_page_number'])):
        request_data = get_request_data(current_city['code'], page_number)
        transactions_data = extract_transactions(requests.post(**request_data).text)
        write_csv(transactions_data)


def main():
    global current_city, current_transaction_type
    write_csv(
        [["نوع قرارداد", "شهر", "منطقه", "محله", "تاریخ عقد قرارداد", "مساحت", "سن (سال)", "قیمت کل تومان",
          "قیمت هر متر تومان"]])
    for transaction_type in settings.transaction_types:
        if transaction_type['do_extract']:
            current_transaction_type = transaction_type
            for city in settings.cities:
                if city['do_extract']:
                    current_city = city
                    extract_and_write_data()


if __name__ == '__main__':
    main()
