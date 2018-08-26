import csv
import re
import sys

import requests
from progressbar import progressbar

import settings

current_city = dict()


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_request_data(city_code, page_number):
    settings.request_template['params']['strTownship'].format(city_code=city_code)
    settings.request_template['headers']['Referer'].format(city_code=city_code)
    settings.request_template['data'].format(page_number=page_number)
    return settings.request_template


def remove_substrings(string, substrings):
    for substring in substrings:
        string = re.sub(substring, '', string)
    return string


def clean_transaction_data(transaction_data):
    transaction_data = [current_city['label']] + transaction_data.split('</td><td')[:-1]
    return [remove_substrings(field, [".*?>", ","]) for field in transaction_data]


def clean_response(text):
    pattern = re.compile('dx-al">.*?<td class="dxgvHEC')
    transactions_data = [clean_transaction_data(transaction_data) for transaction_data in pattern.findall(text)]
    return transactions_data


def write_csv(data_rows):
    with open('out.csv', 'a', newline='') as output_csv_file:
        writer_csv_file_valid = csv.writer(output_csv_file, delimiter=',', quotechar='"')
        for data_row in data_rows:
            writer_csv_file_valid.writerow(data_row)


def extract_and_write_data():
    eprint("Exporting data for: " + current_city['label'])
    bar = progressbar.ProgressBar()
    for page_number in bar(range(1, current_city['max_page_number'])):
        request_data = get_request_data(current_city['code'], page_number)
        transactions_data = clean_response(requests.post(**request_data).text)
        write_csv(transactions_data)


def main():
    global current_city
    write_csv(
        [["شهر", "منطقه", "محله", "تاریخ عقد قرارداد", "مساحت", "سن (سال)", "قیمت کل تومان", "قیمت هر متر تومان"]])
    for _, city in settings.cities.items():
        if city['do_extract']:
            current_city = city
            extract_and_write_data()


if __name__ == '__main__':
    main()
