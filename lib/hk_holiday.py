import json, requests, codecs
from datetime import date, datetime

today_day = date.today().strftime("%d")
today_month_abbr = date.today().strftime("%b")
today_month = date.today().strftime("%m")
today_year = date.today().strftime("%Y")

HOLIDAY_QUERY_RESULT = ""

def get_holiday_list():
    holiday_url = 'https://www.1823.gov.hk/common/ical/tc.json'
    holiday_data = json.loads(codecs.decode(requests.get(holiday_url).text.encode(),'utf-8-sig'))
    
    return holiday_data

def isHoliday(date):
    global HOLIDAY_QUERY_RESULT
    HOLIDAY_QUERY_RESULT = ""
    holiday = get_holiday_list()["vcalendar"][0]["vevent"]
    for i in range(len(holiday)-1,-1,-1):
        #h_length = (datetime.strptime(holiday[i]["dtend"][0],"%Y%m%d")-datetime.strptime(holiday[i]["dtstart"][0],"%Y%m%d")).days
        #diff = (datetime.strptime(holiday[i]["dtend"][0],"%Y%m%d")-datetime.strptime(date,"%Y%m%d")).days

        if (date == holiday[i]["dtstart"][0]):
            HOLIDAY_QUERY_RESULT = holiday[i]["summary"]
            return True
    return False

def get_holiday_name(date=""):
    global HOLIDAY_QUERY_RESULT
    if (date==""):
        return HOLIDAY_QUERY_RESULT
    elif(isHoliday(date)):
        return HOLIDAY_QUERY_RESULT
    return ""
    