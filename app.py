from GoogleAPIHandler import GoogleAPIHandler
import datetime
import json

apiHandler = GoogleAPIHandler()

sheets_service = apiHandler.get_sheets_service()
cal_service = apiHandler.get_cal_service()

def get_schedule():
    # The ID and range of a sample spreadsheet.
    SPREADSHEET_ID = "10fVLecrwYSGyQhfIBNPqXgtIw2WiKPcTbhw7Fkj-vwk"
    SHEET_NAME = "FIG Schedule"
    CELL_RANGE = "A1:D58"
    RANGE_NAME = f"{SHEET_NAME}!{CELL_RANGE}"
    sheet = sheets_service.spreadsheets()
    sheets_result = (
        sheet.values()
        .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
        .execute()
    )
    sheet_values = sheets_result.get("values", [])
    return sheet_values

def schedule_event(summary, location, description, activity, start_date, end_date):
    timeZone = "Singapore"
    time_map = {"sunday": {"start":"10:45", "end": "12:00"}, "yucha": {"start":"14:00", "end": "17:00"}, "camp":{"start":"09:00", "end": "17:00"}}
    time = time_map[activity]
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': f'{start_date}T{time["start"]}:00+08:00',
            'timeZone': timeZone,
        },
        'end': {
            'dateTime': f'{end_date}T{time["end"]}:00+08:00',
            'timeZone': timeZone,
        }
    }
    created_event = cal_service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (created_event.get('htmlLink')))
    return created_event

def delete_event(event_id):
    cal_service.events().delete(calendarId='primary', eventId=event_id).execute()
    print("Event deleted: %s" % (event_id))

def create_events_from_schedule():
    created_events = []
    now = datetime.datetime.now()
    for event in get_schedule()[5:]:
        event_date = (event[1] if event[1].count("/") == 0 else event[1].split("-")[0].strip().replace("/", "-")) + "-2024"
        event_date = datetime.datetime.strptime(event_date, "%d-%b-%Y") if event[1].count("/") == 0 else datetime.datetime.strptime(event_date, "%d-%m-%Y")
        if event_date > now:
            yucha_lessons = event[0]
            summary = event[2]
            description = event[3] if len(event) == 4 else ""
            event_date_str = event_date.strftime("%Y-%m-%d")
            try:
                if yucha_lessons.startswith("L"):
                    event_date_minus_one = datetime.datetime(event_date.year, event_date.month, event_date.day-1).strftime("%Y-%m-%d")
                    created_event = schedule_event(summary="Yucha",  
                                location="GCMC", 
                                description=yucha_lessons, 
                                activity="yucha", 
                                start_date=event_date_minus_one, 
                                end_date=event_date_minus_one)
                    created_events.append(created_event)
                if summary == "FIG Camp":
                    event_start = event[1].split("-")[0].strip().replace("/", "-") + "-2024"
                    event_start = "-".join(event_start.split("-")[::-1])
                    event_end = "0" + event[1].split("-")[1].strip().replace("/", "-") + "-2024"
                    event_end = "-".join(event_end.split("-")[::-1])
                    created_event = schedule_event(summary=summary,
                                location="GCMC",
                                activity="camp",
                                description=description,
                                start_date=event_start,
                                end_date=event_end)
                    created_events.append(created_event)
                else:
                    created_event = schedule_event(summary=summary,
                                location="GCMC",
                                description=description,
                                activity="sunday",
                                start_date=event_date_str,
                                end_date=event_date_str)
                    created_events.append(created_event)
            except Exception as e:
                print(e)
                continue
    json.dump(created_events, open("created_events.txt", "w"))

def delete_events_from_schedule():
    now = datetime.datetime.now()
    all_events = json.load(open("created_events.txt", 'r'))
    to_be_deleted = list(filter(lambda x: datetime.datetime.strptime(x["start"]["dateTime"].split("T")[0], "%Y-%m-%d") > now, all_events))
    ids = list(map(lambda x: x["id"], to_be_deleted))
    for id in ids:
        try:
            delete_event(id)
        except Exception:
            continue

# delete_events_from_schedule()
create_events_from_schedule()
