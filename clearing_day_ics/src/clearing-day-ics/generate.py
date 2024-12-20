import client
from ics import Calendar, Event
from collections import defaultdict
from typing import Literal
import os
import sys

def generate(env: Literal["Test", "Prod"], output_folder: str = 'out'):
    url = client.TEST_URL if env == 'Test' else client.PROD_URL
    data = client.get_calendar_v1(url)

    print(f"Output directory: {os.path.abspath(output_folder)}")

    calendar_file = os.path.join(os.getcwd(), output_folder, f'six_clearingday_{env.lower()}.ics')
    if os.path.exists(calendar_file):
        with open(calendar_file, 'r') as f:
            calendar = Calendar(f.read())
    else:
        calendar = Calendar()
    
    grouped_entries = defaultdict(list)
    
    for entry in data.entries:
        for service in entry.services:
            grouped_entries[entry.calendarDay].append((entry, service))
    
    if not os.path.exists('out'):
        os.makedirs('out')
    
    for calendar_day, entries in grouped_entries.items():
        existing_event = next((e for e in calendar.events if e.begin.date() == calendar_day and e.all_day), None)
        
        if existing_event:
            description = existing_event.description
            has_downtime = "Scheduled Downtime" in existing_event.name
        else:
            existing_event = Event()
            existing_event.name = "Normal Operation"
            existing_event.begin = calendar_day
            existing_event.end = calendar_day
            existing_event.make_all_day()
            description = ""
            has_downtime = False
        
        downtime_events = defaultdict(list)
        
        for entry, service in entries:
            description += f"Service: {service.serviceDescription}\n"
            if service.scheduledClearingDayChange:
                if service.scheduledClearingDayChange.scheduledClearingStop1:
                    description += f"Clearing Stop 1: {service.scheduledClearingDayChange.scheduledClearingStop1}\n"

                if service.scheduledClearingDayChange.scheduledClearingStop2:
                    description += f"Clearing Stop 2: {service.scheduledClearingDayChange.scheduledClearingStop2}\n"

                if service.scheduledClearingDayChange.scheduledClearingStop3:
                    description += f"Clearing Stop 3: {service.scheduledClearingDayChange.scheduledClearingStop3}\n"

                if service.scheduledClearingDayChange.scheduledCutOff1:
                    description += f"Cut Off 1: {service.scheduledClearingDayChange.scheduledCutOff1}\n"

                if service.scheduledClearingDayChange.scheduledCutOff2:
                    description += f"Cut Off 2: {service.scheduledClearingDayChange.scheduledCutOff2}\n"
                    
                description += "\n"
            if service.scheduledDowntimes:
                has_downtime = True
                for downtime in service.scheduledDowntimes:
                    downtime_events[(downtime.startDateTime, downtime.endDateTime)].append(service)
        
        if existing_event.description != description or existing_event.name != ("Scheduled Downtime" if has_downtime else "Normal Operation"):
            existing_event.name = f"Scheduled Downtime ({env})" if has_downtime else f"Normal Operation ({env})"
            existing_event.description = description
        calendar.events.add(existing_event)
        
        for (start, end), services in downtime_events.items():
            existing_downtime_event = next((e for e in calendar.events if e.begin == start and e.end == end), None)
            new_description = "\n".join([s.serviceDescription for s in services])
            if existing_downtime_event:
                if existing_downtime_event.description != new_description:
                    existing_downtime_event.description = new_description
            else:
                downtime_event = Event()
                downtime_event.name = f"Downtime ({env}): " + ", ".join([s.serviceIdentification for s in services])
                downtime_event.begin = start
                downtime_event.end = end
                downtime_event.description = new_description
                calendar.events.add(downtime_event)
    
    with open(calendar_file, 'w', newline='') as f:
        f.write(calendar.serialize())

if __name__ == '__main__':
    generate('Test', output_folder=sys.argv[1] if len(sys.argv) > 1 else 'out')
    generate('Prod', output_folder=sys.argv[1] if len(sys.argv) > 1 else 'out')