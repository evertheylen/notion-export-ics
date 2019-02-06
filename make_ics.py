
import json
from notion.client import Client
from notion_ics import get_ical

with open('settings.json') as f:
    settings = json.load(f)

client = NotionClient(settings['token'], monitor=False)
cal = get_ical(client, settings['calendar_url'], settings['title_format'])

with open('calendar.ics', 'wb') as f:
    f.write(cal.to_ical())
    f.close()
