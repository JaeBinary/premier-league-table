import pandas as pd
import requests

def extract_full_epl_data():
    url = "https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v5/competitions/8/seasons/2025/standings"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    data = response.json()

    # 공통 정보 (모든 행에 동일하게 들어갈 메타데이터)
    matchweek = data.get("matchweek")           # 현재 진행 중인 라운드 번호
    season_name = data.get("season", {}).get("name") # 시즌 명칭 (예: Season 2025/2026)
    
    all_rows = []

    for entry in data['tables'][0]['entries']:
        team = entry['team']
        ovr = entry['overall']
        home = entry['home']
        away = entry['away']

        row = {
            # --- 기본 및 팀 정보 ---
            "Season": season_name,              # 시즌 (데이터 구분용)
            "Matchweek": matchweek,             # 라운드 (시계열 분석의 핵심 축)
            "Team": team['name'],               # 팀 전체 이름 (예: Arsenal)
            "Abbr": team['abbr'],               # 팀 약어 (예: ARS)
            
            # --- 종합 성적 (Overall Standings) ---
            "Pos": ovr['position'],             # 현재 전체 순위
            "Start_Pos": ovr['startingPosition'], # 해당 라운드 시작 전 순위 (순위 변동 추적용)
            "P": ovr['played'],                 # 전체 경기 수
            "W": ovr['won'],                    # 전체 승리 수
            "D": ovr['drawn'],                  # 전체 무승부 수
            "L": ovr['lost'],                   # 전체 패배 수
            "GF": ovr['goalsFor'],              # 전체 득점 (Goals For)
            "GA": ovr['goalsAgainst'],          # 전체 실점 (Goals Against)
            "GD": ovr['goalsFor'] - ovr['goalsAgainst'], # 전체 득실차 (Goal Difference)
            "Pts": ovr['points'],               # 전체 승점 (Points)

            # --- 홈 성적 (Home Records) ---
            "H_Pos": home['position'],          # 홈 경기 기준 순위
            "H_P": home['played'],              # 홈 경기 수
            "H_W": home['won'],                 # 홈 승리
            "H_D": home['drawn'],               # 홈 무승부
            "H_L": home['lost'],                # 홈 패배
            "H_GF": home['goalsFor'],           # 홈 득점
            "H_GA": home['goalsAgainst'],       # 홈 실점
            "H_GD": home['goalsFor'] - home['goalsAgainst'], # 홈 득실차
            "H_Pts": home['points'],            # 홈 승점

            # --- 원정 성적 (Away Records) ---
            "A_Pos": away['position'],          # 원정 경기 기준 순위
            "A_P": away['played'],              # 원정 경기 수
            "A_W": away['won'],                 # 원정 승리
            "A_D": away['drawn'],               # 원정 무승부
            "A_L": away['lost'],                # 원정 패배
            "A_GF": away['goalsFor'],           # 원정 득점
            "A_GA": away['goalsAgainst'],       # 원정 실점
            "A_GD": away['goalsFor'] - away['goalsAgainst'], # 원정 득실차
            "A_Pts": away['points']             # 원정 승점
        }
        all_rows.append(row)

    return pd.DataFrame(all_rows)

# 데이터프레임 생성 및 확인
df = extract_full_epl_data()
print(df)

"""
Number (decimal)  //실수
Number (whole)    //정수
Date & Time
Date
String
Spatial
Boolean
"""