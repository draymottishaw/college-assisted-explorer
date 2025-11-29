import pandas as pd

# Load NBA complete assisted data
nba_df = pd.read_csv('temp_data/nba_complete_assisted.csv')

# Load NBA combine data
combine_df = pd.read_csv('temp_data/nba_combine_data_clean.csv')

# Clean player names for matching
nba_df['player_match'] = nba_df['Player'].str.lower().str.strip()
combine_df['player_match'] = combine_df['PLAYER_NAME'].str.lower().str.strip()

# Get height data (using HEIGHT_WO_SHOES as it's more consistent)
height_data = combine_df[['player_match',
                          'HEIGHT_WO_SHOES']].drop_duplicates('player_match')

# Merge height data
nba_df = nba_df.merge(height_data, on='player_match', how='left')
nba_df.rename(columns={'HEIGHT_WO_SHOES': 'Height'}, inplace=True)

# Drop the temporary matching column
nba_df.drop(columns=['player_match'], inplace=True)

print(f"Total NBA players: {len(nba_df)}")
print(f"Players with height data: {nba_df['Height'].notna().sum()}")
print(f"\nSample players with height:")
print(nba_df[nba_df['Height'].notna()][['Player', 'Height']].head(10))

# Save updated file
nba_df.to_csv('temp_data/nba_complete_assisted.csv', index=False)
print("\nSaved updated nba_complete_assisted.csv with Height column")
