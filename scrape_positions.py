import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re


def get_player_position(player_name):
    """Scrape position from Sports Reference for a given player."""
    # Convert player name to URL format (lowercase, replace spaces with hyphens)
    # Remove special characters
    clean_name = re.sub(r"[^a-zA-Z\s-]", "", player_name.lower())
    # Replace spaces with hyphens
    url_name = clean_name.replace(" ", "-")

    # Try different URL patterns (some players have -1, -2, etc.)
    for suffix in ["", "-1", "-2", "-3"]:
        url = f"https://www.sports-reference.com/cbb/players/{url_name}{suffix}.html"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find position in the meta info
                meta_div = soup.find('div', {'id': 'meta'})
                if meta_div:
                    # Look for position in the text
                    text = meta_div.get_text()

                    # Position is typically listed as "Position: G" or similar
                    pos_match = re.search(
                        r'Position:\s*([A-Z]+(?:-[A-Z]+)?)', text)
                    if pos_match:
                        return pos_match.group(1)

        except Exception as e:
            print(f"Error fetching {player_name} ({url}): {e}")
            continue

    return None


def standardize_position(position):
    """Standardize position to G, F, or C based on user's rules."""
    if not position or pd.isna(position):
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


def main():
    print("Loading all_assisted.csv...")
    df = pd.read_csv('temp_data/all_assisted.csv')
    print(f"Total players: {len(df)}")

    # Add Role_final column if it doesn't exist
    if 'Role_final' not in df.columns:
        df['Role_final'] = None

    # Process players in batches
    save_interval = 50  # Save every 50 players in case of crash

    for i, row in df.iterrows():
        if pd.notna(row.get('Role_final')):
            continue  # Skip if already has position

        player_name = row['Player']

        print(f"[{i+1}/{len(df)}] Fetching position for {player_name}...")

        position = get_player_position(player_name)
        standardized = standardize_position(position)

        if standardized:
            df.at[i, 'Role_final'] = standardized
            print(f"  → Found: {position} → {standardized}")
        else:
            print(f"  → Not found or invalid position")

        # Save progress periodically every 50 players
        if (i + 1) % save_interval == 0:
            print(f"\n💾 Saving progress at {i+1} players...")
            df.to_csv('temp_data/all_assisted.csv', index=False)
            print("Saved!\n")

        # Be nice to the server
        time.sleep(1)

    # Final save
    print("\nSaving final results...")
    df.to_csv('temp_data/all_assisted.csv', index=False)

    print(f"\nComplete!")
    print(f"Players with positions: {df['Role_final'].notna().sum()}")
    print(f"Players without positions: {df['Role_final'].isna().sum()}")


if __name__ == "__main__":
    main()
