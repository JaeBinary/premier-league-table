"""
프리미어리그 팀 정보 및 순위표 데이터 수집 스크립트

Teams API와 Standings API에서 데이터를 수집하여
하나의 엑셀 파일에 4개 시트로 저장합니다.
"""

import time
from pathlib import Path
from typing import Optional, TypedDict

import pandas as pd
import requests
from rich.console import Console
from rich.progress import track

# ==================== 타입 정의 ====================
class TeamData(TypedDict):
    """팀 정보 데이터 구조"""
    ID: int
    code: str
    short_name: str
    name: str
    country: str
    city: str
    stadium: str
    capacity: int
    logo_URL: str


class StatsData(TypedDict, total=False):
    """통계 데이터 구조"""
    round: int
    ID: int
    goals_for: int
    goals_against: int
    won: int
    drawn: int
    lost: int
    played: int
    points: int
    position: int
    starting_position: int  # overall 통계에서만 사용


class TeamPlayedInfo(TypedDict):
    """팀별 경기 수 추적 정보"""
    home_played: int
    away_played: int


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
                retry_msg = f"{prefix}Rate limit 감지, {RETRY_WAIT}초 후 재시도 ({attempt}/{MAX_RETRIES})"
                console.print(f"[yellow]{retry_msg}[/yellow]")
                time.sleep(RETRY_WAIT)
                continue

            error_msg = f"{prefix}HTTP Error {response.status_code}: {response.reason}"
            console.print(f"[red]{error_msg}[/red]")
            return None

        except Exception as e:
            console.print(f"[red]{prefix}요청 중 에러 발생: {e}[/red]")
            if attempt < MAX_RETRIES:
                retry_msg = f"{prefix}{RETRY_WAIT}초 후 재시도 ({attempt}/{MAX_RETRIES})"
                console.print(f"[yellow]{retry_msg}[/yellow]")
                time.sleep(RETRY_WAIT)

    console.print(f"[red]{prefix}최대 재시도 횟수({MAX_RETRIES})를 초과했습니다.[/red]")
    return None


