# API 엔드포인트

### [teams](\teams.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v1/competitions/8/seasons/2024/teams?_limit=20

```mermaid
erDiagram
    team {
        INT team_id PK "팀ID (id)"
        STRING(3) team_cd "팀코드 (abbr)"
        STRING team_sn "팀명 (shortName)"
        STRING stadium_cn "나라 (country)"
        STRING stadium_ct "도시 (city)"
        STRING stadium_nm "경기장 (name)"
        INT stadium_cc "수용인원 (capcity)"
    }
```

---

### [standings](\standings.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v5/competitions/8/seasons/2025/matchweeks/1/standings

```mermaid
erDiagram
    standings {
        DATA_TYPE name PK "Domain"
    }
```

---

### [matches1](\matches1.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v1/competitions/8/seasons/2025/matchweeks/25/matches

```mermaid
erDiagram
    matches1 {
        DATA_TYPE name PK "Domain"
    }
```

---

### [matches2](\matches2.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v2/matches?competition=8&season=2025&matchweek=25

```mermaid
erDiagram
    matches2 {
        DATA_TYPE name PK "Domain"
    }
```

---

### [momentum](\momentum.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v1/matches/2562085/momentum

```mermaid
erDiagram
    momentum {
        DATA_TYPE name PK "Domain"
    }
```

---

### [stats](\stats.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v3/matches/2562085/stats
```mermaid
erDiagram
    stats {
        DATA_TYPE name PK "Domain"
    }
```

---

### [preview](\preview.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v2/matches/2562085/preview
```mermaid
erDiagram
    preview {
        DATA_TYPE name PK "Domain"
    }
```

---

### [lineups](\lineups.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v3/matches/2562085/lineups
```mermaid
erDiagram
    lineups {
        DATA_TYPE name PK "Domain"
    }
```

---

### [commentary](\commentary.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v1/matches/2562085/commentary?_limit=100
```mermaid
erDiagram
    commentary {
        DATA_TYPE name PK "Domain"
    }
```
