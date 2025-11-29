import json
import pandas as pd
import numpy as np
from pathlib import Path


def process_2026_current_players():
    """Process 2026 current season players only"""

    # Load 2026 stats for role and year info
    stats_2026 = pd.read_csv("temp_data/2026_stats.csv")
    stats_2026['player_lower'] = stats_2026['Player'].str.lower().str.strip()

    print(f"2026 Stats players: {len(stats_2026)}")

    # Create set of players to include (only those in 2026_stats.csv)
    players_to_include = set(stats_2026['player_lower'])
    print(f"Players to include: {len(players_to_include)}")

    # Load 2026 JSON
    json_file = "temp_data/2026_pbp_playerstat_array.json"
    with open(json_file, 'r') as f:
        year_data = json.load(f)

    print(f"Processing 2026 JSON: {len(year_data)} players")

    all_player_data = []
    for player_row in year_data:
        if len(player_row) >= 15:
            player_id, player_name, team = player_row[0], player_row[1], player_row[2]
            player_lower = player_name.lower().strip()

            # Only include players that are in 2026_stats.csv
            if player_lower not in players_to_include:
                continue
            rim_made, rim_miss, rim_ast = player_row[3], player_row[4], player_row[5]
            mid_made, mid_miss, mid_ast = player_row[6], player_row[7], player_row[8]
            three_made, three_miss, three_ast = player_row[9], player_row[10], player_row[11]
            dunk_made, dunk_miss, dunk_ast = player_row[12], player_row[13], player_row[14]

            all_player_data.append({
                'Player': player_name,
                'Team': team,
                'RimMade': rim_made,
                'RimMiss': rim_miss,
                'RimAst': rim_ast,
                'MidMade': mid_made,
                'MidMiss': mid_miss,
                'MidAst': mid_ast,
                'ThreeMade': three_made,
                'ThreeMiss': three_miss,
                'ThreeAst': three_ast,
                'DunkMade': dunk_made,
                'DunkMiss': dunk_miss,
                'DunkAst': dunk_ast
            })

    df_2026 = pd.DataFrame(all_player_data)
    df_2026['player_lower'] = df_2026['Player'].str.lower().str.strip()

    print(f"Total 2026 players: {len(df_2026)}")

    # Group by player_lower and sum stats for transfers/duplicate names
    stat_cols_to_sum = ['RimMade', 'RimMiss', 'RimAst', 'MidMade', 'MidMiss', 'MidAst',
                        'ThreeMade', 'ThreeMiss', 'ThreeAst', 'DunkMade', 'DunkMiss', 'DunkAst']

    # Aggregate: sum stats, keep first Player/Team
    agg_dict = {col: 'sum' for col in stat_cols_to_sum}
    agg_dict['Player'] = 'first'
    agg_dict['Team'] = 'first'

    df_2026 = df_2026.groupby('player_lower', as_index=False).agg(agg_dict)
    print(f"After deduplication: {len(df_2026)} unique players")

    # Merge with stats to get Role and YR (inner join to only keep exact matches)
    df_2026 = df_2026.merge(stats_2026[['player_lower', 'Role', 'YR']],
                            on='player_lower', how='inner')

    # Convert to numeric
    stat_cols = ['RimMade', 'RimMiss', 'RimAst', 'MidMade', 'MidMiss', 'MidAst',
                 'ThreeMade', 'ThreeMiss', 'ThreeAst', 'DunkMade', 'DunkMiss', 'DunkAst']

    for col in stat_cols:
        df_2026[col] = pd.to_numeric(df_2026[col], errors='coerce').fillna(0)

    print("\nCalculating shooting metrics...")

    # --- Non-dunk rim ---
    df_2026["ND_RimMade"] = (df_2026["RimMade"] -
                             df_2026["DunkMade"]).clip(lower=0)
    df_2026["ND_RimMiss"] = (df_2026["RimMiss"] -
                             df_2026["DunkMiss"]).clip(lower=0)
    df_2026["ND_RimAtt"] = df_2026["ND_RimMade"] + df_2026["ND_RimMiss"]
    df_2026["NonDunk_Rim%"] = df_2026["ND_RimMade"] / \
        df_2026["ND_RimAtt"].replace({0: np.nan})
    df_2026["NonDunk_Assisted%"] = ((df_2026["RimAst"] - df_2026["DunkAst"]).clip(lower=0) /
                                    df_2026["ND_RimMade"].replace({0: np.nan}))

    # --- Total rim ---
    df_2026["RimAtt"] = df_2026["RimMade"] + df_2026["RimMiss"]
    df_2026["Total_Rim%"] = df_2026["RimMade"] / \
        df_2026["RimAtt"].replace({0: np.nan})
    df_2026["Total_Assisted_Rim%"] = df_2026["RimAst"] / \
        df_2026["RimMade"].replace({0: np.nan})

    # --- Midrange ---
    df_2026["Mid_Att"] = df_2026["MidMade"] + df_2026["MidMiss"]
    df_2026["Mid_FG%"] = df_2026["MidMade"] / \
        df_2026["Mid_Att"].replace({0: np.nan})
    df_2026["Mid_Assisted%"] = df_2026["MidAst"] / \
        df_2026["MidMade"].replace({0: np.nan})

    # --- 2pt combined ---
    df_2026["TwoPt_Att"] = df_2026["RimMade"] + \
        df_2026["RimMiss"] + df_2026["MidMade"] + df_2026["MidMiss"]
    df_2026["TwoPt_FG%"] = ((df_2026["RimMade"] + df_2026["MidMade"]) /
                            df_2026["TwoPt_Att"].replace({0: np.nan}))
    df_2026["TwoPt_Assisted%"] = ((df_2026["RimAst"] + df_2026["MidAst"]) /
                                  (df_2026["RimMade"] + df_2026["MidMade"]).replace({0: np.nan}))

    # --- Three ---
    df_2026["Three_Att"] = df_2026["ThreeMade"] + df_2026["ThreeMiss"]
    df_2026["Three_FG%"] = df_2026["ThreeMade"] / \
        df_2026["Three_Att"].replace({0: np.nan})
    df_2026["Three_Assisted%"] = df_2026["ThreeAst"] / \
        df_2026["ThreeMade"].replace({0: np.nan})

    # --- Total Assisted ---
    df_2026["Total_Assisted%"] = ((df_2026["RimAst"] + df_2026["MidAst"] + df_2026["ThreeAst"]) /
                                  (df_2026["RimMade"] + df_2026["MidMade"] + df_2026["ThreeMade"]).replace({0: np.nan}))

    # --- Shot Frequency Metrics ---
    df_2026["Total_Att"] = df_2026["RimAtt"] + \
        df_2026["Mid_Att"] + df_2026["Three_Att"]
    df_2026["Rim_Freq"] = df_2026["RimAtt"] / \
        df_2026["Total_Att"].replace({0: np.nan})
    df_2026["Mid_Freq"] = df_2026["Mid_Att"] / \
        df_2026["Total_Att"].replace({0: np.nan})
    df_2026["Three_Freq"] = df_2026["Three_Att"] / \
        df_2026["Total_Att"].replace({0: np.nan})
    df_2026["TwoPt_Freq"] = df_2026["TwoPt_Att"] / \
        df_2026["Total_Att"].replace({0: np.nan})

    # --- Dunk Metrics ---
    df_2026["DunkAtt"] = df_2026["DunkMade"] + df_2026["DunkMiss"]
    df_2026["Dunk_Freq"] = df_2026["DunkAtt"] / \
        df_2026["Total_Att"].replace({0: np.nan})
    df_2026["Dunk_FG%"] = df_2026["DunkMade"] / \
        df_2026["DunkAtt"].replace({0: np.nan})

    # Add season markers
    df_2026["First_Season"] = 2026
    df_2026["Last_Season"] = 2026

    print("Shooting metrics calculated!")

    # Show sample
    print("\nSample of 2026 current players:")
    sample_cols = ['Player', 'YR', 'Role', 'Total_Rim%', 'Mid_FG%', 'Three_FG%',
                   'Total_Assisted%', 'Rim_Freq', 'Mid_Freq', 'Three_Freq']
    print(df_2026[sample_cols].head(10))

    # Save
    output_file = "temp_data/2026_current_players.csv"
    df_2026.to_csv(output_file, index=False)
    print(f"\nSaved 2026 current players to: {output_file}")
    print(f"Total players: {len(df_2026)}")
    print(f"Players with Role/YR: {df_2026['Role'].notna().sum()}")

    return df_2026


if __name__ == "__main__":
    result = process_2026_current_players()
