# premier-league-table
2025/26 Premier League Table

## 설치

```shell
c:\GitHub\premier-league-table\.venv\Scripts\python.exe -m pip install requests
c:\GitHub\premier-league-table\.venv\Scripts\python.exe -m pip install pandas
c:\GitHub\premier-league-table\.venv\Scripts\python.exe -m pip install rich
c:\GitHub\premier-league-table\.venv\Scripts\python.exe -m pip install openpyxl
```

## 데이터 구조 (ERD)

```mermaid
erDiagram
    teams ||--o{ overall_stats : "has"
    teams ||--o{ home_stats : "has"
    teams ||--o{ away_stats : "has"

    teams {
        INT ID PK
        STRING code
        STRING short_name
        STRING name
        STRING county
        STRING city
        STRING stadium
        INT capacity
        STRING logo_URL
    }

    overall_stats {
        INT round
        INT ID FK
        INT goals_for
        INT goals_against
        INT won
        INT drawn
        INT lost
        INT played
        INT poINTs
        INT position
        INT starting_position
    }

    home_stats {
        INT round
        INT ID FK
        INT goals_for
        INT goals_against
        INT won
        INT drawn
        INT lost
        INT played
        INT poINTs
        INT position
    }

    away_stats {
        INT round
        INT ID FK
        INT goals_for
        INT goals_against
        INT won
        INT drawn
        INT lost
        INT played
        INT poINTs
        INT position
    }
```