def create_stats_dict(
    stats: dict,
    round_num: int,
    team_id: int,
    include_starting_position: bool = False
) -> StatsData:
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
    stats_dict: StatsData = {
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


def process_stats_if_played(
    stats: dict,
    round_num: int,
    team_id: int,
    played_key: str,
    tracker: dict[int, TeamPlayedInfo],
    data_list: list[StatsData]
) -> None:
    """
    경기를 진행한 경우에만 통계를 추가하는 헬퍼 함수

    Args:
        stats: API 응답의 통계 정보 (home 또는 away)
        round_num: 라운드 번호
        team_id: 팀 ID
        played_key: 'home_played' 또는 'away_played'
        tracker: 팀별 경기 수 추적 딕셔너리
        data_list: 통계를 추가할 리스트
    """
    current_played = stats.get('played', 0)
    previous_played = tracker[team_id][played_key]

    # 이전 라운드보다 played가 증가한 경우에만 저장
    if current_played > previous_played:
        data_list.append(create_stats_dict(stats, round_num, team_id))
        tracker[team_id][played_key] = current_played


# ==================== Teams 데이터 수집 ====================
def fetch_teams_data(session: requests.Session) -> Optional[dict]:
    """프리미어리그 팀 데이터를 API에서 가져옴"""
    url = TEAMS_API_URL.format(comp_id=COMPETITION_ID, season_id=SEASON_ID)
    return fetch_with_retry(session, url)


def extract_teams_data(teams_json: dict) -> list[TeamData]:
    """
    API 응답에서 팀 정보 추출

    Args:
        teams_json: API로부터 받은 원본 JSON 데이터

    Returns:
        팀 정보 리스트
    """
    teams_list: list[TeamData] = []

    for team in teams_json.get('data', []):
        stadium_info = team.get('stadium', {})
        team_id = team.get('id')

        team_data: TeamData = {
            'ID': int(team_id),
            'code': team.get('abbr'),
            'short_name': team.get('shortName'),
            'name': team.get('name'),
            'country': stadium_info.get('country'),
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


def extract_standings_data(
    standings_json: dict,
    round_num: int,
    data_store: dict[str, list],
    team_played_tracker: dict[int, TeamPlayedInfo]
) -> None:
    """
    API 응답에서 순위표 정보를 추출하여 data_store에 누적

    Args:
        standings_json: API로부터 받은 원본 JSON 데이터
        round_num: 현재 라운드 번호
        data_store: 데이터를 누적할 저장소
        team_played_tracker: 팀별 이전 라운드 played 값을 추적하는 딕셔너리
    """
    tables = standings_json.get('tables', [])
    if not tables:
        return

    entries = tables[0].get('entries', [])

    for entry in entries:
        team = entry.get('team', {})
        team_id = int(team.get('id'))

        # 팀별 추적 데이터 초기화
        if team_id not in team_played_tracker:
            team_played_tracker[team_id] = {'home_played': 0, 'away_played': 0}

        # Overall 통계 (starting_position 포함)
        overall = entry.get('overall', {})
        data_store[OVERALL_STATS].append(
            create_stats_dict(overall, round_num, team_id, include_starting_position=True)
        )

        # Home 통계 (경기를 진행한 경우에만 저장)
        home = entry.get('home', {})
        process_stats_if_played(
            home, round_num, team_id, 'home_played',
            team_played_tracker, data_store[HOME_STATS]
        )

        # Away 통계 (경기를 진행한 경우에만 저장)
        away = entry.get('away', {})
        process_stats_if_played(
            away, round_num, team_id, 'away_played',
            team_played_tracker, data_store[AWAY_STATS]
        )


# ==================== 엑셀 저장 ====================
def save_dataframe_to_sheet(
    writer: pd.ExcelWriter,
    data: list[TeamData | StatsData],
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


def save_to_excel(data_store: dict[str, list], output_path: Path) -> None:
    """
    4개 테이블을 시트별로 나눠서 엑셀 파일로 저장

    Args:
        data_store: 테이블 데이터가 담긴 dict
        output_path: 저장할 엑셀 파일 경로
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 통계 시트들의 공통 정렬 기준
    stats_sort_by = ['round', 'position']

    # 시트 저장 설정 (시트명: (데이터, 정렬기준))
    sheets_config = {
        'teams': (data_store[TEAMS], 'ID'),
        'overall_stats': (data_store[OVERALL_STATS], stats_sort_by),
        'home_stats': (data_store[HOME_STATS], stats_sort_by),
        'away_stats': (data_store[AWAY_STATS], stats_sort_by),
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
    data_store: dict[str, list] = {
        TEAMS: [],
        OVERALL_STATS: [],
        HOME_STATS: [],
        AWAY_STATS: [],
    }

    # 팀별 played 값 추적용 딕셔너리 (누적 데이터에서 실제 경기 여부 판단용)
    team_played_tracker: dict[int, TeamPlayedInfo] = {}

    season_display = f"{SEASON_ID}/{(SEASON_ID + 1) % 100:02d}"
    console.print(
        f"\n[bold magenta]═══ Premier League Data Collection ({season_display}) ═══[/bold magenta]\n"
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
        rounds_range = f"{START_ROUND}-{END_ROUND}"
        console.print(f"[cyan]Step 2:[/cyan] 순위표 데이터 수집 중 ({rounds_range} 라운드)...")

        for round_num in track(range(START_ROUND, END_ROUND + 1), description="         진행"):
            standings_json = fetch_standings_data(session, round_num)

            if standings_json is None:
                console.print(f"[yellow][Round {round_num}] 데이터 수집 실패, 건너뜀[/yellow]")
                continue

            extract_standings_data(standings_json, round_num, data_store, team_played_tracker)

        total_rounds = END_ROUND - START_ROUND + 1
        console.print(f"[green]✓ 완료:[/green] {total_rounds}개 라운드 데이터 수집")

        # Step 3: 엑셀 저장
        console.print("\n[cyan]Step 3:[/cyan] 엑셀 파일로 저장 중...")
        save_to_excel(data_store, output_path)

    console.print("\n[bold green]═══ 모든 작업 완료! ═══[/bold green]\n")


if __name__ == "__main__":
    main()
