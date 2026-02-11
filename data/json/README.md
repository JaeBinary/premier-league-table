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
    standings_entry {
        INT team_id FK "팀ID (team.id)"
        STRING team_name "팀명 (team.name)"
        STRING team_sn "팀약칭 (team.shortName)"
        STRING(3) team_cd "팀코드 (team.abbr)"
    }

    home_stats {
        INT team_id FK "팀ID"
        INT goals_for "득점 (goalsFor)"
        INT goals_against "실점 (goalsAgainst)"
        INT won "승 (won)"
        INT drawn "무 (drawn)"
        INT lost "패 (lost)"
        INT played "경기수 (played)"
        INT points "승점 (points)"
        INT position "순위 (position)"
    }

    away_stats {
        INT team_id FK "팀ID"
        INT goals_for "득점 (goalsFor)"
        INT goals_against "실점 (goalsAgainst)"
        INT won "승 (won)"
        INT drawn "무 (drawn)"
        INT lost "패 (lost)"
        INT played "경기수 (played)"
        INT points "승점 (points)"
        INT position "순위 (position)"
    }

    overall_stats {
        INT team_id FK "팀ID"
        INT goals_for "득점 (goalsFor)"
        INT goals_against "실점 (goalsAgainst)"
        INT won "승 (won)"
        INT drawn "무 (drawn)"
        INT lost "패 (lost)"
        INT played "경기수 (played)"
        INT points "승점 (points)"
        INT position "순위 (position)"
        INT starting_position "시작순위 (startingPosition)"
    }

    standings_meta {
        INT matchweek PK "경기주차 (matchweek)"
        STRING season_id "시즌ID (season.id)"
        STRING season_name "시즌명 (season.name)"
        STRING competition_id "대회ID (competition.id)"
        STRING competition_name "대회명 (competition.name)"
        STRING competition_code "대회코드 (competition.code)"
        BOOLEAN live "라이브여부 (live)"
    }

    standings_entry ||--|| home_stats : "has"
    standings_entry ||--|| away_stats : "has"
    standings_entry ||--|| overall_stats : "has"
```

---

### [matches1](\matches1.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v1/competitions/8/seasons/2025/matchweeks/25/matches

```mermaid
erDiagram
    match {
        STRING match_id PK "경기ID (matchId)"
        DATETIME kickoff "킥오프시간 (kickoff)"
        STRING kickoff_tz "타임존 (kickoffTimezone)"
        STRING period "경기상태 (period)"
        STRING clock "경기시간 (clock)"
        STRING competition "대회명 (competition)"
        STRING ground "경기장 (ground)"
        INT attendance "관중수 (attendance)"
        STRING result_type "결과타입 (resultType)"
    }

    home_team {
        STRING match_id FK "경기ID"
        STRING team_id "팀ID (id)"
        STRING team_name "팀명 (name)"
        STRING team_sn "팀약칭 (shortName)"
        INT score "득점 (score)"
        INT half_time_score "전반득점 (halfTimeScore)"
        INT red_cards "퇴장 (redCards)"
    }

    away_team {
        STRING match_id FK "경기ID"
        STRING team_id "팀ID (id)"
        STRING team_name "팀명 (name)"
        STRING team_sn "팀약칭 (shortName)"
        INT score "득점 (score)"
        INT half_time_score "전반득점 (halfTimeScore)"
        INT red_cards "퇴장 (redCards)"
    }

    pagination {
        INT limit "제한 (_limit)"
        STRING prev "이전 (_prev)"
        STRING next "다음 (_next)"
    }

    match ||--|| home_team : "has"
    match ||--|| away_team : "has"
