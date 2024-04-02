from credentialsHandler import handle_creds
from googleapiclient.discovery import build

class GoogleAPIHandler:
    def __init__(self):
        self.creds = handle_creds()
        self.sheet_service = None
        self.cal_service = None
    
    def get_sheets_service(self):
        if not self.sheet_service:
            self.sheet_service = build("sheets", "v4", credentials=self.creds)
        return self.sheet_service


    def get_cal_service(self):
        if not self.cal_service:
            self.cal_service = build("calendar", "v3", credentials=self.creds)
        return self.cal_service
