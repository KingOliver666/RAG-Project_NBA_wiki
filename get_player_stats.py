import pandas as pd
import requests
import time

# Step 1: Add NBA keyword check
def is_nba_related(text):
    nba_keywords = [
        "NBA", "National Basketball Association", "basketball player",
        "points per game", "rebounds", "assists", "shooting guard",
        "power forward", "center", "rookie season", "drafted"
    ]
    return any(keyword.lower() in text.lower() for keyword in nba_keywords)

# Step 2: Wikipedia full text fetcher with retry
def get_wikipedia_full_text(player_name):
    for title_variant in [player_name, f"{player_name} (basketball)"]:
        title = title_variant.replace(" ", "_")
        url = "https://en.wikipedia.org/w/api.php"
        try:
            params = {
                "action": "query",
                "prop": "extracts",
                "explaintext": True,
                "redirects": True,
                "titles": title,
                "format": "json",
                "exlimit": 1,
            }
            response = requests.get(url, params=params, timeout=10)
            pages = response.json()["query"]["pages"]
            page = next(iter(pages.values()))
            extract = page.get("extract", "")
            if extract and is_nba_related(extract):
                return extract
        except Exception as e:
            print(f"❌ Failed to fetch {title_variant}: {e}")
    return ""

# Step 3: Stats fetcher stays unchanged
def get_stat_sentences(player_name):
    def summarize_stat_row(row, player_name):
        year = row.get("Year", "Unknown Year")
        team = row.get("Team", "an unknown team")
        gp = row.get("GP", "?")
        mpg = row.get("MPG", "?")
        fg = row.get("FG%", "?")
        fg3 = row.get("3P%", "?")
        ft = row.get("FT%", "?")
        ppg = row.get("PPG", "?")
        rpg = row.get("RPG", "?")
        apg = row.get("APG", "?")
        spg = row.get("SPG", "?")
        bpg = row.get("BPG", "?")

        return (
            f"In the {year} season, {player_name} played for {team} in {gp} games. "
            f"He averaged {ppg} points, {rpg} rebounds, {apg} assists, "
            f"{spg} steals, and {bpg} blocks per game. "
            f"He shot {fg} from the field, {fg3} from 3-point range, and {ft} from the free throw line, "
            f"playing an average of {mpg} minutes per game."
        )

    # Try standard and disambiguated Wikipedia titles
    for title_variant in [player_name, f"{player_name} (basketball)"]:
        title = title_variant.replace(" ", "_")
        url = f"https://en.wikipedia.org/wiki/{title}"

        try:
            tables = pd.read_html(url)
        except:
            continue  # if page/table fails, skip

        stat_keywords = {"Year", "PPG", "RPG", "APG", "FG%", "GP", "MPG", "3P%", "FT%", "Team", "SPG", "BPG"}
        stat_sentences = []

        for table in tables:
            columns = set(str(col) for col in table.columns)
            if stat_keywords <= columns:  # must contain all desired columns
                for _, row in table.iterrows():
                    try:
                        sentence = summarize_stat_row(row, player_name)
                        stat_sentences.append(sentence)
                    except:
                        continue

        if stat_sentences:
            return "\n".join(stat_sentences)

    return ""

# Step 4: Main logic with filter
def main():
    try:
        df = pd.read_csv("filtered_nba_players.csv", dtype=str)
    except FileNotFoundError:
        print("❌ File not found. Make sure 'filtered_nba_players.csv' is in the same folder.")
        return

    player_data = []

    for i, name in enumerate(df["DISPLAY_FIRST_LAST"].dropna().unique()):
        print(f"[{i+1}] Processing {name}")
        wiki_text = get_wikipedia_full_text(name)
        if not wiki_text:
            print(f"❌ Skipping {name}: not a valid NBA player article.")
            continue
        stats_text = get_stat_sentences(name)
        player_data.append({
            "player": name,
            "wiki_text": wiki_text,
            "stats_text": stats_text
        })
        time.sleep(0.1)  # polite delay

    output_df = pd.DataFrame(player_data)
    output_df.to_csv("player_text_and_stats_columns.csv", index=False)
    print("✅ Final dataset saved to 'player_text_and_stats_columns.csv'")

main()
