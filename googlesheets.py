from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pprint import pprint


def sheets_connect(scopes, spreadsheet_id, ranges):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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
    # request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body={
    #     "valueInputOption": "USER_ENTERED",
    #     "data": [
    #         {"range": "Лист1!A1:D1",
    #          "majorDimension": "ROWS",
    #          # сначала заполнять ряды, затем столбцы (т.е. самые внутренние списки в values - это ряды)
    #          "values": [["Время запроса бота", "Время ответа", "Имя пользователя", "Ответ"]]}
    #     ]
    # })

    return service


def get_sheets_value(service, spreadsheet_id, ranges):
    # simple get all of values in range
    request = service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id,
        ranges=ranges
    )

    response = request.execute()

    pprint(response['valueRanges'][0]['values'][0])


def set_sheets_value(service, spreadsheet_id, ranges, request_time=None, response_time=None, response_username=None, response_text=None):
    sheet = service.spreadsheets()
    request = sheet.values().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": ranges,
             "majorDimension": "ROWS",
             # сначала заполнять ряды, затем столбцы (т.е. самые внутренние списки в values - это ряды)
             "values": [[str(request_time), str(response_time), str(response_username), str(response_text)]]}
        ]
    })
    response = request.execute()
    pprint(response)


def main():
    # If modifying these scopes, delete the file token.pickle.
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    # The ID and range of a sample spreadsheet.
    spreadsheet_id = 'YOUR-SPREADSHEET-ID'
    ranges = 'YOUR RANGE IN SPREADSHEET'

    sheets_connect(scopes, spreadsheet_id, ranges)


if __name__ == "__main__":
    main()
