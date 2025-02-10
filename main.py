#sacar todas las jornadas para saber todos los jugadores que han jugado
#sacar los jugadores sancionados
#comparar si los jugadores sancionados han jugado en las jornadas posteriores

import requests
from bs4 import BeautifulSoup
from save_in_database import Session, SuspendedPlayer, MatchdayPlayers

def get_leagues():
    url = "https://www.fcf.cat/resultats/2425/futbol-sala/lliga-segona-divisio-catalana-futbol-sala/bcn-gr-3"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    select = soup.find("select")
    leagues = []

    for option in select.find_all("option"):
        name = option.text.strip()
        link = option.get("value")
        leagues.append((name, link))
    return leagues

def get_group_league(link):
    url = link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    select = soup.find(id="select_grupo")
    groups = []

    for group in select.find_all("option"):
        name = group.text.strip()
        link = group.get("value")
        groups.append((name, link))
    return groups

def get_suspended_players(link, matchday, lliga, grup):
    link = link.replace("resultats", "sancions")
    url = f"{link}/{matchday}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    

    suspended_players = {}
    suspended_players[matchday] = {}
    for row in soup.select(".fcftable-block tbody tr"):
        columns = row.find_all("td")
        if len(columns) >= 5:
            player_link = columns[1].find_all("a")
            player_name = player_link[1].text.strip() if player_link else ""
            team_name = columns[1].text.strip().replace("\n\n", "").replace(player_name, "").strip()
            sanction_matches = columns[4].text.strip()
            if sanction_matches:
                sanction_matches = int(sanction_matches)
            else:
                sanction_matches = 0
            
            if player_name in suspended_players[matchday]:
                suspended_players[matchday][player_name]["sanction_matches"] += sanction_matches
            else:
                suspended_players[matchday][player_name] = {
                    "sanction_matches": sanction_matches,
                    "team" : team_name,
                    "league": lliga,
                    "group": grup,
                }
    return suspended_players

def get_all_suspended_players(link, lliga, grup):
    all_suspended_players = {}

    for matchday in generate_matchdays():
        suspended_players = get_suspended_players(link, matchday, lliga, grup)
        all_suspended_players.update(suspended_players)
    
    return all_suspended_players

def get_hrefs_matchdays(link, matchday):
    matchdays_url = f"{link}/{matchday}"
    response = requests.get(matchdays_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    hrefs = []
    for match in soup.select(".uppercase.w-100.fs-12_tp.fs-11_ml.table_resultats tr"):
        columns = match.find_all("a")
        [hrefs.append(link.get('href')) for link in columns if "acta" in link.get('href', '')]
    return hrefs

def get_match_lineups(hrefs, matchday):
    players = []
    for href in hrefs:
        response = requests.get(href)
        soup = BeautifulSoup(response.text, 'html.parser')
        for match in soup.select(".col-md-4.p-0_ml table tbody tr td"):
            columns = match.find_all("a")
            players.extend(link.text.strip() for link in columns if link.get('href') and "jugador" in link['href'])
    return list(set(players)) #all players that have played in the matchday

def save_suspended_players_in_db(all_suspended_players):
    session = Session()
    session.query(SuspendedPlayer).delete()
    session.query(MatchdayPlayers).delete()
    session.commit()
    for matchday, data in all_suspended_players.items():
        for player_name, data_player in data.items():
            if data_player.get("sanction_matches") != 0 and player_name != "":
                suspended_player = SuspendedPlayer(
                    matchday=matchday.split("-")[1],
                    name=player_name,
                    sanction_matches=data_player.get("sanction_matches"),
                    team=data_player.get("team"),
                    league=data_player.get("league"),
                    group=data_player.get("group"),
                )
                session.add(suspended_player)
                session.commit()

def check_suspended_players(link):
    session = Session()
    suspended_players = session.query(SuspendedPlayer).all()
    for suspended_player in suspended_players:
        suspended_matchdays = generate_suspended_matchdays(suspended_player.matchday + 1, suspended_player.matchday + suspended_player.sanction_matches)
        for matchday in suspended_matchdays:
            hrefs_matchday = get_hrefs_matchdays(link, matchday)
            players_in_lineups = get_match_lineups(hrefs_matchday, matchday)
            # all_players_in_lineups[matchday] = players_in_lineups
            if suspended_player.name in players_in_lineups:
                print(f"Este jugador ha jugado cuando no debía! El jugador es {suspended_player.name} del equipo {suspended_player.team}. Fue sancionado en la jornada {suspended_player.matchday} de {suspended_player.sanction_matches} partidos y está jugando en la {matchday}")

def generate_matchdays():
    matchdays = []
    for i in range(1,27):
        matchdays.append(f"jornada-{i}")
    return matchdays

def generate_suspended_matchdays(start, end):
    matchdays = []
    for i in range(start,end+1):
        matchdays.append(f"jornada-{i}")
    return matchdays

if __name__ == "__main__":
    leagues = get_leagues()
    for i, league in enumerate(leagues, start=1):
        print(f"{i}.{league[0]}")
    lliga = int(input("Elige la liga que quieres consultar: "))
    if 1<=lliga<=len(leagues):
        selected_league = leagues[lliga-1]
        print("\nLiga seleccionada:", selected_league[0])
    for league, link in leagues:
        if selected_league[0] == league:
            groups = get_group_league(link)
    for i, group in enumerate(groups, start=1):
        print(f"{i}.{group[0]}")
    selected_group = int(input("Elige el grupo que quieres consultar: "))
    if 1<=selected_group<=len(groups):
        selected_group = groups[selected_group-1]
        print("\nGrupo seleccionado: ", selected_group[0])
    for group, link in groups:
        if selected_group[0] == group:
            issues = get_all_suspended_players(link, selected_league[0], selected_group[0])
            save_suspended_players_in_db(issues)
            check_suspended_players(link)    