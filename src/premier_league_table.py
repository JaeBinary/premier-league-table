"""
프리미어리그 팀 정보 및 순위표 데이터 수집 스크립트

Teams API와 Standings API에서 데이터를 수집하여
하나의 엑셀 파일에 4개 시트로 저장합니다.
"""

import time
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from rich.console import Console
from rich.progress import track

# ==================== 초기화 ====================
console = Console()

# ==================== 상수 정의 ====================
# API 설정
COMPETITION_ID = 8
SEASON_ID = 2024
START_ROUND = 1
END_ROUND = 38

# API 엔드포인트
BASE_URL = "https://sdp-prem-prod.premier-league-prod.pulselive.com"
TEAMS_API_URL = f"{BASE_URL}/api/v1/competitions/{{comp_id}}/seasons/{{season_id}}/teams?_limit=20"
STANDINGS_API_URL = f"{BASE_URL}/api/v5/competitions/{{comp_id}}/seasons/{{season_id}}/matchweeks/{{matchweek}}/standings"
LOGO_URL_TEMPLATE = "https://resources.premierleague.com/premierleague25/badges-alt/{team_id}.svg"

# HTTP 설정
HEADERS = {
    "Origin": "https://www.premierleague.com",
    "Referer": "https://www.premierleague.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# 재시도 설정
MAX_RETRIES = 3
RETRY_WAIT = 5

# HTTP 상태 코드
HTTP_OK = 200
HTTP_RATE_LIMIT = 429

# 데이터 저장소 키
TEAMS = 'teams'
OVERALL_STATS = 'overall_stats'
HOME_STATS = 'home_stats'
AWAY_STATS = 'away_stats'


# ==================== 유틸리티 함수 ====================
def fetch_with_retry(
    session: requests.Session,
    url: str,
    context: str = ""
) -> Optional[dict]:
    """
    재시도 로직을 포함한 HTTP GET 요청

    Args:
        session: HTTP 요청에 사용할 requests.Session 객체
        url: 요청할 URL
        context: 로그 출력에 사용할 컨텍스트 정보

    Returns:
        성공 시 응답 JSON dict, 실패 시 None
    """
    prefix = f"[{context}] " if context else ""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url)

            if response.status_code == HTTP_OK:
                return response.json()

            if response.status_code == HTTP_RATE_LIMIT:
                console.print(
                    f"[yellow]{prefix}Rate limit 감지, {RETRY_WAIT}초 후 재시도 "
                    f"({attempt}/{MAX_RETRIES})[/yellow]"
                )
                time.sleep(RETRY_WAIT)
                continue

            console.print(f"[red]{prefix}HTTP Error {response.status_code}: {response.reason}[/red]")
            return None

        except Exception as e:
            console.print(f"[red]{prefix}요청 중 에러 발생: {e}[/red]")
            if attempt < MAX_RETRIES:
                console.print(f"[yellow]{prefix}{RETRY_WAIT}초 후 재시도 ({attempt}/{MAX_RETRIES})[/yellow]")
                time.sleep(RETRY_WAIT)

    console.print(f"[red]{prefix}최대 재시도 횟수({MAX_RETRIES})를 초과했습니다.[/red]")
    return None


def create_stats_dict(stats: dict, round_num: int, team_id: int, include_starting_position: bool = False) -> dict:
    """
    통계 딕셔너리 생성 헬퍼 함수

    Args:
        stats: API 응답의 통계 정보
        round_num: 라운드 번호
        team_id: 팀 ID
        include_starting_position: starting_position 포함 여부

    Returns:
        정제된 통계 딕셔너리
    """
    stats_dict = {
        'round': round_num,
        'ID': team_id,
        'goals_for': stats.get('goalsFor'),
        'goals_against': stats.get('goalsAgainst'),
        'won': stats.get('won'),
        'drawn': stats.get('drawn'),
        'lost': stats.get('lost'),
        'played': stats.get('played'),
        'points': stats.get('points'),
        'position': stats.get('position'),
    }

    if include_starting_position:
        stats_dict['starting_position'] = stats.get('startingPosition')

    return stats_dict


# ==================== Teams 데이터 수집 ====================
def fetch_teams_data(session: requests.Session) -> Optional[dict]:
    """프리미어리그 팀 데이터를 API에서 가져옴"""
    url = TEAMS_API_URL.format(comp_id=COMPETITION_ID, season_id=SEASON_ID)
    return fetch_with_retry(session, url)


def extract_teams_data(teams_json: dict) -> list[dict]:
    """
    API 응답에서 팀 정보 추출

    Args:
        teams_json: API로부터 받은 원본 JSON 데이터

    Returns:
        팀 정보 리스트
    """
    teams_list = []

    for team in teams_json.get('data', []):
        stadium_info = team.get('stadium', {})
        team_id = team.get('id')

        team_data = {
            'ID': int(team_id),
            'code': team.get('abbr'),
            'short_name': team.get('shortName'),
            'name': team.get('name'),
            'county': stadium_info.get('country'),
            'city': stadium_info.get('city'),
            'stadium': stadium_info.get('name'),
            'capacity': stadium_info.get('capacity'),
            'logo_URL': LOGO_URL_TEMPLATE.format(team_id=team_id)
        }
        teams_list.append(team_data)

    return teams_list


