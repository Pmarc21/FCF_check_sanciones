#sacar todas las jornadas para saber todos los jugadores que han jugado
#sacar los jugadores sancionados
#comparar si los jugadores sancionados han jugado en las jornadas posteriores

import requests
from bs4 import BeautifulSoup
import datetime
from save_in_database import Session, SuspendedPlayer, MatchdayPlayers

def get_suspended_players(matchday):
    url = f"https://www.fcf.cat/sancions/2425/futbol-sala/lliga-segona-divisio-catalana-futbol-sala/bcn-gr-3/{matchday}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    

    suspended_players = {}
    suspended_players[matchday] = {}
    for row in soup.select(".fcftable-block tbody tr"):  # Ajustar según estructura HTML
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
                }
    return suspended_players

def get_all_suspended_players():
    all_suspended_players = {}

    for matchday in generate_matchdays():
        suspended_players = get_suspended_players(matchday)
        all_suspended_players.update(suspended_players)
    
    return all_suspended_players

def get_hrefs_matchdays(matchday):
    matchdays_url = f"https://www.fcf.cat/resultats/2425/futbol-sala/lliga-segona-divisio-catalana-futbol-sala/bcn-gr-3/{matchday}"
    response = requests.get(matchdays_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    hrefs = []
    for match in soup.select(".uppercase.w-100.fs-12_tp.fs-11_ml.table_resultats tr"):  # Ajustar según estructura HTML
        # print(match)  # Ajustar según estructura HTML
        columns = match.find_all("a")
        [hrefs.append(link.get('href')) for link in columns if "acta" in link.get('href', '')]
        # print(hrefs)
    return hrefs

def get_match_lineups(hrefs, matchday):
    players = []
    for href in hrefs:
        response = requests.get(href)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        for match in soup.select(".col-md-4.p-0_ml table tbody tr td"):  # Ajustar según estructura HTML
            # print(match)  # Ajustar según estructura HTML
            columns = match.find_all("a")
            players.extend(link.text.strip() for link in columns if link.get('href') and "jugador" in link['href'])
    return list(set(players)) #all players that have played in the matchday

def save_suspended_players_in_db(all_suspended_players):
    session = Session()
    for matchday, data in all_suspended_players.items():
        for player_name, data_player in data.items():
            if data_player.get("sanction_matches") != 0 and player_name != "":
                suspended_player = SuspendedPlayer(
                    matchday=matchday.split("-")[1],
                    name=player_name,
                    sanction_matches=data_player.get("sanction_matches"),
                    team=data_player.get("team")
                )
                session.add(suspended_player)
                session.commit()

def check_suspended_players():
    player_suspensions = {}
    all_players_in_lineups = {}
    session = Session()
    suspended_players = session.query(SuspendedPlayer).all()
    for suspended_player in suspended_players:
        suspended_matchdays = generate_suspended_matchdays(suspended_player.matchday + 1, suspended_player.matchday + suspended_player.sanction_matches)
        for matchday in suspended_matchdays:
            hrefs_matchday = get_hrefs_matchdays(matchday)
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
    # issues = get_all_suspended_players()
    # save_suspended_players_in_db(issues)
    check_suspended_players()