```

---

### [matches2](\matches2.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v2/matches?competition=8&season=2025&matchweek=25

```mermaid
erDiagram
    match_v2 {
        STRING match_id PK "경기ID (matchId)"
        STRING phase "페이즈 (phase)"
        STRING competition_id "대회ID (competitionId)"
        STRING competition "대회명 (competition)"
        STRING season "시즌 (season)"
        INT match_week "경기주차 (matchWeek)"
        DATETIME kickoff "킥오프시간 (kickoff)"
        STRING kickoff_tz "타임존 (kickoffTimezone)"
        STRING kickoff_tz_str "타임존문자열 (kickoffTimezoneString)"
        STRING period "경기상태 (period)"
        STRING clock "경기시간 (clock)"
        STRING ground "경기장 (ground)"
        INT attendance "관중수 (attendance)"
        STRING result_type "결과타입 (resultType)"
    }

    home_team_v2 {
        STRING match_id FK "경기ID"
        STRING team_id "팀ID (id)"
        STRING team_name "팀명 (name)"
        STRING team_sn "팀약칭 (shortName)"
        STRING(3) team_cd "팀코드 (abbr)"
        INT score "득점 (score)"
        INT half_time_score "전반득점 (halfTimeScore)"
        INT red_cards "퇴장 (redCards)"
    }

    away_team_v2 {
        STRING match_id FK "경기ID"
        STRING team_id "팀ID (id)"
        STRING team_name "팀명 (name)"
        STRING team_sn "팀약칭 (shortName)"
        STRING(3) team_cd "팀코드 (abbr)"
        INT score "득점 (score)"
        INT half_time_score "전반득점 (halfTimeScore)"
        INT red_cards "퇴장 (redCards)"
    }

    pagination_v2 {
        INT limit "제한 (_limit)"
        STRING prev "이전 (_prev)"
        STRING next "다음 (_next)"
    }

    match_v2 ||--|| home_team_v2 : "has"
    match_v2 ||--|| away_team_v2 : "has"
