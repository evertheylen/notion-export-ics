
import json
from datetime import datetime

from icalendar import Calendar, Event
from notion.client import NotionClient
from notion.collection import CalendarView
from notion.block import BasicBlock

# Hack some representation stuff into notion-py

BasicBlock.__repr__ = BasicBlock.__str__ = lambda self: self.title


# Separate file, since the token is rather sensitive :)
with open('settings.json') as f:
    settings = json.load(f)

client = NotionClient(token_v2=settings['token'], monitor=False)

start = datetime.now()

calendar = client.get_block(settings['calendar'])
for view in calendar.views:
    if isinstance(view, CalendarView):
        calendar_view = view
        break
else:
    raise Exception(f"Couldn't find a calendar view in the following list: {calendar.views}")

calendar_query = calendar_view.build_query()
calendar_entries = calendar_query.execute()

collection = calendar.collection

schema = collection.get_schema_properties()
print("SCHEMA", schema)
properties_by_name = {}
properties_by_slug = {}
properties_by_id = {}

for prop in schema:
    name = prop['name']
    if name in properties_by_name:
        print("WARNING: duplicate property with name {}".format(name))
    properties_by_name[name] = prop
    properties_by_slug[prop['slug']] = prop
    properties_by_id[prop['id']] = prop

print("handled props")

dateprop = properties_by_id[calendar_query.calendar_by]
assert dateprop['type'] == 'date', "Property '{}' is not a Date property".format(settings['property'])

print("handled dateprop")

cal = Calendar()
cal.add("summary", "Imported from Notion, via notion-export-ics.")
cal.add('version', '2.0')

print("made calendar")

entries = collection.get_rows()

print(f"GOT {len(entries)} ENTRIES")


for e in entries:
    date = e.get_property(dateprop['id'])
    if date is None:
        continue
    name = e.get_property('name')
    clean_props = {'NAME': name}
    
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
    title = settings['title_format'].format_map(clean_props)
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

end = datetime.now()

print("TOOK ", end - start)