# ==================== Standings 데이터 수집 ====================
def fetch_standings_data(session: requests.Session, round_num: int) -> Optional[dict]:
    """프리미어리그 순위표 데이터를 API에서 가져옴"""
    url = STANDINGS_API_URL.format(
        comp_id=COMPETITION_ID,
        season_id=SEASON_ID,
        matchweek=round_num
    )
    return fetch_with_retry(session, url, context=f"Round {round_num}")


def extract_standings_data(standings_json: dict, round_num: int, data_store: dict) -> None:
    """
    API 응답에서 순위표 정보를 추출하여 data_store에 누적

    Args:
        standings_json: API로부터 받은 원본 JSON 데이터
        round_num: 현재 라운드 번호
        data_store: 데이터를 누적할 저장소
    """
    tables = standings_json.get('tables', [])
    if not tables:
        return

    entries = tables[0].get('entries', [])

    for entry in entries:
        team = entry.get('team', {})
        team_id = int(team.get('id'))

        # Overall 통계 (starting_position 포함)
        overall = entry.get('overall', {})
        data_store[OVERALL_STATS].append(
            create_stats_dict(overall, round_num, team_id, include_starting_position=True)
        )

        # Home 통계
        home = entry.get('home', {})
        data_store[HOME_STATS].append(
            create_stats_dict(home, round_num, team_id)
        )

        # Away 통계
        away = entry.get('away', {})
        data_store[AWAY_STATS].append(
            create_stats_dict(away, round_num, team_id)
        )


# ==================== 엑셀 저장 ====================
def save_dataframe_to_sheet(
    writer: pd.ExcelWriter,
    data: list[dict],
    sheet_name: str,
    sort_by: list[str] | str
) -> int:
    """
    DataFrame을 정렬하여 엑셀 시트에 저장

    Args:
        writer: pandas ExcelWriter 객체
        data: 저장할 데이터 리스트
        sheet_name: 시트 이름
        sort_by: 정렬 기준 컬럼 (리스트 또는 문자열)

    Returns:
        저장된 레코드 수
    """
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values(sort_by)
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    return len(df)


def save_to_excel(data_store: dict, output_path: Path) -> None:
    """
    4개 테이블을 시트별로 나눠서 엑셀 파일로 저장

    Args:
        data_store: 테이블 데이터가 담긴 dict
        output_path: 저장할 엑셀 파일 경로
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 시트 저장 설정 (시트명: (데이터, 정렬기준))
    sheets_config = {
        'teams': (data_store[TEAMS], 'ID'),
        'overall_stats': (data_store[OVERALL_STATS], ['round', 'position']),
        'home_stats': (data_store[HOME_STATS], ['round', 'position']),
        'away_stats': (data_store[AWAY_STATS], ['round', 'position']),
    }

    counts = {}
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, (data, sort_by) in sheets_config.items():
            counts[sheet_name] = save_dataframe_to_sheet(writer, data, sheet_name, sort_by)

    # 결과 출력
    console.print(f"\n[green]✓ 저장 완료:[/green] {output_path}")
    for sheet_name, count in counts.items():
        console.print(f"  • {sheet_name}: [bold]{count}[/bold]개 레코드")


# ==================== 메인 함수 ====================
def main() -> None:
    """
    프리미어리그 전체 데이터 수집 프로세스 실행

    Process:
        1. Teams 데이터 수집
        2. Standings 데이터 수집 (1-38 라운드)
        3. 엑셀 파일로 저장 (4개 시트)
    """
    output_path = Path('data/premier_league_table_2024-25.xlsx')

    # 데이터 저장소 초기화
    data_store = {
        TEAMS: [],
        OVERALL_STATS: [],
        HOME_STATS: [],
        AWAY_STATS: [],
    }

    console.print(
        f"\n[bold magenta]═══ Premier League Data Collection "
        f"({SEASON_ID}/{(SEASON_ID + 1) % 100:02d}) ═══[/bold magenta]\n"
    )

    with requests.Session() as session:
        session.headers.update(HEADERS)

        # Step 1: Teams 데이터 수집
        console.print("[cyan]Step 1:[/cyan] 팀 데이터 수집 중...")
        teams_json = fetch_teams_data(session)

        if teams_json is None:
            console.print("[bold red]✗ 실패:[/bold red] 팀 데이터를 가져올 수 없습니다.")
            console.print("[yellow]⚠ Standings 데이터만 수집합니다.[/yellow]\n")
        else:
            teams_data = extract_teams_data(teams_json)
            data_store[TEAMS] = teams_data
            console.print(f"[green]✓ 완료:[/green] {len(teams_data)}개 팀 정보 수집\n")

        # Step 2: Standings 데이터 수집
        console.print(f"[cyan]Step 2:[/cyan] 순위표 데이터 수집 중 ({START_ROUND}-{END_ROUND} 라운드)...")
        for round_num in track(range(START_ROUND, END_ROUND + 1), description="         진행"):
            standings_json = fetch_standings_data(session, round_num)

            if standings_json is None:
                console.print(f"[yellow][Round {round_num}] 데이터 수집 실패, 건너뜀[/yellow]")
                continue

            extract_standings_data(standings_json, round_num, data_store)

        total_rounds = END_ROUND - START_ROUND + 1
        console.print(f"[green]✓ 완료:[/green] {total_rounds}개 라운드 데이터 수집")

        # Step 3: 엑셀 저장
        console.print("\n[cyan]Step 3:[/cyan] 엑셀 파일로 저장 중...")
        save_to_excel(data_store, output_path)

    console.print("\n[bold green]═══ 모든 작업 완료! ═══[/bold green]\n")


if __name__ == "__main__":
    main()
