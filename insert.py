import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DataInserter:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to Neon PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor()
            print("✅ Connected to database successfully")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔒 Database connection closed")
    
    def check_csv_files(self):
        """Check if CSV files exist and show their structure"""
        csv_files = [
            'csv_files/batting_most_runs_test.csv',
            'csv_files/batting_most_runs_odi.csv', 
            'csv_files/bowling_most_wickets_test.csv',
            'csv_files/bowling_most_wickets_odi.csv'
        ]
        
        print("\n🔍 Checking CSV files...")
        for file in csv_files:
            if os.path.exists(file):
                df = pd.read_csv(file)
                print(f"✅ {file}: {len(df)} rows, columns: {list(df.columns)}")
            else:
                print(f"❌ {file}: File not found")
    
    def get_format_id(self, format_name):
        """Get format_id for given format name - fixed to handle case sensitivity"""
        # Map lowercase input to proper case
        format_mapping = {
            'test': 'Test',
            'odi': 'ODI'
        }
        
        proper_format_name = format_mapping.get(format_name.lower(), format_name)
        self.cursor.execute("SELECT format_id FROM formats WHERE format_name = %s", (proper_format_name,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        else:
            print(f"⚠️  Format '{format_name}' not found in database. Available formats:")
            self.cursor.execute("SELECT format_name FROM formats")
            available_formats = self.cursor.fetchall()
            for fmt in available_formats:
                print(f"   - {fmt[0]}")
            return None
    
    def insert_player(self, player_name):
        """Insert player and return player_id"""
        try:
            # Clean player name
            player_name = str(player_name).strip()
            if not player_name or player_name == 'nan' or player_name == '0':
                return None
                
            # First check if player exists
            self.cursor.execute("SELECT player_id FROM players WHERE full_name = %s", (player_name,))
            existing_player = self.cursor.fetchone()
            
            if existing_player:
                return existing_player[0]
            else:
                # Insert new player
                self.cursor.execute(
                    "INSERT INTO players (full_name) VALUES (%s) RETURNING player_id",
                    (player_name,)
                )
                result = self.cursor.fetchone()
                player_id = result[0] if result else None
                return player_id
                
        except Exception as e:
            print(f"❌ Failed to insert player {player_name}: {e}")
            self.conn.rollback()
            return None
    
    def clean_numeric_value(self, value, default=0):
        """Clean numeric values, handle NaN and convert to appropriate type"""
        if pd.isna(value) or value == '' or value == 'nan':
            return default
        try:
            # Remove commas and convert to appropriate type
            cleaned = str(value).replace(',', '').strip()
            if cleaned == '':
                return default
            return float(cleaned) if '.' in cleaned else int(float(cleaned))
        except:
            return default
    
    def load_batting_data(self, format_name):
        """Load batting data from CSV files with exact column mapping"""
        try:
            filename = f"csv_files/batting_most_runs_{format_name.lower()}.csv"
            
            if not os.path.exists(filename):
                print(f"❌ CSV file not found: {filename}")
                return
            
            df = pd.read_csv(filename)
            format_id = self.get_format_id(format_name)
            
            if not format_id:
                print(f"❌ Cannot load data - format not found: {format_name}")
                return
            
            print(f"\n📥 Loading {format_name.upper()} batting data...")
            print(f"   Found {len(df)} records in CSV")
            
            records_loaded = 0
            skipped_players = 0
            
            for index, row in df.iterrows():
                player_name = str(row['Player']).strip()
                
                # Skip if player name is invalid
                if not player_name or player_name == 'nan' or player_name == '0':
                    skipped_players += 1
                    continue
                
                player_id = self.insert_player(player_name)
                
                if player_id:
                    # Clean and prepare all values
                    rank = self.clean_numeric_value(row['Rank'])
                    matches = self.clean_numeric_value(row['Matches'])
                    innings = self.clean_numeric_value(row['Innings'])
                    runs = self.clean_numeric_value(row['Runs'])
                    average = self.clean_numeric_value(row['Average'], 0.0)
                    strike_rate = self.clean_numeric_value(row['Strike Rate'], 0.0)
                    highest_score = self.clean_numeric_value(row['Highest Score'])
                    fours = self.clean_numeric_value(row['4s'])
                    sixes = self.clean_numeric_value(row['6s'])
                    fifties = self.clean_numeric_value(row['50s'])
                    hundreds = self.clean_numeric_value(row['100s'])
                    
                    # Insert batting stats with exact column names
                    self.cursor.execute("""
                        INSERT INTO batting_stats 
                        (player_id, format_id, rank, matches, innings, runs, average, 
                         strike_rate, highest_score, fours, sixes, fifties, hundreds)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (player_id, format_id) DO UPDATE SET
                        rank = EXCLUDED.rank,
                        matches = EXCLUDED.matches,
                        innings = EXCLUDED.innings,
                        runs = EXCLUDED.runs,
                        average = EXCLUDED.average,
                        strike_rate = EXCLUDED.strike_rate,
                        highest_score = EXCLUDED.highest_score,
                        fours = EXCLUDED.fours,
                        sixes = EXCLUDED.sixes,
                        fifties = EXCLUDED.fifties,
                        hundreds = EXCLUDED.hundreds
                    """, (
                        player_id, format_id, rank, matches, innings, runs, 
                        average, strike_rate, highest_score, fours, sixes, 
                        fifties, hundreds
                    ))
                    records_loaded += 1
            
            self.conn.commit()
            print(f"   ✅ Successfully loaded: {records_loaded} records")
            if skipped_players > 0:
                print(f"   ⚠️  Skipped: {skipped_players} invalid player names")
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Failed to load {format_name} batting data: {e}")
            import traceback
            traceback.print_exc()
    
    def load_bowling_data(self, format_name):
        """Load bowling data from CSV files with exact column mapping"""
        try:
            filename = f"csv_files/bowling_most_wickets_{format_name.lower()}.csv"
            
            if not os.path.exists(filename):
                print(f"❌ CSV file not found: {filename}")
                return
            
            df = pd.read_csv(filename)
            format_id = self.get_format_id(format_name)
            
            if not format_id:
                print(f"❌ Cannot load data - format not found: {format_name}")
                return
            
            print(f"\n📥 Loading {format_name.upper()} bowling data...")
            print(f"   Found {len(df)} records in CSV")
            
            records_loaded = 0
            skipped_players = 0
            
            for index, row in df.iterrows():
                player_name = str(row['Player']).strip()
                
                # Skip if player name is invalid
                if not player_name or player_name == 'nan' or player_name == '0':
                    skipped_players += 1
                    continue
                
                player_id = self.insert_player(player_name)
                
                if player_id:
                    # Clean and prepare all values
                    rank = self.clean_numeric_value(row['Rank'])
                    matches = self.clean_numeric_value(row['Matches'])
                    innings = self.clean_numeric_value(row['Innings'])
                    wickets = self.clean_numeric_value(row['Wickets'])
                    average = self.clean_numeric_value(row['Average'], 0.0)
                    economy = self.clean_numeric_value(row['Economy'], 0.0)
                    strike_rate = self.clean_numeric_value(row['Strike_Rate'], 0.0)
                    bowling_figure = self.clean_numeric_value(row['Bowling_Figure'], 0.0)
                    runs = self.clean_numeric_value(row['Runs'])
                    
                    # Insert bowling stats with exact column names
                    self.cursor.execute("""
                        INSERT INTO bowling_stats 
                        (player_id, format_id, rank, matches, innings, wickets, average, 
                         economy, strike_rate, bowling_figure, runs)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (player_id, format_id) DO UPDATE SET
                        rank = EXCLUDED.rank,
                        matches = EXCLUDED.matches,
                        innings = EXCLUDED.innings,
                        wickets = EXCLUDED.wickets,
                        average = EXCLUDED.average,
                        economy = EXCLUDED.economy,
                        strike_rate = EXCLUDED.strike_rate,
                        bowling_figure = EXCLUDED.bowling_figure,
                        runs = EXCLUDED.runs
                    """, (
                        player_id, format_id, rank, matches, innings, wickets,
                        average, economy, strike_rate, bowling_figure, runs
                    ))
                    records_loaded += 1
            
            self.conn.commit()
            print(f"   ✅ Successfully loaded: {records_loaded} records")
            if skipped_players > 0:
                print(f"   ⚠️  Skipped: {skipped_players} invalid player names")
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Failed to load {format_name} bowling data: {e}")
            import traceback
            traceback.print_exc()
    
    def verify_data_loaded(self):
        """Verify that data has been loaded successfully"""
        try:
            print("\n" + "="*50)
            print("🔍 VERIFICATION REPORT")
            print("="*50)
            
            # Check players count
            self.cursor.execute("SELECT COUNT(*) FROM players")
            player_count = self.cursor.fetchone()[0]
            print(f"📊 Total players in database: {player_count}")
            
            # Check batting stats count by format
            self.cursor.execute("""
                SELECT f.format_name, COUNT(*) 
                FROM batting_stats bs
                JOIN formats f ON bs.format_id = f.format_id
                GROUP BY f.format_name
                ORDER BY f.format_name
            """)
            batting_counts = self.cursor.fetchall()
            print("\n🏏 BATTING RECORDS:")
            for format_name, count in batting_counts:
                print(f"   {format_name}: {count} records")
            
            # Check bowling stats count by format
            self.cursor.execute("""
                SELECT f.format_name, COUNT(*) 
                FROM bowling_stats bws
                JOIN formats f ON bws.format_id = f.format_id
                GROUP BY f.format_name
                ORDER BY f.format_name
            """)
            bowling_counts = self.cursor.fetchall()
            print("\n🎯 BOWLING RECORDS:")
            for format_name, count in bowling_counts:
                print(f"   {format_name}: {count} records")
            
            # Show sample data
            print("\n👥 SAMPLE PLAYERS (first 5):")
            self.cursor.execute("SELECT full_name FROM players ORDER BY player_id LIMIT 5")
            sample_players = self.cursor.fetchall()
            for player in sample_players:
                print(f"   - {player[0]}")
                
            print("\n📈 SAMPLE BATTING STATS (Top run-scorers):")
            self.cursor.execute("""
                SELECT p.full_name, f.format_name, bs.runs, bs.average, bs.matches
                FROM batting_stats bs
                JOIN players p ON bs.player_id = p.player_id
                JOIN formats f ON bs.format_id = f.format_id
                ORDER BY bs.runs DESC
                LIMIT 5
            """)
            sample_batting = self.cursor.fetchall()
            for player, format_name, runs, average, matches in sample_batting:
                print(f"   - {player} ({format_name}): {runs} runs, {matches} matches, Avg: {average}")
                
            print("\n🎯 SAMPLE BOWLING STATS (Top wicket-takers):")
            self.cursor.execute("""
                SELECT p.full_name, f.format_name, bws.wickets, bws.average, bws.matches
                FROM bowling_stats bws
                JOIN players p ON bws.player_id = p.player_id
                JOIN formats f ON bws.format_id = f.format_id
                ORDER BY bws.wickets DESC
                LIMIT 5
            """)
            sample_bowling = self.cursor.fetchall()
            for player, format_name, wickets, average, matches in sample_bowling:
                print(f"   - {player} ({format_name}): {wickets} wickets, {matches} matches, Avg: {average}")
                
        except Exception as e:
            print(f"❌ Error verifying data: {e}")

def main():
    inserter = DataInserter()
    
    try:
        # Connect to database
        inserter.connect()
        
        # First check CSV files
        inserter.check_csv_files()
        
        # Load data for both formats
        formats = ['test', 'odi']  # Use lowercase for file names
        
        for format_name in formats:
            inserter.load_batting_data(format_name)
            inserter.load_bowling_data(format_name)
        
        # Verify data loaded
        inserter.verify_data_loaded()
        
        print("\n🎉 DATA INSERTION COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()
    finally:
        inserter.close()

if __name__ == "__main__":
    print("🚀 Starting Data Insertion into Neon Database...")
    print("📝 Fixed format name matching...")
    main()