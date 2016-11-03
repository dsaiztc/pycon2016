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


def get_schedule_json():
    schedule_html = get_schedule_html()
    soup = BeautifulSoup(schedule_html, 'html.parser')

    day_elements = soup.select('p.schedule__day-switcher-item')
    days = [ {'name': day.string, 'id': day['data-date'] } for day in day_elements]

    for day in days:
        day['events'] = []
        day_schedule = soup.select('#{id}'.format(id=day['id']))[0]
        day_event_elements = day_schedule.select('div.session')
        for day_event_element in day_event_elements:

            event = {
                'time_start': day_event_element.select('span.session__time')[0].string.replace('\n', '').strip(),
                'id': day_event_element.select('div.session__content')[0]['data-link'],
                'title': day_event_element.select('h5.session__title')[0].string
            }

            event['datetime_start'] = datetime.datetime.strptime('2016' + day['name'] + event['time_start'], '%Y%d %B%I:%M %p')
            event['datetime_start_str'] = str(event['datetime_start'])

            event_description_element = soup.select('#{id}'.format(id=event['id']))[0]
            event_time_finish = event_description_element.select('span.session__time')[1].string.replace('\n', '').strip()
            event['time_finish'] = event_time_finish
            event['datetime_finish'] = datetime.datetime.strptime('2016' + day['name'] + event['time_finish'], '%Y%d %B%I:%M %p')
            event['datetime_finish_str'] = str(event['datetime_finish'])

            event['location'] = event_description_element.select('span.session__location')[0].string if len(event_description_element.select('span.session__location')) > 0 else ''
            event['description'] = event_description_element.select('div.uv-card__description')[0].string if len(event_description_element.select('div.uv-card__description')) > 0 else ''
            event['description'] = event['description'].replace('\n', '').strip() if event['description'] else ''
            if not event['description']:
                event['description'] = ''.join(event_description_element.select('div.uv-card__description')[0].stripped_strings) if len(event_description_element.select('div.uv-card__description')) > 0 else ''

            if event['title'] == 'Introduction to Pandas library':
                print(event_description_element.select('div.uv-card__description'))
                print(event_description_element.select('div.uv-card__description')[0].string)
                strings = event_description_element.select('div.uv-card__description')[0].stripped_strings
                for string in strings:
                    print(string)
                    print('\n')
                print(''.join(event_description_element.select('div.uv-card__description')[0].stripped_strings))

            speakers_list = []
            event_speakers_elements = event_description_element.select('div.uv-shortcard--speaker')
            for event_speakers_element in event_speakers_elements:
                speaker_details = []
                speaker_details.append(event_speakers_element.select('div.uv-shortcard__title')[0].string)
                for subtitle in event_speakers_element.select('div.uv-shortcard__subtitle'):
                    speaker_details.append(subtitle.string)
                speakers_list.append(' - '.join(speaker_details))
            event['speakers'] = '; '.join(speakers_list)

            day['events'].append(event)

    return days


def create_ics(schedule_json):
    c = Calendar()
    for day in schedule_json:
        for event in day['events']:
            e = Event(
                name=event['title'],
                begin=event['datetime_start'],
                end=event['datetime_finish'],
                description=u'Description:\n{description}\n\nSpeakers:\n{speakers}'.format(**event).encode('ascii', 'ignore'),
                location=event['location']
            )
            c.events.append(e)
    with open('pycon2016.ics', 'w') as writer:
        writer.writelines(c)


def main():
    schedule_json = get_schedule_json()
    create_ics(schedule_json)


if __name__ == '__main__':
    main()
