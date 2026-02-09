import requests
import pandas as pd
import time

from rich.console import Console
from rich.progress import track

COMPETITION_ID = 8
SEASON_ID = 2025
START_ROUND = 1
END_ROUND = 38

BASE_URL = (
    "https://sdp-prem-prod.premier-league-prod.pulselive.com"
    "/api/v5/competitions/{comp_id}/seasons/{season_id}/matchweeks/{mw_id}/standings"
)

HEADERS = {
    "Origin": "https://www.premierleague.com",
    "Referer": "https://www.premierleague.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}

MAX_RETRIES = 3
RETRY_WAIT = 5

console = Console()


def fetch_round(session: requests.Session, round_num: int) -> dict | None:
    url = BASE_URL.format(comp_id=COMPETITION_ID, season_id=SEASON_ID, mw_id=round_num)
    for attempt in range(1, MAX_RETRIES + 1):
        response = session.get(url)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 429:
            console.print(f"[yellow][Round {round_num}] Rate limited, {RETRY_WAIT}초 후 재시도 ({attempt}/{MAX_RETRIES})[/yellow]")
            time.sleep(RETRY_WAIT)
        else:
            return None
    return None


def parse_entry(entry: dict, round_num: int) -> tuple[dict, dict, dict]:
    team = entry["team"]
    t_id = team["id"]

    team_row = {
        "team_id": t_id,
        "team_name": team.get("name"),
        "team_code": team.get("abbr"),
    }

    overall_row = {
        "round": round_num, "team_id": t_id,
        "pre_rk": entry["overall"].get("startingPosition"),
        "all_rk": entry["overall"].get("position"),
        "all_gp": entry["overall"].get("played"),
        "all_w": entry["overall"].get("won"),
        "all_d": entry["overall"].get("drawn"),
        "all_l": entry["overall"].get("lost"),
        "all_gf": entry["overall"].get("goalsFor"),
        "all_ga": entry["overall"].get("goalsAgainst"),
        "all_p": entry["overall"].get("points"),
    }

    home_row = {
        "round": round_num, "team_id": t_id,
        "home_rk": entry["home"].get("position"),
        "home_gp": entry["home"].get("played"),
        "home_w": entry["home"].get("won"),
        "home_d": entry["home"].get("drawn"),
        "home_l": entry["home"].get("lost"),
        "home_gf": entry["home"].get("goalsFor"),
        "home_ga": entry["home"].get("goalsAgainst"),
        "home_p": entry["home"].get("points"),
    }

    away_row = {
        "round": round_num, "team_id": t_id,
        "away_rk": entry["away"].get("position"),
        "away_gp": entry["away"].get("played"),
        "away_w": entry["away"].get("won"),
        "away_d": entry["away"].get("drawn"),
        "away_l": entry["away"].get("lost"),
        "away_gf": entry["away"].get("goalsFor"),
        "away_ga": entry["away"].get("goalsAgainst"),
        "away_p": entry["away"].get("points"),
    }

    return team_row, overall_row, home_row, away_row


def save_csv(data_store: dict) -> None:
    dfs = {
        "competition": pd.DataFrame(list(data_store["competition"].values())),
        "season": pd.DataFrame(list(data_store["season"].values())),
        "team": pd.DataFrame(list(data_store["team"].values())),
        "overall": pd.DataFrame(data_store["overall"]),
        "home": pd.DataFrame(data_store["home"]),
        "away": pd.DataFrame(data_store["away"]),
    }
    for name, df in dfs.items():
        file_path = f"data/{name}.csv"
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        console.print(f"[green]저장 완료:[/green] {file_path} ({len(df)}행)")


def main():
    data_store = {
        "competition": {},
        "season": {},
        "team": {},
        "overall": [],
        "home": [],
        "away": [],
    }

    console.print(f"\n[bold magenta][{SEASON_ID}/{(SEASON_ID+1) % 100:02d} Premier League][/bold magenta]")

    with requests.Session() as session:
        session.headers.update(HEADERS)
        for round_num in track(range(START_ROUND, END_ROUND + 1), description="[cyan]수집 현황:[/cyan]"):
            try:
                data = fetch_round(session, round_num)
                if data is None:
                    continue

                if "competition" in data:
                    comp = data["competition"]
                    data_store["competition"][comp["id"]] = {
                        "comp_id": comp.get("id"),
                        "comp_code": comp.get("code"),
                        "comp_name": comp.get("name"),
                    }
                if "season" in data:
                    season = data["season"]
                    data_store["season"][season["id"]] = {
                        "season_id": season.get("id"),
                        "season_name": season.get("name"),
                    }

                if data.get("tables"):
                    for entry in data["tables"][0]["entries"]:
                        team_row, overall_row, home_row, away_row = parse_entry(entry, round_num)
                        t_id = team_row["team_id"]
                        data_store["team"].setdefault(t_id, team_row)
                        data_store["overall"].append(overall_row)
                        data_store["home"].append(home_row)
                        data_store["away"].append(away_row)

            except Exception as e:
                console.print(f"[red][Round {round_num}] 에러: {e}[/red]")

    console.print()
    save_csv(data_store)


if __name__ == "__main__":
    main()
