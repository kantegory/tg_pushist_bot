from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import httplib2
from oauth2client.service_account import ServiceAccountCredentials


def create_sheet(scopes, title):
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    print('it maybe useful link', service)

    spreadsheet_body = {
          "properties": {
            "title": title
          }
    }


    request = service.spreadsheets().create(body=spreadsheet_body)

    response = request.execute()

    spreadsheet_id, spreadsheet_url = response["spreadsheetId"], response["spreadsheetUrl"]

    return spreadsheet_id, spreadsheet_url, service


def give_access(user_email, spreadsheet_id):
    credentials = ServiceAccountCredentials.from_json_keyfile_name('pushiststat.json',
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    driveService = build('drive', 'v3', http=httpAuth)
    shareRes = driveService.permissions().create(
        fileId=spreadsheet_id,
        body={'type': 'anyone', 'role': 'writer', 'emailAddress': user_email},  # доступ на чтение кому угодно
        fields='id'
    )
    shareRes.execute()


def create_new_list(spreadsheet_id, service, sheet_title):
    sheet = service.spreadsheets()
    request = sheet.batchUpdate(spreadsheetId=spreadsheet_id, body={
          "requests": [
            {
              "addSheet": {
                "properties": {
                    "title": sheet_title,
                }
              }
            }
          ]
        }
    )
    response = request.execute()


def get_sheets_value(service, spreadsheet_id, ranges):
    
    request = service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id,
        ranges=ranges
    )

    response = request.execute()

    return response['valueRanges'][0]['values']


def set_sheets_value(service, spreadsheet_id, ranges, values):
    sheet = service.spreadsheets()
    request = sheet.values().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": ranges,
             "majorDimension": "ROWS",
             # сначала заполнять ряды, затем столбцы (т.е. самые внутренние списки в values - это ряды)
             "values": values}
        ]
    })
    response = request.execute()
