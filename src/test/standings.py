import requests
import pandas as pd
import time
from pathlib import Path
from rich.console import Console
from rich.progress import track

console = Console()

# ==================== API 설정 ====================
COMPETITION_ID = 8  # 프리미어리그
SEASON_ID = 2024    # 2024/25 시즌
START_ROUND = 1     # 시작 라운드
END_ROUND = 38      # 종료 라운드

STANDINGS_API_URL = (
    "https://sdp-prem-prod.premier-league-prod.pulselive.com"
    "/api/v5/competitions/{comp_id}/seasons/{season_id}/matchweeks/{matchweek}/standings"
)

# ==================== HTTP 요청 설정 ====================
# API 차단 방지를 위해 공식 웹사이트에서 요청하는 것처럼 헤더 설정
HEADERS = {
    "Origin": "https://www.premierleague.com",
    "Referer": "https://www.premierleague.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}

# ==================== 재시도 설정 ====================
MAX_RETRIES = 3      # 최대 재시도 횟수
RETRY_WAIT = 5       # 재시도 대기 시간(초)

def fetch_standings_data(session: requests.Session, round_num: int) -> dict | None:
    """
    프리미어리그 순위표 데이터를 API에서 가져옴

    Args:
        session: HTTP 요청에 사용할 requests.Session 객체
        round_num: 라운드 번호

    Returns:
        성공 시 순위표 데이터가 담긴 dict, 실패 시 None

    Note:
        - Rate limit(429) 발생 시 자동으로 재시도
        - 최대 MAX_RETRIES 횟수만큼 재시도 시도
    """
    url = STANDINGS_API_URL.format(
        comp_id=COMPETITION_ID,
        season_id=SEASON_ID,
        matchweek=round_num
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url)

            if response.status_code == 200:
                return response.json()

            # Rate limit에 걸린 경우 대기 후 재시도
            if response.status_code == 429:
                console.print(
                    f"[yellow][Round {round_num}] Rate limit 감지, {RETRY_WAIT}초 후 재시도 "
                    f"({attempt}/{MAX_RETRIES})[/yellow]"
                )
                time.sleep(RETRY_WAIT)
                continue

            # 기타 HTTP 에러는 재시도하지 않고 종료
            console.print(f"[red][Round {round_num}] HTTP Error {response.status_code}: {response.reason}[/red]")
            return None

        except Exception as e:
            console.print(f"[red][Round {round_num}] 요청 중 에러 발생: {e}[/red]")

            # 마지막 시도가 아니면 재시도
            if attempt < MAX_RETRIES:
                console.print(f"[yellow][Round {round_num}] {RETRY_WAIT}초 후 재시도 ({attempt}/{MAX_RETRIES})[/yellow]")
                time.sleep(RETRY_WAIT)

    console.print(f"[red][Round {round_num}] 최대 재시도 횟수({MAX_RETRIES})를 초과했습니다.[/red]")
    return None


def extract_standings_data(standings_json: dict, round_num: int, data_store: dict) -> None:
    """
    API 응답에서 필요한 순위표 정보를 추출하여 data_store에 누적

    Args:
        standings_json: API로부터 받은 원본 JSON 데이터
        round_num: 현재 라운드 번호
        data_store: 데이터를 누적할 저장소

    Note:
        - standings_entry는 중복 없이 저장 (팀 정보는 한 번만)
        - 나머지 통계는 라운드별로 누적
    """
    # 메타 정보 추출
    matchweek = standings_json.get('matchweek')
    season_info = standings_json.get('season', {})
    competition_info = standings_json.get('competition', {})
    is_live = standings_json.get('live', False)

    # 시즌 및 대회 정보는 한 번만 저장
    if not data_store['standings_meta']:
        data_store['standings_meta'].append({
            'season_id': season_info.get('id'),
            'season_name': season_info.get('name'),
            'competition_id': competition_info.get('id'),
            'competition_name': competition_info.get('name'),
            'competition_code': competition_info.get('code'),
        })

    # 각 팀의 순위 데이터 추출
    tables = standings_json.get('tables', [])
    if tables:
        entries = tables[0].get('entries', [])

        for entry in entries:
            team = entry.get('team', {})
            overall = entry.get('overall', {})
            home = entry.get('home', {})
            away = entry.get('away', {})

            team_id = int(team.get('id'))

            # standings_entry 테이블 (중복 제거 - 팀당 1번만 저장)
            if team_id not in data_store['team_ids']:
                data_store['team_ids'].add(team_id)
                data_store['standings_entry'].append({
                    'ID': team_id,
                    'name': team.get('name'),
                    'short_name': team.get('shortName'),
                    'code': team.get('abbr'),
                })

            # overall_stats 테이블 (라운드별 누적)
            data_store['overall_stats'].append({
                'round': round_num,
                'ID': team_id,
                'goals_for': overall.get('goalsFor'),
                'goals_against': overall.get('goalsAgainst'),
                'won': overall.get('won'),
                'drawn': overall.get('drawn'),
                'lost': overall.get('lost'),
                'played': overall.get('played'),
                'points': overall.get('points'),
                'position': overall.get('position'),
                'starting_position': overall.get('startingPosition'),
            })

            # home_stats 테이블 (라운드별 누적)
            data_store['home_stats'].append({
                'round': round_num,
                'ID': team_id,
                'goals_for': home.get('goalsFor'),
                'goals_against': home.get('goalsAgainst'),
                'won': home.get('won'),
                'drawn': home.get('drawn'),
                'lost': home.get('lost'),
                'played': home.get('played'),
                'points': home.get('points'),
                'position': home.get('position'),
            })

            # away_stats 테이블 (라운드별 누적)
            data_store['away_stats'].append({
                'round': round_num,
                'ID': team_id,
                'goals_for': away.get('goalsFor'),
                'goals_against': away.get('goalsAgainst'),
                'won': away.get('won'),
                'drawn': away.get('drawn'),
                'lost': away.get('lost'),
                'played': away.get('played'),
                'points': away.get('points'),
                'position': away.get('position'),
            })


def save_to_excel(data_store: dict, output_path: Path) -> None:
    """
    순위표 데이터를 시트별로 나눠서 엑셀 파일로 저장

    Args:
        data_store: 5개의 테이블 데이터가 담긴 dict
        output_path: 저장할 엑셀 파일 경로

    Note:
        - 부모 디렉토리가 없으면 자동으로 생성
        - openpyxl 엔진 사용 (xlsx 형식)
        - 각 테이블은 별도의 시트로 저장
    """
    # 디렉토리가 없으면 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ExcelWriter를 사용하여 여러 시트에 저장
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # standings_entry 시트 (ID 기준 정렬)
        df_entry = pd.DataFrame(data_store['standings_entry'])
        if not df_entry.empty:
            df_entry = df_entry.sort_values('ID')
        df_entry.to_excel(writer, sheet_name='standings_entry', index=False)

        # overall_stats 시트 (round, position 기준 정렬)
        df_overall = pd.DataFrame(data_store['overall_stats'])
        if not df_overall.empty:
            df_overall = df_overall.sort_values(['round', 'position'])
        df_overall.to_excel(writer, sheet_name='overall_stats', index=False)

        # home_stats 시트 (round, position 기준 정렬)
        df_home = pd.DataFrame(data_store['home_stats'])
        if not df_home.empty:
            df_home = df_home.sort_values(['round', 'position'])
        df_home.to_excel(writer, sheet_name='home_stats', index=False)

        # away_stats 시트 (round, position 기준 정렬)
        df_away = pd.DataFrame(data_store['away_stats'])
        if not df_away.empty:
            df_away = df_away.sort_values(['round', 'position'])
        df_away.to_excel(writer, sheet_name='away_stats', index=False)

        # standings_meta 시트
        df_meta = pd.DataFrame(data_store['standings_meta'])
        df_meta.to_excel(writer, sheet_name='standings_meta', index=False)

    team_count = len(data_store['standings_entry'])
    overall_count = len(data_store['overall_stats'])
    home_count = len(data_store['home_stats'])
    away_count = len(data_store['away_stats'])

    console.print(
        f"[green]✓ 저장 완료:[/green] {output_path}\n"
        f"  • standings_entry: [bold]{team_count}[/bold]개 팀\n"
        f"  • overall_stats: [bold]{overall_count}[/bold]개 레코드\n"
        f"  • home_stats: [bold]{home_count}[/bold]개 레코드\n"
        f"  • away_stats: [bold]{away_count}[/bold]개 레코드\n"
        f"  • standings_meta: [bold]1[/bold]개 레코드"
    )


def main() -> None:
    """
    프리미어리그 순위표 데이터 수집 프로세스를 실행하는 메인 함수

    Process:
        1. 1라운드부터 38라운드까지 순차적으로 데이터 수집
        2. 필요한 정보만 추출하여 정제
        3. 엑셀 파일로 저장 (시트별로 분리)
    """
    excel_path = Path('data/standings.xlsx')

    # 데이터 저장소 초기화
    data_store = {
        'standings_entry': [],
        'overall_stats': [],
        'home_stats': [],
        'away_stats': [],
        'standings_meta': [],
        'team_ids': set(),  # 중복 제거용
    }

    console.print(f"\n[bold magenta]═══ Premier League Standings Data ({SEASON_ID}/{(SEASON_ID+1) % 100:02d}) ═══[/bold magenta]\n")

    with requests.Session() as session:
        session.headers.update(HEADERS)

        # Step 1: 각 라운드별 데이터 수집
        for round_num in track(range(START_ROUND, END_ROUND + 1), description="[cyan]데이터 수집 중:[/cyan]"):
            try:
                standings_json = fetch_standings_data(session, round_num)

                if standings_json is None:
                    console.print(f"[yellow][Round {round_num}] 데이터 수집 실패, 건너뜀[/yellow]")
                    continue

                # 데이터 추출 및 누적
                extract_standings_data(standings_json, round_num, data_store)

            except Exception as e:
                console.print(f"[red][Round {round_num}] 에러 발생: {e}[/red]")
                continue

    # Step 2: 엑셀 저장
    console.print("\n[cyan]엑셀 파일로 저장 중...[/cyan]")

    # team_ids set 제거 (저장 불필요)
    data_store.pop('team_ids', None)

    save_to_excel(data_store, excel_path)

    console.print("\n[bold green]═══ 모든 작업 완료! ═══[/bold green]\n")


if __name__ == "__main__":
    main()
