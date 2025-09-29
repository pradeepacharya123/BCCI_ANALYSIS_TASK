import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database_tables():
    """Create all necessary tables in Neon PostgreSQL database"""
    
    # Get database connection string from environment variable
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Please add your Neon database connection string to .env file")
        return
    
    try:
        # Connect to Neon PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to Neon Database successfully")
        
        # 1. Create Players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id SERIAL PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created 'players' table")
        
        # 2. Create Formats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS formats (
                format_id SERIAL PRIMARY KEY,
                format_name VARCHAR(20) NOT NULL UNIQUE
            );
        """)
        print("✅ Created 'formats' table")
        
        # 3. Create Batting Statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batting_stats (
                batting_id SERIAL PRIMARY KEY,
                player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
                format_id INTEGER REFERENCES formats(format_id) ON DELETE CASCADE,
                rank INTEGER,
                matches INTEGER,
                innings INTEGER,
                runs INTEGER,
                average DECIMAL(6,2),
                strike_rate DECIMAL(6,2),
                highest_score INTEGER,
                fours INTEGER,
                sixes INTEGER,
                fifties INTEGER,
                hundreds INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_id, format_id)
            );
        """)
        print("✅ Created 'batting_stats' table")
        
        # 4. Create Bowling Statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bowling_stats (
                bowling_id SERIAL PRIMARY KEY,
                player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
                format_id INTEGER REFERENCES formats(format_id) ON DELETE CASCADE,
                rank INTEGER,
                matches INTEGER,
                innings INTEGER,
                wickets INTEGER,
                average DECIMAL(6,2),
                economy DECIMAL(6,2),
                strike_rate DECIMAL(6,2),
                bowling_figure DECIMAL(6,3),
                runs INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_id, format_id)
            );
        """)
        print("✅ Created 'bowling_stats' table")
        
        # 5. Insert default formats (Test and ODI)
        cursor.execute("""
            INSERT INTO formats (format_name) VALUES 
            ('Test'), ('ODI')
            ON CONFLICT (format_name) DO NOTHING;
        """)
        print("✅ Inserted default formats: Test and ODI")
        
        # Commit changes
        conn.commit()
        print("🎉 All tables created successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("\n📊 Database Tables Created:")
        for table in tables:
            print(f"   - {table[0]}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        # Close connection
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("🔒 Database connection closed")

def verify_tables():
    """Verify that tables are created and check their structure"""
    
    database_url = os.getenv('DATABASE_URL')
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("\n🔍 Verifying table structures...")
        
        # Check players table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'players' 
            ORDER BY ordinal_position;
        """)
        print("\n📋 Players Table Structure:")
        for col in cursor.fetchall():
            print(f"   - {col[0]}: {col[1]}")
        
        # Check formats table
        cursor.execute("SELECT format_id, format_name FROM formats ORDER BY format_id;")
        formats = cursor.fetchall()
        print("\n🏏 Available Formats:")
        for fmt in formats:
            print(f"   - {fmt[0]}: {fmt[1]}")
            
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting Neon Database Table Creation...")
    create_database_tables()
    verify_tables()