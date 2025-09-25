from espn_api.football import League, Matchup, Player, BoxPlayer, Team
from espn_api.football import box_score
from espn_api.football import helper
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

name_map  = {
    "Calvin's Daddy":"Harry",
    "Dee Wuffest":"Jake",
    "Is this the dagger":"DC",
    "LeFantasy Football":"Ethan",
    "Mat Noment Oens":"Harry",
    "Mr. Strydom and Me":"Cawley",
    "Otay MyMan":"Cawley",
    "PBR Kayla":"Stager",
    "Small PP team":"Greenberg",
    "Straw Hat":"Cash",
    "Swordless Mimetown":"Hayden",
    "Team Miller":"Gavin",
    "Team Rock":"Calvin",
    "Tiitsburgh Feelers":"Gavin",
    "Zilwaukee Chudwick":"Chad",
    "That was the dagger":"DC"
}


def pull_team_by_position_stats(year):
    league_id = 1957747319
    espn_s2 = "AEBb%2FDwONHQyMedrYsdD%2FErgg4sIQEhuTg7HnQfw7cAswgeY8hvRVZM3bBS7Kn3lqzpR7fANyNnx3gSb0cKpo078OukVEfEo4zHTtIAp4BPh7KkrKU0%2BxwT%2FWx0505bJz95b4C6OEA6o3AuzDrcEnhUS0X6dC%2B3fGbzoNgAjZxP5BiLSPgu5tYn%2BWhXwqw9ajsxxMIIIOFvAhSv%2BQOXnHpd8rG%2FmPKR3faPQlaoNs3aiLWdv%2B63EiYIzCeC%2FzeHcq8Fhhtbg27xT4%2FyLiMeGCAllTFia6KLg9X7R58tbGc7QbQ%3D%3D"
    swid = "{FBA603CA-5829-4581-A603-CA5829E581F0}"

    # create League object
    league = League(
        league_id=league_id,
        year=year,
        espn_s2=espn_s2,
        swid=swid
    )

    finals = []
    try:
        for week in range(1, 15):
            frames = []
            for matchup in league.box_scores(week=week):
                for str in ['home', 'away']:
                    team = getattr(matchup, f"{str}_team")
                    players = [player.name for player in getattr(matchup, f"{str}_lineup")]
                    # actual_breakdown = [pd.DataFrame(player.stats['breakdown'] for player in getattr(matchup, f"{str}_lineup"))]
                    # projected_breakdown = [pd.DataFrame(player.stats['projected_breakdown'] for player in getattr(matchup, f"{str}_lineup"))]
                    player_scored = [player.points for player in getattr(matchup, f"{str}_lineup")]
                    player_projected = [player.projected_points for player in getattr(matchup, f"{str}_lineup")]
                    position = [player.position for player in getattr(matchup, f"{str}_lineup")]
                    starter_nonstarter = [player.slot_position for player in getattr(matchup, f"{str}_lineup")]

                    stats = pd.DataFrame({
                        'week':week,
                        'home_away':str,
                        'team':team.team_name,
                        'players':players,
                        'player_scored':player_scored,
                        'player_projected':player_projected,
                        'position':position,
                        'started_nonstarted':starter_nonstarter
                    })
                    frames.append(stats)
            finals.append(pd.concat(frames))
    except:
        return None

    stats_all = pd.concat(finals)
    stats_all['year'] = year

    stats_all['first_name'] = stats_all['team'].apply(lambda x: name_map[x.rstrip()])
    
    stats_all.loc[stats_all['started_nonstarted'] == 'RB/WR/TE', 'started_nonstarted'] = 'FLEX'

    return stats_all

def get_total_scoring_by_team(year):
    league_id = 1957747319
    espn_s2 = "AEBb%2FDwONHQyMedrYsdD%2FErgg4sIQEhuTg7HnQfw7cAswgeY8hvRVZM3bBS7Kn3lqzpR7fANyNnx3gSb0cKpo078OukVEfEo4zHTtIAp4BPh7KkrKU0%2BxwT%2FWx0505bJz95b4C6OEA6o3AuzDrcEnhUS0X6dC%2B3fGbzoNgAjZxP5BiLSPgu5tYn%2BWhXwqw9ajsxxMIIIOFvAhSv%2BQOXnHpd8rG%2FmPKR3faPQlaoNs3aiLWdv%2B63EiYIzCeC%2FzeHcq8Fhhtbg27xT4%2FyLiMeGCAllTFia6KLg9X7R58tbGc7QbQ%3D%3D"
    swid = "{FBA603CA-5829-4581-A603-CA5829E581F0}"

    # create League object
    league = League(
        league_id=league_id,
        year=year,
        espn_s2=espn_s2,
        swid=swid
    )

    all_weeks = []
    all_weeks_pivot = []
    for week in range(1, 15):
        frames = []
        frames_pivot = []
        for matchup in league.box_scores(week=week):
            matchups = []
            matchups_pivot = []
            max_score = 0
            for str in ['home', 'away']:
                team = getattr(matchup, f"{str}_team") 
                score = getattr(matchup, f"{str}_score")
                projected = getattr(matchup, f"{str}_projected")
                allowed = getattr(matchup, f"{np.setdiff1d(['home', 'away'], str)[0]}_score")

                stats = pd.DataFrame({
                        f'year':year,
                        f'week':week,
                        f'{str}_team':team.team_name,
                        f'{str}_team_first_name':name_map[team.team_name.rstrip()],
                        f'{str}_score':score,
                        f'{str}_projected':projected
                }, index=[0])   

                pivot_stats = pd.DataFrame({
                        f'year':year,
                        f'week':week,
                        f'home_away':str,
                        f'team':team.team_name,
                        f'team_first_name':name_map[team.team_name.rstrip()],
                        f'score':score,
                        f'projected':projected,
                        f'allowed':allowed,
                        f'wins':team.wins,
                        f'losses':team.losses,
                        f'wl_pct':(team.wins) / (team.wins + team.losses),
                        f'standing':np.where(np.array(league.standings()) == team)[0]
                }, index=[0])   
                

                if score > max_score:
                    winner = team
                    max_score = score

                matchups.append(stats)
                matchups_pivot.append(pivot_stats)

            merged = pd.merge(left=matchups[0], right=matchups[1], on=['year', 'week'])     
            merged['winner'] = winner
            
            frames.append(merged)
            frames_pivot.append(pd.concat(matchups_pivot))
            

        all_weeks.append(pd.concat(frames))
        all_weeks_pivot.append(pd.concat(frames_pivot))
    
    return pd.concat(all_weeks), pd.concat(all_weeks_pivot)


if __name__ == '__main__':
    years = [2023, 2024, 2025]
    stats = pd.concat(pull_team_by_position_stats(year=year) for year in years)
    scoreboard = pd.concat(get_total_scoring_by_team(year=year)[0] for year in years)
    scoreboard_pivot = pd.concat(get_total_scoring_by_team(year=year)[1] for year in years)
    
    stats.to_csv('/Users/benstager/Desktop/fantasy/data/team_stats_by_position.csv')
    scoreboard.to_csv('/Users/benstager/Desktop/fantasy/data/scoreboard.csv')
    scoreboard_pivot.to_csv('/Users/benstager/Desktop/fantasy/data/scoreboard_pivot.csv')
    