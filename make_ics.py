
import json

from icalendar import Calendar, Event
from notion.client import NotionClient
from notion.markdown import notion_to_markdown


# Settings ======================================

# Separate file, since the token is rather sensitive :)
with open('settings.json') as f:
    settings = json.load(f)

def make_title(name, props):
    return "{} [{}]".format(name, props['Status'])

# ===============================================


client = NotionClient(token_v2=settings['token'])

block = client.get_block(settings['block'])
collection = block.collection

schema = collection.get_schema_properties()
properties_by_name = {}
properties_by_slug = {}

for prop in schema:
    name = prop['name']
    if name in properties_by_name:
        print("WARNING: duplicate property with name {}".format(name))
    properties_by_name[name] = prop
    properties_by_slug[prop['slug']] = prop

dateprop = properties_by_name[settings['property']]
assert dateprop['type'] == 'date', "Property '{}' is not a Date property".format(settings['property'])

cal = Calendar()
cal.add("summary", "Imported from Notion, via notion-export-ics.")
cal.add('version', '2.0')

entries = collection.get_rows()

for e in entries:
    date = e.get_property(dateprop['id'])
    if date is None:
        continue
    name = e.get_property('name')
    clean_props = {}
    
    # Put in ICS file
    event = Event()
    desc = ''
    event.add('dtstart', date.start)
    if date.end is not None:
        event.add('dtend', date.end)
    desc += e.get_browseable_url() + '\n\n'
    desc += 'Properties:\n'
    for k, v in e.get_all_properties().items():
        if k != dateprop['slug'] and k != 'name':
            name = properties_by_slug[k]['name']
            desc += "  - {}: {}\n".format(name, v)
            clean_props[name] = v
    title = make_title(name, clean_props)
    event.add('summary', title)
    event.add('description', desc)
    cal.add_component(event)
    
    # Print
    print("{}: {} -> {}".format(title, date.start, date.end))
    print(desc)
    print('--------------')



with open('calendar.ics', 'wb') as f:
    f.write(cal.to_ical())
    f.close()
