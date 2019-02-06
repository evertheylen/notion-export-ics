
import traceback
import json
import sys
import os
import base64
from datetime import datetime, timedelta

from icalendar import Calendar, Event
from notion.client import NotionClient
from notion_ics import get_ical

from flask import Flask, request, make_response

with open('settings.json') as f:
    settings = json.load(f)
token = settings['token']
client = NotionClient(settings['token'], monitor=False)

with open('create_url.html') as f:
    index = f.read()

app = Flask(__name__)

@app.route('/')
def create_url():
    return index


@app.route('/ics')
def make_ics():
    try:
        try:
            calendar_url = base64.b64decode(request.args['url']).decode()
            title_format = base64.b64decode(request.args['format']).decode()
        except Exception as e:
            raise Exception('Something went wrong with the given parameters') from e
        cal = get_ical(client, calendar_url, title_format)
        text = cal.to_ical()
    except Exception as e:
        traceback.print_exc()
        # put it in calendar
        cal = Calendar()
        cal.add("summary", "Imported from Notion, via notion-export-ics, but failed.")
        cal.add('version', '2.0')
        for i in range(7):
            event = Event()
            event.add('dtstart', datetime.now().date() + timedelta(days=i))
            event.add('summary', repr(e))
            cal.add_component(event)
        text = cal.to_ical()
    
    res = make_response(text)
    res.headers.set('Content-Disposition', 'attachment;filename=calendar.ics')
    res.headers.set('Content-Type', 'text/calendar;charset=utf-8')
    return res


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

