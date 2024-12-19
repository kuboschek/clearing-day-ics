import client
from ics import Calendar, Event
from collections import defaultdict
import os

def generate(env):
    url = client.TEST_URL if env == 'test' else client.PROD_URL
    data = client.get_calendar_v1(url)
    
    calendar = Calendar()
    grouped_entries = defaultdict(list)
    
    for entry in data.entries:
        for service in entry.services:
            grouped_entries[entry.calendarDay].append((entry, service))
    
    if not os.path.exists('out'):
        os.makedirs('out')
    
    for calendar_day, entries in grouped_entries.items():
        all_day_event = Event()
        all_day_event.name = "Normal Operation"
        all_day_event.begin = calendar_day
        all_day_event.end = calendar_day
        all_day_event.make_all_day()
        
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
        
        all_day_event.name = "Scheduled Downtime" if has_downtime else "Normal Operation"
        all_day_event.description = description
        calendar.events.add(all_day_event)
        
        for (start, end), services in downtime_events.items():
            downtime_event = Event()
            downtime_event.name = "Downtime: " + ", ".join([s.serviceIdentification for s in services])
            downtime_event.begin = start
            downtime_event.end = end
            downtime_event.description = "\n".join([s.serviceDescription for s in services])
            calendar.events.add(downtime_event)
    
    with open(f'out/clearingday_{env}.ics', 'w', newline='') as f:
        f.write(calendar.serialize())

if __name__ == '__main__':
    generate('test')
    generate('prod')