import pandas as pd

print("Loading files...")
df_all = pd.read_csv('temp_data/all_assisted.csv')
bart_pos = pd.read_csv('temp_data/Bart_Core_Positions.csv')

print(f"Total players in all_assisted: {len(df_all)}")
print(f"Players with positions in Bart file: {len(bart_pos)}")

# Add Role_final column if it doesn't exist
if 'Role_final' not in df_all.columns:
    df_all['Role_final'] = None

# Standardize positions from Bart data


def standardize_position(position):
    if pd.isna(position):
        return None

    position = str(position).upper()

    # Guard: PG, SG, G, Wing G, Combo G, etc.
    if 'G' in position and 'F' not in position:
        return 'G'

    # Forward: PF, SF, Wing F, Stretch 4, F
    if any(x in position for x in ['PF', 'SF', 'WING F', 'STRETCH 4']) or position == 'F':
        return 'F'

    # Forward-Center combos
    if 'F-C' in position or 'C-F' in position:
        return 'F'

    # Center: C
    if position == 'C':
        return 'C'

    return None


# Standardize Bart positions
bart_pos['Role_standardized'] = bart_pos['Role'].apply(standardize_position)

# Create lookup with lowercase player names
bart_pos['player_lower'] = bart_pos['Player'].str.lower().str.strip()

# Merge positions
print("\nMerging positions...")
for i, row in df_all.iterrows():
    player_lower = row['Player_lower']

    # Look up in Bart data
    match = bart_pos[bart_pos['player_lower'] == player_lower]

    if not match.empty:
        position = match.iloc[0]['Role_standardized']
        if position:
            df_all.at[i, 'Role_final'] = position

# Save results
print("\nSaving updated all_assisted.csv...")
df_all.to_csv('temp_data/all_assisted.csv', index=False)

print(f"\nComplete!")
print(f"Players with positions: {df_all['Role_final'].notna().sum()}")
print(f"Players without positions: {df_all['Role_final'].isna().sum()}")

# Show breakdown by position
print(f"\nPosition breakdown:")
print(df_all['Role_final'].value_counts(dropna=False))
