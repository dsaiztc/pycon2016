# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import datetime
import pprint
import json
from ics import Calendar, Event


this_path = os.path.dirname(os.path.realpath(__file__))


def save_file(file_str, file_name):
    file_path = os.path.join(this_path, file_name)
    with open(file_path, 'w') as writer:
        writer.write(file_str.encode('utf-8', errors='replace'))


def read_file(file_name):
    result = None
    file_path = os.path.join(this_path, file_name)
    if os.path.exists(file_path):
        with open(file_path) as reader:
            result = reader.read()
    return result


def get_schedule_html():
    file_name = 'schedule.html'
    file_str = read_file(file_name)
    if not file_str:
        response = requests.get('http://d6unce.attendify.io/schedule.html')
        file_str = response.text
        save_file(file_str, file_name)
    return file_str


def main():
    schedule_html = get_schedule_html()


if __name__ == '__main__':
    main()
