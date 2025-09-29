import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Create csv_files folder if it doesn't exist
if not os.path.exists('csv_files'):
    os.makedirs('csv_files')

def scrape_bowling_stats(format_name, url):
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 20)

    driver.get(url)

    # Click "Bowling Records" tab
    bowling_tab = wait.until(EC.element_to_be_clickable((By.ID, "bowling-records")))
    driver.execute_script("arguments[0].click();", bowling_tab)
    time.sleep(2)

    # Click "Most wickets" inside Bowling menu
    most_wickets_tab = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "ul#bba-bowling li a[data-slug='bowling_top_wicket_takers']"))
    )
    driver.execute_script("arguments[0].click();", most_wickets_tab)
    time.sleep(3)

    # Scrape the top player's stats (main highlighted player)
    data = []
    
    try:
        main_player_div = driver.find_element(By.CSS_SELECTOR, "div.team-ranking-wrapper.player")
        player_name = main_player_div.find_element(By.CSS_SELECTOR, "div.player-name-trw p").text.strip()
        last_name_span = main_player_div.find_element(By.CSS_SELECTOR, "div.player-name-trw span").text.strip()
        full_name = f"{player_name} {last_name_span}".strip()

        # Extract stats from main player table
        stats_table = main_player_div.find_element(By.TAG_NAME, "table")
        stats_cells = stats_table.find_elements(By.TAG_NAME, "td")
        
        # For main player, extract the numeric values
        stats = []
        for cell in stats_cells:
            p_tags = cell.find_elements(By.TAG_NAME, "p")
            if p_tags and p_tags[0].text.strip():
                stats.append(p_tags[0].text.strip())
            else:
                stats.append(cell.text.strip().split('\n')[0] if '\n' in cell.text else cell.text.strip())
        
        # Create row for main player
        main_player_row = ["1", full_name] + stats
        data.append(main_player_row)
    except Exception as e:
        print(f"⚠️ Could not find main player: {e}")

    # Scrape all other rows from the table
    try:
        table_container = driver.find_element(By.CSS_SELECTOR, "div.stats-data-table-player")
        table = table_container.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            row_data = []
            
            for j, col in enumerate(cols):
                if j == 0:  # Rank column
                    row_data.append(col.text.strip())
                elif j == 1:  # Player name column
                    name_parts = []
                    h6_elements = col.find_elements(By.TAG_NAME, "h6")
                    span_elements = col.find_elements(By.TAG_NAME, "span")
                    
                    for elem in h6_elements + span_elements:
                        if elem.text.strip():
                            name_parts.append(elem.text.strip())
                    
                    if name_parts:
                        row_data.append(" ".join(name_parts))
                    else:
                        row_data.append(col.text.strip())
                else:
                    h6_elements = col.find_elements(By.TAG_NAME, "h6")
                    if h6_elements and h6_elements[0].text.strip():
                        row_data.append(h6_elements[0].text.strip())
                    else:
                        lines = col.text.strip().split('\n')
                        row_data.append(lines[0] if lines else col.text.strip())
            
            if row_data and len(row_data) >= 3:
                data.append(row_data)
    except Exception as e:
        print(f"⚠️ Could not find table rows: {e}")

    # Define column names
    column_names = [
        "Rank", 
        "Player", 
        "Matches", 
        "Innings", 
        "Wickets", 
        "Average", 
        "Bowling_Figure", 
        "Economy", 
        "Strike_Rate", 
        "Runs"
    ]

    if data:
        # Create DataFrame
        df = pd.DataFrame(data, columns=column_names)
        
        # Convert fractions in Bowling_Figure to decimal
        def convert_fraction_to_decimal(value):
            if pd.isna(value):
                return value
            value_str = str(value).strip()
            if '/' in value_str:
                try:
                    parts = value_str.split('/')
                    if len(parts) == 2:
                        numerator = float(parts[0])
                        denominator = float(parts[1])
                        return round(numerator / denominator, 3) if denominator != 0 else numerator
                except:
                    pass
            try:
                return float(value_str)
            except:
                return value
        
        # Replace Bowling_Figure column with decimal values
        df['Bowling_Figure'] = df['Bowling_Figure'].apply(convert_fraction_to_decimal)
        
        # Clean data types
        numeric_columns = ["Rank", "Matches", "Innings", "Wickets", "Runs"]
        float_columns = ["Average", "Economy", "Strike_Rate", "Bowling_Figure"]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        
        for col in float_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows where all numeric columns are empty
        numeric_cols_to_check = [col for col in numeric_columns + float_columns if col in df.columns]
        df = df.dropna(subset=numeric_cols_to_check, how='all')
        
        # Save to csv_files folder
        filename = f"csv_files/bowling_most_wickets_{format_name.lower()}.csv"
        df.to_csv(filename, index=False)
        print(f"✅ Saved {len(df)} rows to {filename}")
    else:
        print("⚠️ No data scraped!")

    driver.quit()

if __name__ == "__main__":
    formats = {
        "ODI": "https://www.bcci.tv/international/men/stats/odi",
        "Test": "https://www.bcci.tv/international/men/stats/test",
    }

    for fmt, url in formats.items():
        scrape_bowling_stats(fmt, url)
        time.sleep(2)