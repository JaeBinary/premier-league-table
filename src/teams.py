import requests
import pandas as pd
import time
from pathlib import Path
from rich.console import Console

console = Console()

# ==================== API 설정 ====================
COMPETITION_ID = 8  # 프리미어리그
SEASON_ID = 2025    # 2024-2025 시즌

TEAMS_API_URL = (
    "https://sdp-prem-prod.premier-league-prod.pulselive.com"
    "/api/v1/competitions/{comp_id}/seasons/{season_id}/teams?_limit=20"
)

LOGO_URL_TEMPLATE = "https://resources.premierleague.com/premierleague25/badges-alt/{team_id}.svg"

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

def fetch_teams_data(session: requests.Session) -> dict | None:
    """
    프리미어리그 팀 데이터를 API에서 가져옴

    Args:
        session: HTTP 요청에 사용할 requests.Session 객체

    Returns:
        성공 시 팀 데이터가 담긴 dict, 실패 시 None

    Note:
        - Rate limit(429) 발생 시 자동으로 재시도
        - 최대 MAX_RETRIES 횟수만큼 재시도 시도
    """
    url = TEAMS_API_URL.format(comp_id=COMPETITION_ID, season_id=SEASON_ID)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url)

            if response.status_code == 200:
                return response.json()

            # Rate limit에 걸린 경우 대기 후 재시도
            if response.status_code == 429:
                console.print(
                    f"[yellow]Rate limit 감지, {RETRY_WAIT}초 후 재시도 "
                    f"({attempt}/{MAX_RETRIES})[/yellow]"
                )
                time.sleep(RETRY_WAIT)
                continue

            # 기타 HTTP 에러는 재시도하지 않고 종료
            console.print(f"[red]HTTP Error {response.status_code}: {response.reason}[/red]")
            return None

        except Exception as e:
            console.print(f"[red]요청 중 에러 발생: {e}[/red]")

            # 마지막 시도가 아니면 재시도
            if attempt < MAX_RETRIES:
                console.print(f"[yellow]{RETRY_WAIT}초 후 재시도 ({attempt}/{MAX_RETRIES})[/yellow]")
                time.sleep(RETRY_WAIT)

    console.print(f"[red]최대 재시도 횟수({MAX_RETRIES})를 초과했습니다.[/red]")
    return None


def extract_teams_data(teams_json: dict) -> list[dict]:
    """
    API 응답에서 필요한 팀 정보를 추출하여 정제된 리스트로 변환

    Args:
        teams_json: API로부터 받은 원본 JSON 데이터

    Returns:
        팀 정보가 담긴 dict의 리스트
        각 dict는 team_id, team_cd, team_sn, team_name, stadium 정보, logo_url 포함
    """
    teams_list = []

    for team in teams_json.get('data', []):
        stadium_info = team.get('stadium', {})

        team_data = {
            'team_id': int(team.get('id')),
            'team_cd': team.get('abbr'),
            'team_sn': team.get('shortName'),
            'team_name': team.get('name'),
            'stadium_cn': stadium_info.get('country'),
            'stadium_ct': stadium_info.get('city'),
            'stadium_nm': stadium_info.get('name'),
            'stadium_cc': stadium_info.get('capacity'),
            'logo_url': LOGO_URL_TEMPLATE.format(team_id=team.get('id'))
        }
        teams_list.append(team_data)

    return teams_list


def save_to_excel(teams_data: list[dict], output_path: Path) -> None:
    """
    팀 데이터를 엑셀 파일로 저장

    Args:
        teams_data: 팀 정보가 담긴 dict의 리스트
        output_path: 저장할 엑셀 파일 경로

    Note:
        - 부모 디렉토리가 없으면 자동으로 생성
        - openpyxl 엔진 사용 (xlsx 형식)
    """
    # 디렉토리가 없으면 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(teams_data)
    df.to_excel(output_path, index=False, engine='openpyxl')

    console.print(f"[green]✓ 저장 완료:[/green] {output_path} ([bold]{len(df)}[/bold]개 팀)")


def main() -> None:
    """
    프리미어리그 팀 데이터 수집 프로세스를 실행하는 메인 함수

    Process:
        1. API로부터 현재 시즌 팀 데이터 가져오기
        2. 필요한 정보만 추출하여 정제
        3. 엑셀 파일로 저장
    """
    excel_path = Path('data/teams.xlsx')

    console.print("\n[bold magenta]═══ Premier League Teams Data ═══[/bold magenta]\n")

    with requests.Session() as session:
        session.headers.update(HEADERS)

        # Step 1: API 호출
        console.print("[cyan]Step 1:[/cyan] API에서 팀 데이터 가져오는 중...")
        teams_json = fetch_teams_data(session)

        if teams_json is None:
            console.print("\n[bold red]✗ 실패:[/bold red] 팀 데이터를 가져올 수 없습니다.\n")
            return

        team_count = len(teams_json.get('data', []))
        console.print(f"[green]✓ 완료:[/green] {team_count}개 팀 데이터 수신\n")

        # Step 2: 데이터 추출
        console.print("[cyan]Step 2:[/cyan] 필요한 정보 추출 및 정제 중...")
        teams_data = extract_teams_data(teams_json)
        console.print(f"[green]✓ 완료:[/green] 팀 정보 추출 (경기장, 로고 URL 포함)\n")

        # Step 3: 엑셀 저장
        console.print("[cyan]Step 3:[/cyan] 엑셀 파일로 저장 중...")
        save_to_excel(teams_data, excel_path)

    console.print("\n[bold green]═══ 모든 작업 완료! ═══[/bold green]\n")


if __name__ == "__main__":
    main()
