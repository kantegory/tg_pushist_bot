from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# from # pprint import # pprint
import httplib2
from oauth2client.service_account import ServiceAccountCredentials


def sheets_connect(scopes, spreadsheet_id=None, ranges=None):
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

    return service


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
    # pprint(response)


def get_sheets_value(service, spreadsheet_id, ranges):
    # simple get all of values in range
    request = service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id,
        ranges=ranges
    )

    response = request.execute()

    return response['valueRanges'][0]['values'][0]


def set_sheets_value(service, spreadsheet_id, ranges, values):
    sheet = service.spreadsheets()
    request = sheet.values().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": ranges,
             "majorDimension": "ROWS",
             # сначала заполнять ряды, затем столбцы (т.е. самые внутренние списки в values - это ряды)
             "values": [values]}
        ]
    })
    response = request.execute()
    # pprint(response)


def main():
    pass
    # If modifying these scopes, delete the file token.pickle.
    # scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    # spreadsheet_id, spreadsheet_url, service = create_sheet(scopes, 'test')
    # user_email = input('Введите gmail почту для доступа к редактированию таблицы Вашего бота:')
    # give_access(user_email, spreadsheet_id)
    # The ID and range of a sample spreadsheet.
    # spreadsheet_id = '1PMHlClUrQc8fPZRVRPwprthY2jRCWt2ZMh-I32FK9ko'
    # ranges = 'Лист1!A2:E2'
    #
    # service = sheets_connect(scopes)
    # title = "Статистика пушиста"
    # spreadsheet_id, spreadsheet_url, service = create_sheet(scopes, title)
    # sheet_title = 'Статистика по дням'
    # create_new_list(spreadsheet_id, service, sheet_title)
    # curr_row = 1
    # ranges = sheet_title + '!A' + str(curr_row) + ':F' + str(curr_row)
    # curr_row += 1
    # new_ranges = sheet_title + '!A' + str(curr_row) + ':F' + str(curr_row)
    # values = ['День', 'Кол-во пользователей:', 'Кол-во оплат:',	'Кол-во использования промокодов:',	'Кол-во запросов созданных за сутки:', 'Кол-во запросов отправленных за сутки:']
    # set_sheets_value(service, spreadsheet_id, ranges, values)
    # set_sheets_value(service, spreadsheet_id, new_ranges, values)
    # append_sheets_value(service, spreadsheet_id, new_ranges, values)
    # print(spreadsheet_id, spreadsheet_url)


if __name__ == "__main__":
    main()
