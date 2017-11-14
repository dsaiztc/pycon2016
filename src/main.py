from datetime import datetime

import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event

import requests_cache

requests_cache.install_cache()


def get_event_list_from_url(main_url):
    event_list = []

    s = requests.Session()
    s.headers.update({
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    })
    main_url = 'https://www.bigdataspain.org/2017/schedule'
    r = s.get(main_url)
    main_html = r.text
    soup = BeautifulSoup(main_html, 'html.parser')
    for container in soup.select('.slots-container'):
        container_url = container.find('a')
        if container_url:
            talk_url = container_url['href']
            event = get_event_from_url(s, talk_url)
            event_list.append(event)
    return event_list


def get_event_from_url(s, talk_url):

    r = s.get(talk_url)
    talk_html = r.text

    soup = BeautifulSoup(talk_html, 'html.parser')

    speaker_url = soup.select('.single-talk-speaker-link')[0].find('a')['href']
    speaker = get_speaker_from_url(s, speaker_url)

    event_container = soup.select('.single-talk-maininfo-container')[0]

    kind_selector = event_container.select('.single-talk-type')
    kind = ''
    if kind_selector:
        kind = kind_selector[0].contents[0].split('|')[1].strip()
    title = event_container.find('h2').string

    date_location_info = event_container.select('.single-talk-whereinfo')[0].string.split('|')
    location = date_location_info[2].strip()
    date_str = date_location_info[0].strip()
    time_str = date_location_info[1].strip()
    time_str_split = time_str.split(' - ')
    time_start_str = time_str_split[0]
    time_start_str = time_start_str if len(time_start_str) == 5 else '0' + time_start_str
    start_date_str = '2017-11-' + date_str[-4:-2].strip() + time_start_str
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d%H:%M')
    time_end_str = time_str_split[1]
    time_end_str = time_end_str if len(time_end_str) == 5 else '0' + time_end_str
    end_date_str = '2017-11-' + date_str[-4:-2].strip() + time_end_str
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d%H:%M')

    single_field_data_list = event_container.select('.single-field-data')
    summary = ''
    keywords = []
    if single_field_data_list:
        summary = single_field_data_list[0].string
        for i in range(1, len(single_field_data_list)):
            keywords.append(single_field_data_list[i].string[2:])

    description_p = event_container.select('.single-talk-description')[0].find('p')
    description = description_p.string if description_p else ''

    event = {
        'kind': kind,
        'title': title,
        'start_date': start_date,
        'end_date': end_date,
        'location': location,
        'speaker': speaker,
        'summary': summary,
        'keywords': keywords,
        'description': description
    }
    return event


def get_speaker_from_url(s, speaker_url):

    r = s.get(speaker_url)
    speaker_html = r.text

    soup = BeautifulSoup(speaker_html, 'html.parser')

    info_list = soup.select('.speaker-maininfo')
    if not info_list:
        return {
            'name': '',
            'position': '',
            'company': '',
            'description': '',
            'linkedin': '',
            'twitter': ''
        }
    info = info_list[0]

    name = info.find('h4').string

    position_contents = info.select('.speaker-position-info')[0].contents
    position = position_contents[0]
    company = position_contents[2].string

    description_p = info.select('.speaker-single-description')[0].find('p')
    description = description_p.string if description_p else ''

    twitter_el = info.select('.speaker-social-item.twitter')
    twitter = twitter_el[0].find('a')['href'] if twitter_el else ''
    linkedin_el = info.select('.speaker-social-item.linkedin')
    linkedin = linkedin_el[0].find('a')['href'] if linkedin_el else ''

    speaker = {
        'name': name,
        'position': position,
        'company': company,
        'description': description,
        'linkedin': linkedin,
        'twitter': twitter
    }
    return speaker


def create_calendar_from_event_list(event_list, ics_filename):
    c = Calendar()
    for event in event_list:
        speaker_str = """\
            Name: {name}
            Position: {position} @ {company}
            Description: {description}
            LinkedIn: {linkedin}
            Twitter: {twitter}
        """.replace('            ', '').format(**event['speaker'])
        event['speaker_str'] = speaker_str
        event_description = """\
            Title:
            {title}

            Summary:
            {summary}

            Description:
            {description}

            Speaker:
            {speaker_str}
        """.replace('            ', '').format(**event)
        e = Event(
            name='{} [{}]'.format(event['title'], event['kind']),
            begin=event['start_date'],
            end=event['end_date'],
            description=event_description,
            location=event['location']
        )
        c.events.append(e)
    with open(ics_filename, 'w') as w:
        w.writelines(c)


def main():
    event_list = get_event_list_from_url('https://www.bigdataspain.org/2017/schedule')
    create_calendar_from_event_list(event_list, 'bigdataspain.ics')


if __name__ == '__main__':
    main()
