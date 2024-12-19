from typing import Optional
from pydantic import BaseModel
from datetime import datetime, date

class ClearingDayCalendarV1(BaseModel):
    metaData: "MetaData"
    entries: list["CalendarEntry"]

class MetaData(BaseModel):
    createdStamp: datetime

class CalendarEntry(BaseModel):
    calendarDay: date
    dayOfWeek: str
    services: list["Service"]

class Service(BaseModel):
    serviceIdentification: str
    serviceDescription: str
    clearingDay: date
    scheduledDowntimes: Optional[list["ScheduledDowntime"]] = None
    scheduledClearingDayChange: Optional["ScheduledClearingDayChange"] = None

class ScheduledDowntime(BaseModel):
    startDateTime: datetime
    endDateTime: datetime

class ScheduledClearingDayChange(BaseModel):
    nextClearingDay: date
    scheduledClearingStop1: Optional[datetime] = None
    scheduledClearingStop2: Optional[datetime] = None
    scheduledClearingStop3: Optional[datetime] = None
    scheduledCutOff1: Optional[datetime] = None
    scheduledCutOff2: Optional[datetime] = None

    