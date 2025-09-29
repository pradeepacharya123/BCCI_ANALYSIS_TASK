import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os

# Create csv_files folder if it doesn't exist
if not os.path.exists('csv_files'):
    os.makedirs('csv_files')

urls = {
    "test": "https://www.bcci.tv/international/men/stats/test",
    "odi": "https://www.bcci.tv/international/men/stats/odi"
}

column_names = [
    "Rank", "Player", "Matches", "Innings", "Average", "Strike Rate",
    "Highest Score", "4s", "6s", "50s", "100s", "Runs"
]

def clean_int(val):
    # Remove non-digit characters and convert to int, else return None
    val = val.replace(',', '').split()[0]
    return int(val) if val.isdigit() else None

def clean_float(val):
    try:
        return float(val.split()[0])
    except:
        return None

for name, url in urls.items():
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    main_player_div = soup.find("div", class_="team-ranking-wrapper player")
    main_row = []
    if main_player_div:
        player_name_div = main_player_div.find("div", class_="player-name-trw")
        first_name = player_name_div.find("p").get_text(strip=True) if player_name_div else ""
        last_name = player_name_div.find("span").get_text(strip=True) if player_name_div else ""
        full_name = f"{first_name} {last_name}".strip()
        stats_table = main_player_div.find("table")
        stats = []
        if stats_table:
            for td in stats_table.find_all("td"):
                stat_value = td.find("p").get_text(strip=True) if td.find("p") else ""
                stats.append(stat_value)
        main_row = ["1", full_name] + stats

    table_div = soup.find("div", class_="stats-data-table-player")
    if not table_div:
        print(f"No data table found for {name}")
        continue
    table = table_div.find("table")
    rows = table.find_all("tr")
    data = []
    if main_row:
        data.append(main_row)
    for row in rows:
        cols = row.find_all("td")
        row_data = []
        for col in cols:
            val = col.find("h6") or col.find("p")
            text = val.get_text(strip=True) if val else col.get_text(strip=True)
            row_data.append(text)

        if row_data:
            data.append(row_data)
    # Convert data types
    df = pd.DataFrame(data, columns=column_names)
    # Convert columns to appropriate types
    for col in ["Rank", "Matches", "Innings","Highest Score","4s", "6s", "50s", "100s", "Runs"]:
        df[col] = df[col].apply(lambda x: clean_int(str(x)) if pd.notnull(x) else None)
    for col in ["Average", "Strike Rate"]:
        df[col] = df[col].apply(lambda x: clean_float(str(x)) if pd.notnull(x) else None)
    
    # Replace NaN values with 0 for all numeric columns
    numeric_columns = ["Rank", "Matches", "Innings", "Average", "Strike Rate", 
                      "Highest Score", "4s", "6s", "50s", "100s", "Runs"]
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Save to csv_files folder
    filename = f"csv_files/batting_most_runs_{name}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {filename}")