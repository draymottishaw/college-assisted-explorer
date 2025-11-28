"""
Fetch player position data from Sports Reference College Basketball
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# We'll fetch multiple years to get comprehensive data
years = range(2010, 2026)
all_players = []

for year in years:
    url = f"https://www.sports-reference.com/cbb/seasons/men/{year}-leaders.html"
    print(f"Fetching {year} data from Sports Reference...")

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        # Use pandas to read HTML tables
        tables = pd.read_html(response.content)

        for table in tables:
            if 'Player' in table.columns or 'Rk' in table.columns:
                # Add year column
                if 'Player' in table.columns:
                    table['Year'] = year
                    all_players.append(table)
                    print(f"  Found {len(table)} players from {year}")

        time.sleep(1)  # Be nice to the server

    except Exception as e:
        print(f"  Error fetching {year}: {e}")
        continue

if not all_players:
    print("No data found! Trying alternative approach...")
    exit(1)

# Combine all data
df = pd.concat(all_players, ignore_index=True)

# Clean up player names
if 'Player' in df.columns:
    df['player_lower'] = df['Player'].str.lower().str.strip()

print(f"\nTotal records: {len(df)}")
print(
    f"Unique players: {df['player_lower'].nunique() if 'player_lower' in df.columns else 'N/A'}")

# Look for position column
pos_col = None
for col in df.columns:
    if col.lower() in ['pos', 'position', 'role', 'class']:
        pos_col = col
        print(f"Found position column: {col}")
        break

if pos_col:
    # Standardize positions
    def standardize_role(role):
        if pd.isna(role) or role == '' or str(role).lower() in ['null', 'nan', 'none']:
            return None
        role = str(role).strip().upper()

        # Guard: PG, G, Wing G, Combo G, SG, etc.
        if 'PG' in role or 'SG' in role or ('G' in role and 'F' not in role):
            return 'G'
        # Forward: PF, SF, Wing F, Stretch 4, F
        elif 'PF' in role or 'SF' in role or 'WING F' in role or 'STRETCH' in role or (role == 'F'):
            return 'F'
        # Center: C
        elif role == 'C':
            return 'C'
        else:
            return None

    df['Role'] = df[pos_col].apply(standardize_role)
    df = df[df['Role'].notna()]

    print(f"\nRole distribution:")
    print(df['Role'].value_counts())

    # Keep unique players with their role
    df = df[['Player', 'player_lower', 'Role']
            ].drop_duplicates(subset='player_lower')

    print(f"\nUnique players with roles: {len(df)}")

# Save
output_file = 'temp_data/sports_reference_positions.csv'
df.to_csv(output_file, index=False)
print(f"\n✅ Saved to {output_file}")
