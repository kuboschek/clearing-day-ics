import requests
import pydantic

from model import ClearingDayCalendarV1

TEST_URL = "https://api-etu.six-group.com/api/epcd/clearingday/v1/calendar"
PROD_URL = "https://api.six-group.com/api/epcd/clearingday/v1/calendar"

def get_calendar_v1(url) -> ClearingDayCalendarV1: 
    response = requests.get(url)
    return ClearingDayCalendarV1.parse_obj(response.json())

if __name__ == "__main__":
    data = get_calendar_v1(TEST_URL)
    print(data)