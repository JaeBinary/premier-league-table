import pandas as pd
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

# 1. EPL API 데이터 가져오기
url = "https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v5/competitions/8/seasons/2025/standings"
data = requests.get(url).json()
matchweek = int(data['matchweek'])

# 2. 구글 시트 인증 (GitHub Secrets에서 가져올 예정)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# 로컬 테스트 시에는 json 파일을 읽고, 서버(GitHub)에서는 환경변수에서 읽음
creds_json = os.environ.get('GSPREAD_CREDENTIALS')
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
client = gspread.authorize(creds)

# 3. 시트 열기
sheet = client.open("EPL_Standings_2025").get_worksheet(0)

# 4. 중복 체크 및 데이터 추가
existing_matchweeks = sheet.col_values(1) # 첫 번째 컬럼(Matchweek) 확인

if str(matchweek) in existing_matchweeks:
    print(f"{matchweek}주차 데이터가 이미 존재합니다. 업데이트를 중단합니다.")
else:
    rows_to_add = []
    for entry in data['tables'][0]['entries']:
        stats = entry['overall']
        rows_to_add.append([matchweek, entry['team']['name'], stats['points'], stats['position'], stats['played']])
    
    sheet.append_rows(rows_to_add)
    print(f"{matchweek}주차 데이터가 성공적으로 추가되었습니다.")