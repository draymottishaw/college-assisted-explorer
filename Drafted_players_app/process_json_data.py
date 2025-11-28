import json
import pandas as pd
import numpy as np
from pathlib import Path


def process_all_json_files():
    """Process all JSON files and create comprehensive NBA player dataset with career totals"""

    # Load NBA players for reference
    nba_players = pd.read_csv("temp_data/nba_players.csv")
    nba_player_names = set(nba_players['Player'].str.lower().str.strip())

    print(f"NBA players to match: {len(nba_player_names)}")

    # Process all JSON files
    all_player_data = []
    years = range(2010, 2027)  # 2010-2026

    for year in years:
        json_file = f"temp_data/{year}_pbp_playerstat_array.json"
        json_path = Path(json_file)

        if not json_path.exists():
            print(f"Warning: {json_file} not found")
            continue

        try:
            with open(json_file, 'r') as f:
                year_data = json.load(f)

            print(f"Processing {year}: {len(year_data)} players")

            for player_row in year_data:
                if len(player_row) >= 15:  # Ensure we have all the data
                    player_id, player_name, team = player_row[0], player_row[1], player_row[2]

                    # Check if this player is in our NBA list
                    if player_name.lower().strip() in nba_player_names:
                        rim_made, rim_miss, rim_ast = player_row[3], player_row[4], player_row[5]
                        mid_made, mid_miss, mid_ast = player_row[6], player_row[7], player_row[8]
                        three_made, three_miss, three_ast = player_row[9], player_row[10], player_row[11]
                        dunk_made, dunk_miss, dunk_ast = player_row[12], player_row[13], player_row[14]

                        all_player_data.append({
                            'Player': player_name,
                            'Year': year,
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

        except Exception as e:
            print(f"Error processing {json_file}: {e}")

    print(f"\nTotal player-season records found: {len(all_player_data)}")

    # Convert to DataFrame
    df_all = pd.DataFrame(all_player_data)

    if len(df_all) == 0:
        print("No data found!")
        return None

    print(f"Unique players found: {df_all['Player'].nunique()}")

    # Now aggregate career totals for each player (keeping season info)
    print("Aggregating career totals...")

    # Group by player and sum all shooting stats
    career_totals = df_all.groupby('Player').agg({
        'RimMade': 'sum',
        'RimMiss': 'sum',
        'RimAst': 'sum',
        'MidMade': 'sum',
        'MidMiss': 'sum',
        'MidAst': 'sum',
        'ThreeMade': 'sum',
        'ThreeMiss': 'sum',
        'ThreeAst': 'sum',
        'DunkMade': 'sum',
        'DunkMiss': 'sum',
        'DunkAst': 'sum'
    }).reset_index()

    # Add season range for each player (first and last season)
    season_ranges = df_all.groupby('Player')['Year'].agg(
        ['min', 'max']).reset_index()
    season_ranges.columns = ['Player', 'First_Season', 'Last_Season']
    career_totals = career_totals.merge(season_ranges, on='Player', how='left')

    print(f"Career totals calculated for {len(career_totals)} players")

    # Calculate all the shooting percentages and frequencies (similar to utils.py)
    df_final = career_totals.copy()

    # Convert to numeric to handle any string/null issues
    stat_cols = ['RimMade', 'RimMiss', 'RimAst', 'MidMade', 'MidMiss', 'MidAst',
                 'ThreeMade', 'ThreeMiss', 'ThreeAst', 'DunkMade', 'DunkMiss', 'DunkAst']

    for col in stat_cols:
        df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)

    print("\nCalculating shooting metrics...")

    # --- Non-dunk rim ---
    df_final["ND_RimMade"] = (df_final["RimMade"] -
                              df_final["DunkMade"]).clip(lower=0)
    df_final["ND_RimMiss"] = (df_final["RimMiss"] -
                              df_final["DunkMiss"]).clip(lower=0)
    df_final["ND_RimAtt"] = df_final["ND_RimMade"] + df_final["ND_RimMiss"]
    df_final["NonDunk_Rim%"] = df_final["ND_RimMade"] / \
        df_final["ND_RimAtt"].replace({0: np.nan})
    df_final["NonDunk_Assisted%"] = ((df_final["RimAst"] - df_final["DunkAst"]).clip(lower=0) /
                                     df_final["ND_RimMade"].replace({0: np.nan}))

    # --- Total rim ---
    df_final["RimAtt"] = df_final["RimMade"] + df_final["RimMiss"]
    df_final["Total_Rim%"] = df_final["RimMade"] / \
        df_final["RimAtt"].replace({0: np.nan})
    df_final["Total_Assisted_Rim%"] = df_final["RimAst"] / \
        df_final["RimMade"].replace({0: np.nan})

    # --- Midrange ---
    df_final["Mid_Att"] = df_final["MidMade"] + df_final["MidMiss"]
    df_final["Mid_FG%"] = df_final["MidMade"] / \
        df_final["Mid_Att"].replace({0: np.nan})
    df_final["Mid_Assisted%"] = df_final["MidAst"] / \
        df_final["MidMade"].replace({0: np.nan})

    # --- 2pt combined ---
    df_final["TwoPt_Att"] = df_final["RimMade"] + \
        df_final["RimMiss"] + df_final["MidMade"] + df_final["MidMiss"]
    df_final["TwoPt_FG%"] = ((df_final["RimMade"] + df_final["MidMade"]) /
                             df_final["TwoPt_Att"].replace({0: np.nan}))
    df_final["TwoPt_Assisted%"] = ((df_final["RimAst"] + df_final["MidAst"]) /
                                   (df_final["RimMade"] + df_final["MidMade"]).replace({0: np.nan}))

    # --- Three ---
    df_final["Three_Att"] = df_final["ThreeMade"] + df_final["ThreeMiss"]
    df_final["Three_FG%"] = df_final["ThreeMade"] / \
        df_final["Three_Att"].replace({0: np.nan})
    df_final["Three_Assisted%"] = df_final["ThreeAst"] / \
        df_final["ThreeMade"].replace({0: np.nan})

    # --- Total Assisted ---
    df_final["Total_Assisted%"] = ((df_final["RimAst"] + df_final["MidAst"] + df_final["ThreeAst"]) /
                                   (df_final["RimMade"] + df_final["MidMade"] + df_final["ThreeMade"]).replace({0: np.nan}))

    # --- Shot Frequency Metrics ---
    df_final["Total_Att"] = df_final["RimAtt"] + \
        df_final["Mid_Att"] + df_final["Three_Att"]
    df_final["Rim_Freq"] = df_final["RimAtt"] / \
        df_final["Total_Att"].replace({0: np.nan})
    df_final["Mid_Freq"] = df_final["Mid_Att"] / \
        df_final["Total_Att"].replace({0: np.nan})
    df_final["Three_Freq"] = df_final["Three_Att"] / \
        df_final["Total_Att"].replace({0: np.nan})
    df_final["TwoPt_Freq"] = df_final["TwoPt_Att"] / \
        df_final["Total_Att"].replace({0: np.nan})

    # Add player_lower column for merging
    df_final["player_lower"] = df_final["Player"].str.lower().str.strip()

    print("Shooting metrics calculated!")

    # Show some sample data
    print("\nSample of final data:")
    sample_cols = ['Player', 'Total_Rim%', 'Mid_FG%', 'Three_FG%',
                   'Total_Assisted%', 'Rim_Freq', 'Mid_Freq', 'Three_Freq']
    print(df_final[sample_cols].head())

    # Save the comprehensive dataset
    output_file = "temp_data/nba_complete_assisted.csv"
    df_final.to_csv(output_file, index=False)
    print(f"\nSaved complete dataset to: {output_file}")
    print(f"Total players: {len(df_final)}")

    return df_final


if __name__ == "__main__":
    result = process_all_json_files()