```

---

### [momentum](\momentum.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v1/matches/2562085/momentum

```mermaid
erDiagram
    match_info {
        STRING match_id PK "경기ID (id)"
        STRING op_id "작전ID (opId)"
        STRING coverage_level "커버리지레벨 (coverageLevel)"
        DATE match_date "경기날짜 (date)"
        TIME match_time "경기시간 (time)"
        STRING week "주차 (week)"
        INT num_periods "피리어드수 (numberOfPeriods)"
        INT period_length "피리어드길이 (periodLength)"
        STRING var "VAR사용 (var)"
        DATETIME last_updated "최종업데이트 (lastUpdated)"
        STRING description "설명 (description)"
    }

    competition_info {
        STRING competition_id PK "대회ID (competition.id)"
        STRING op_id "작전ID (opId)"
        STRING name "대회명 (name)"
        STRING known_name "알려진명칭 (knownName)"
        STRING code "코드 (competitionCode)"
        STRING format "형식 (competitionFormat)"
        STRING country "국가 (country.name)"
    }

    match_details {
        STRING match_id FK "경기ID"
        INT period_id "피리어드ID (periodId)"
        STRING status "경기상태 (matchStatus)"
        STRING winner "승자 (winner)"
        INT length_min "경기시간분 (matchLengthMin)"
        INT length_sec "경기시간초 (matchLengthSec)"
    }

    period_info {
        STRING match_id FK "경기ID"
        INT period_id PK "피리어드ID (id)"
        DATETIME start_time "시작시간 (start)"
        DATETIME end_time "종료시간 (end)"
        INT length_min "경기시간분 (lengthMin)"
        INT length_sec "경기시간초 (lengthSec)"
        INT injury_time "추가시간초 (announcedInjuryTime)"
    }

    score_info {
        STRING match_id FK "경기ID"
        STRING score_type "스코어타입 (ht/ft/total)"
        INT home_score "홈득점 (home)"
        INT away_score "원정득점 (away)"
    }

    momentum_prediction {
        STRING match_id FK "경기ID"
        STRING type "타입 (type)"
        INT time_min "경기시간분 (timeMin)"
        INT time_min_sec "경기시간초 (timeMinSec)"
        INT period_id "피리어드ID (periodId)"
        STRING pred_type "예측타입 (Home/Away/Combined)"
        DECIMAL probability "확률 (probability)"
    }

    goal_event {
        STRING match_id FK "경기ID"
        STRING contestant_id "팀ID (contestantId)"
        STRING op_contestant_id "작전팀ID (opContestantId)"
        INT period_id "피리어드ID (periodId)"
        INT time_min "경기시간분 (timeMin)"
        STRING time_min_sec "경기시간초 (timeMinSec)"
        DATETIME timestamp "타임스탬프 (timestamp)"
        STRING type "타입 (type)"
        STRING scorer_id "득점자ID (scorerId)"
        STRING scorer_name "득점자명 (scorerName)"
        STRING assist_player_id "어시스트ID (assistPlayerId)"
        STRING assist_player_name "어시스트명 (assistPlayerName)"
        STRING opta_event_id "이벤트ID (optaEventId)"
        INT home_score "홈득점 (homeScore)"
        INT away_score "원정득점 (awayScore)"
    }

    card_event {
        STRING match_id FK "경기ID"
        STRING contestant_id "팀ID (contestantId)"
        INT period_id "피리어드ID (periodId)"
        INT time_min "경기시간분 (timeMin)"
        STRING time_min_sec "경기시간초 (timeMinSec)"
        DATETIME timestamp "타임스탬프 (timestamp)"
        STRING type "카드타입 (type)"
        STRING player_id "선수ID (playerId)"
        STRING player_name "선수명 (playerName)"
        STRING card_reason "사유 (cardReason)"
    }

    substitute_event {
        STRING match_id FK "경기ID"
        STRING contestant_id "팀ID (contestantId)"
        INT period_id "피리어드ID (periodId)"
        INT time_min "경기시간분 (timeMin)"
        STRING time_min_sec "경기시간초 (timeMinSec)"
        STRING player_on_id "교체IN선수ID (playerOnId)"
        STRING player_on_name "교체IN선수명 (playerOnName)"
        STRING player_off_id "교체OUT선수ID (playerOffId)"
        STRING player_off_name "교체OUT선수명 (playerOffName)"
        STRING sub_reason "교체사유 (subReason)"
    }

    lineup_info {
        STRING match_id FK "경기ID"
        STRING contestant_id FK "팀ID (contestantId)"
        STRING formation "포메이션 (formationUsed)"
    }

    player_info {
        STRING match_id FK "경기ID"
        STRING contestant_id FK "팀ID"
        STRING player_id PK "선수ID (playerId)"
        STRING first_name "이름 (firstName)"
        STRING last_name "성 (lastName)"
        STRING match_name "경기명 (matchName)"
        INT shirt_number "등번호 (shirtNumber)"
        STRING position "포지션 (position)"
        STRING position_side "포지션사이드 (positionSide)"
        STRING formation_place "포메이션위치 (formationPlace)"
        STRING captain "주장여부 (captain)"
    }

    match_info ||--|| competition_info : "has"
    match_info ||--|| match_details : "has"
    match_info ||--|{ period_info : "has"
    match_info ||--|{ score_info : "has"
    match_info ||--|{ momentum_prediction : "has"
    match_info ||--|{ goal_event : "has"
    match_info ||--|{ card_event : "has"
    match_info ||--|{ substitute_event : "has"
    match_info ||--|{ lineup_info : "has"
    lineup_info ||--|{ player_info : "has"
```

---

### [stats](\stats.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v3/matches/2562085/stats
```mermaid
erDiagram
    team_match_stats {
        STRING team_id PK "팀ID (teamId)"
        STRING side "홈원정 (side)"
    }

    goal_stats {
        STRING team_id FK "팀ID"
        INT goals "득점 (goals)"
        INT goals_conceded "실점 (goalsConceded)"
        INT goals_openplay "오픈플레이득점 (goalsOpenplay)"
        INT goals_conceded_ibox "박스내실점 (goalsConcededIbox)"
        INT goals_conceded_obox "박스밖실점 (goalsConcededObox)"
        DECIMAL expected_goals "예상득점 (expectedGoals)"
        DECIMAL expected_goals_on_target "예상타겟득점 (expectedGoalsOnTarget)"
        DECIMAL expected_goals_on_target_conceded "예상타겟실점 (expectedGoalsOnTargetConceded)"
        INT goal_assist "어시스트 (goalAssist)"
        INT goal_assist_openplay "오픈플레이어시스트 (goalAssistOpenplay)"
        INT goal_assist_setplay "세트피스어시스트 (goalAssistSetplay)"
        DECIMAL expected_assists "예상어시스트 (expectedAssists)"
    }

    shot_stats {
        STRING team_id FK "팀ID"
        INT total_scoring_att "총슛 (totalScoringAtt)"
        INT ontarget_scoring_att "유효슛 (ontargetScoringAtt)"
        INT shot_off_target "슛오프타겟 (shotOffTarget)"
        INT big_chance_scored "빅찬스득점 (bigChanceScored)"
        INT big_chance_created "빅찬스생성 (bigChanceCreated)"
        INT attempts_ibox "박스내슛 (attemptsIbox)"
        INT attempts_obox "박스밖슛 (attemptsObox)"
        INT blocked_scoring_att "차단된슛 (blockedScoringAtt)"
        INT shot_fastbreak "역습슛 (shotFastbreak)"
    }

    pass_stats {
        STRING team_id FK "팀ID"
        INT total_pass "총패스 (totalPass)"
        INT accurate_pass "정확한패스 (accuratePass)"
        INT open_play_pass "오픈플레이패스 (openPlayPass)"
        INT successful_open_play_pass "성공한오픈플레이패스 (successfulOpenPlayPass)"
        INT fwd_pass "전진패스 (fwdPass)"
        INT backward_pass "후진패스 (backwardPass)"
        INT total_long_balls "총롱볼 (totalLongBalls)"
        INT accurate_long_balls "정확한롱볼 (accurateLongBalls)"
        INT total_cross "총크로스 (totalCross)"
        INT accurate_cross "정확한크로스 (accurateCross)"
        INT total_through_ball "총스루패스 (totalThroughBall)"
        INT accurate_through_ball "정확한스루패스 (accurateThroughBall)"
    }

    possession_stats {
        STRING team_id FK "팀ID"
        INT possession_percentage "점유율 (possessionPercentage)"
        INT touches "터치수 (touches)"
        INT touches_in_opp_box "상대박스터치 (touchesInOppBox)"
        INT ball_recovery "볼회수 (ballRecovery)"
        INT poss_lost_all "볼소유상실 (possLostAll)"
        INT poss_lost_ctrl "컨트롤상실 (possLostCtrl)"
        INT dispossessed "탈취당함 (dispossessed)"
    }

    defensive_stats {
        STRING team_id FK "팀ID"
        INT total_tackle "총태클 (totalTackle)"
        INT won_tackle "성공태클 (wonTackle)"
        INT interception "인터셉트 (interception)"
        INT interception_won "성공인터셉트 (interceptionWon)"
        INT total_clearance "총클리어런스 (totalClearance)"
        INT effective_clearance "유효클리어런스 (effectiveClearance)"
        INT head_clearance "헤드클리어런스 (headClearance)"
        INT outfielder_block "필드차단 (outfielderBlock)"
        INT blocked_cross "차단크로스 (blockedCross)"
    }

    duel_stats {
        STRING team_id FK "팀ID"
        INT duel_won "듀얼승 (duelWon)"
        INT duel_lost "듀얼패 (duelLost)"
        INT aerial_won "공중볼승 (aerialWon)"
        INT aerial_lost "공중볼패 (aerialLost)"
        INT won_contest "컨테스트승 (wonContest)"
        INT total_contest "총컨테스트 (totalContest)"
        INT challenge_lost "챌린지패 (challengeLost)"
    }

    card_stats {
        STRING team_id FK "팀ID"
        INT yellow_card "옐로카드 (yellowCard)"
        INT red_card "레드카드 (redCard)"
        INT total_yel_card "총옐로카드 (totalYelCard)"
        INT total_red_card "총레드카드 (totalRedCard)"
    }

    goalkeeper_stats {
        STRING team_id FK "팀ID"
        INT saves "선방 (saves)"
        INT saved_ibox "박스내선방 (savedIbox)"
        INT saved_obox "박스밖선방 (savedObox)"
        INT diving_save "다이빙선방 (divingSave)"
        INT good_high_claim "공중볼잡기 (goodHighClaim)"
        INT punches "펀칭 (punches)"
        INT keeper_throws "킥스로우 (keeperThrows)"
        INT accurate_keeper_throws "정확한스로우 (accurateKeeperThrows)"
    }

    other_stats {
        STRING team_id FK "팀ID"
        INT corner_taken "코너킥 (cornerTaken)"
        INT won_corners "획득코너 (wonCorners)"
        INT lost_corners "상실코너 (lostCorners)"
        INT total_offside "오프사이드 (totalOffside)"
        INT fk_foul_won "파울획득 (fkFoulWon)"
        INT fk_foul_lost "파울범함 (fkFoulLost)"
        DECIMAL total_distance "총이동거리 (totalDistance)"
        JSON fastest_player "최고속도선수 (fastestPlayer)"
        INT subs_made "교체수 (subsMade)"
        INT error_lead_to_goal "실책실점 (errorLeadToGoal)"
        INT error_lead_to_shot "실책슛허용 (errorLeadToShot)"
    }

    team_match_stats ||--|| goal_stats : "has"
    team_match_stats ||--|| shot_stats : "has"
    team_match_stats ||--|| pass_stats : "has"
    team_match_stats ||--|| possession_stats : "has"
    team_match_stats ||--|| defensive_stats : "has"
    team_match_stats ||--|| duel_stats : "has"
    team_match_stats ||--|| card_stats : "has"
    team_match_stats ||--|| goalkeeper_stats : "has"
    team_match_stats ||--|| other_stats : "has"
```

---

### [preview](\preview.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v2/matches/2562085/preview
```mermaid
erDiagram
    previous_meeting {
        STRING match_id PK "경기ID (matchId)"
        DATETIME kickoff "킥오프시간 (kickoff)"
        STRING kickoff_tz "타임존 (kickoffTimezone)"
        STRING kickoff_tz_str "타임존문자열 (kickoffTimezoneString)"
        STRING ground "경기장 (ground)"
        STRING home_team_id "홈팀ID (homeTeam.team.id)"
        STRING home_team_name "홈팀명 (homeTeam.team.name)"
        STRING home_team_sn "홈팀약칭 (homeTeam.team.shortName)"
        STRING(3) home_team_cd "홈팀코드 (homeTeam.team.abbr)"
        INT home_score "홈득점 (homeTeam.score)"
        STRING away_team_id "원정팀ID (awayTeam.team.id)"
        STRING away_team_name "원정팀명 (awayTeam.team.name)"
        STRING away_team_sn "원정팀약칭 (awayTeam.team.shortName)"
        STRING(3) away_team_cd "원정팀코드 (awayTeam.team.abbr)"
        INT away_score "원정득점 (awayTeam.score)"
    }

    head_to_head {
        STRING team_a PK "팀A_ID (teamA)"
        STRING team_b PK "팀B_ID (teamB)"
        INT team_a_wins "팀A승수 (teamAWins)"
        INT team_b_wins "팀B승수 (teamBWins)"
        INT draws "무승부 (draws)"
        INT team_a_goals "팀A득점 (teamAGoals)"
        INT team_b_goals "팀B득점 (teamBGoals)"
        INT team_a_home_wins "팀A홈승 (teamAHomeWins)"
        INT team_b_home_wins "팀B홈승 (teamBHomeWins)"
        INT team_a_clean_sheets "팀A무실점 (teamACleanSheets)"
        INT team_b_clean_sheets "팀B무실점 (teamBCleanSheets)"
        INT team_a_penalties_scored "팀A페널티득점 (teamAPenaltiesScored)"
        INT team_b_penalties_scored "팀B페널티득점 (teamBPenaltiesScored)"
    }

    season_performance_home {
        STRING team_id PK "팀ID (team_id)"
        INT goals_for "득점 (goalsFor)"
        INT goals_against "실점 (goalsAgainst)"
        INT won "승 (won)"
        INT drawn "무 (drawn)"
        INT lost "패 (lost)"
        INT played "경기수 (played)"
        INT points "승점 (points)"
        INT position "순위 (position)"
        INT starting_position "시작순위 (startingPosition)"
        INT clean_sheets "무실점 (cleanSheets)"
        DECIMAL expected_goals "예상득점 (expectedGoals)"
    }

    season_performance_away {
        STRING team_id PK "팀ID (team_id)"
        INT goals_for "득점 (goalsFor)"
        INT goals_against "실점 (goalsAgainst)"
        INT won "승 (won)"
        INT drawn "무 (drawn)"
        INT lost "패 (lost)"
        INT played "경기수 (played)"
        INT points "승점 (points)"
        INT position "순위 (position)"
        INT starting_position "시작순위 (startingPosition)"
        INT clean_sheets "무실점 (cleanSheets)"
        DECIMAL expected_goals "예상득점 (expectedGoals)"
    }
```

---

### [lineups](\lineups.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v3/matches/2562085/lineups
```mermaid
erDiagram
    team_lineup {
        STRING team_id PK "팀ID (teamId)"
        STRING side "홈원정 (home_team/away_team)"
    }

    player_lineup {
        STRING player_id PK "선수ID (id)"
        STRING team_id FK "팀ID"
        STRING first_name "이름 (firstName)"
        STRING last_name "성 (lastName)"
        STRING known_name "별칭 (knownName)"
        STRING shirt_num "등번호 (shirtNum)"
        BOOLEAN is_captain "주장여부 (isCaptain)"
        STRING position "포지션 (position)"
        STRING sub_position "교체포지션 (subPosition)"
    }

    formation_info {
        STRING team_id PK "팀ID (teamId)"
        STRING formation "포메이션 (formation)"
        JSON lineup "선발라인업 (lineup)"
        JSON subs "교체선수목록 (subs)"
    }

    manager_info {
        STRING manager_id PK "감독ID (id)"
        STRING team_id FK "팀ID"
        STRING first_name "이름 (firstName)"
        STRING last_name "성 (lastName)"
        STRING type "타입 (type)"
    }

    team_lineup ||--|{ player_lineup : "has"
    team_lineup ||--|| formation_info : "has"
    team_lineup ||--|{ manager_info : "has"
```

---

### [commentary](\commentary.json)
Request URL: https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v1/matches/2562085/commentary?_limit=100
```mermaid
erDiagram
    commentary_event {
        DATETIME timestamp PK "타임스탬프 (timestamp)"
        STRING type "이벤트타입 (type)"
        STRING time "경기시간 (time)"
        STRING comment "중계내용 (comment)"
        STRING player1 "선수1_ID (player1)"
        STRING player2 "선수2_ID (player2)"
        STRING team1 "팀1_ID (team1)"
        STRING team2 "팀2_ID (team2)"
    }

    commentary_pagination {
        INT limit "제한 (_limit)"
        STRING prev "이전 (_prev)"
        STRING next "다음 (_next)"
    }

    event_type_enum {
        STRING type PK "이벤트타입"
        STRING description "설명"
    }

    commentary_event ||--o| event_type_enum : "has_type"
```
