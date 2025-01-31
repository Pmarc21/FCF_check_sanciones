import requests
from bs4 import BeautifulSoup
import datetime

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
    print(suspended_players)
    return suspended_players

def get_match_lineups(matchday):
    matchdays_url = f"https://www.fcf.cat/resultats/2425/futbol-sala/lliga-segona-divisio-catalana-futbol-sala/bcn-gr-3/{matchday}"
    response = requests.get(matchdays_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    matchdays = []
    for match in soup.select(".uppercase.w-100.fs-12_tp.fs-11_ml.table_resultats tr"):  # Ajustar según estructura HTML
        # print(match)  # Ajustar según estructura HTML
        columns = match.find_all("a")
        hrefs = [link.get('href') for link in columns if "acta" in link.get('href', '')]
        print(hrefs)

        if len(columns) >= 3:
            match_date_text = columns[2].text.strip()
            # href = columns.get('href')
            # print(href)
            try:
                match_date = datetime.datetime.strptime(match_date_text, "%d/%m/%Y").date()
            except ValueError:
                continue
            
            lineup_url = match.find("a")["href"] if match.find("a") else None
            if lineup_url:
                matchdays.append({
                    "date": match_date,
                    "lineup_url": lineup_url
                })
    
    return sorted(matchdays, key=lambda x: x["date"])

def check_suspended_players():
    for matchday in generate_matchdays():
        suspended_players = get_suspended_players(matchday)
        actas_matchday = get_actas_matchdays(matchday)
        matchdays = get_match_lineups(actas_matchday)

    player_suspensions = {}
    for player, data in suspended_players.items():
        player_suspensions[player] = {
            "end_date": None,
            "matches_remaining": data["sanction_matches"]
        }
    
    irregularities = []
    for match in matchdays:
        match_date = match["date"]
        lineup_url = "https://www.fcf.cat" + match["lineup_url"]
        response = requests.get(lineup_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for player in player_suspensions.keys():
            if player_suspensions[player]["matches_remaining"] > 0:
                for squad_player in soup.select(".player-name"):  # Ajustar selector
                    if squad_player.text.strip() == player:
                        irregularities.append(f"{player} jugó el {match_date} estando sancionado por {suspended_players[player]['sanction_matches']} partidos desde {suspended_players[player]['sanction_date']}.")
                player_suspensions[player]["matches_remaining"] -= 1
    
    return irregularities

def generate_matchdays():
    matchdays = []
    for i in range(1,27):
        matchdays.append(f"jornada-{i}")
    return matchdays

def get_actas_matchdays(matchday):
    matchdays_url = f"https://www.fcf.cat/resultats/2425/futbol-sala/lliga-segona-divisio-catalana-futbol-sala/bcn-gr-3/{matchday}"
    response = requests.get(matchdays_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    hrefs = []
    for match in soup.select(".uppercase.w-100.fs-12_tp.fs-11_ml.table_resultats tr"):  # Ajustar según estructura HTML
        # print(match)  # Ajustar según estructura HTML
        columns = match.find_all("a")
        [hrefs.append(link.get('href')) for link in columns if "acta" in link.get('href', '')]
    print(hrefs)
    return hrefs
    
if __name__ == "__main__":
    issues = check_suspended_players()
    if issues:
        print("Jugadores sancionados que jugaron irregularmente:")
        for issue in issues:
            print(issue)
    else:
        print("No se encontraron irregularidades.")