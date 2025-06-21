import csv

def filter_players_by_year(file_path, year_threshold):
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        filtered_players = [row for row in reader if int(row['FROM_YEAR']) >= year_threshold]
    return filtered_players

def main():
    file_path = 'nba_players.csv'
    year_threshold = 1980
    filtered_players = filter_players_by_year(file_path, year_threshold)
    
    output_file_path = 'filtered_nba_players.csv'
    if filtered_players:
        with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=filtered_players[0].keys())
            writer.writeheader()
            writer.writerows(filtered_players)
        print(f"Filtered data saved to: {output_file_path}")
    else:
        print("No players matched the filter criteria.")

if __name__ == "__main__":
    main()

    
    