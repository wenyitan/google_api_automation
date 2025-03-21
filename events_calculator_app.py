import pandas as pd
from app import cal_service
from datetime import datetime

time_format = format("%H:%M:%S")

def get_all_events():
    page_token = None
    result = []
    hours = 0
    while True:
        events = cal_service.events().list(calendarId='primary', pageToken=page_token).execute()
        for event in events['items']:
            if event is not None:
                if "summary" not in event.keys():
                    pass
                else:
                    try:
                        summary = event['summary']
                        date = event['start']['date'] if "date" in event['start'].keys() else event['start']['dateTime'].split("T")[0]
                        start_time = "" if "date" in event['start'].keys() else event['start']['dateTime'].split("T")[1]
                        end_time = "" if "date" in event['end'].keys() else event['end']['dateTime'].split("T")[1]
                        start_time = start_time.replace("+08:00", "")
                        end_time = end_time.replace("+08:00", "")
                        try:
                            duration = datetime.strptime(end_time, time_format) - datetime.strptime(start_time, time_format)
                            duration = duration.total_seconds()/3600
                            hours += duration
                        except:
                            duration = 0
                        result.append({
                            "summary": summary, 
                            # "start": start, 
                            # "end": end,
                            "date": date,
                            "start_time": start_time,
                            "end_time": end_time,
                            "duration": duration,
                            "organizer": event['organizer']['email']
                            }
                        )
                    except KeyError:
                        print(event)
                    
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    print(hours)
    return result

df1 = pd.DataFrame(get_all_events())
print(df1)

year_2023_str = "2023-01-01"
year_2023 = datetime.strptime(year_2023_str, format("%Y-%m-%d"))
now = datetime.now()
after_2023 = [i for i in get_all_events() if now > datetime.strptime(i['date'], format("%Y-%m-%d")) >= year_2023]
after_2023.sort(key=lambda x: datetime.strptime(x['date'], format("%Y-%m-%d")))

df = pd.DataFrame(after_2023)
print(df)
df.to_csv("tians.csv", index=False)