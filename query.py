import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ Connect to YOUR actual Neon DB from .env file
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("🏏 CRICKET STATISTICS ANALYSIS - FINAL RESULTS")
print("=" * 60)

# 🔎 1. Search Functionality
print("\n1. PLAYERS WHOSE NAMES START WITH 'V'")
print("-" * 40)
cur.execute("SELECT DISTINCT full_name FROM players WHERE full_name LIKE 'V%' ORDER BY full_name;")
players_v = cur.fetchall()
for player in players_v:
    print(f"  • {player[0]}")

print("\n2. SEARCH PLAYER - Virat Kohli")
print("-" * 40)
cur.execute("""
    SELECT DISTINCT p.full_name, f.format_name, bs.runs, bs.matches
    FROM players p
    JOIN batting_stats bs ON p.player_id = bs.player_id
    JOIN formats f ON bs.format_id = f.format_id
    WHERE p.full_name LIKE '%Virat%' OR p.full_name LIKE '%Kohli%'
    ORDER BY f.format_name;
""")
virat_data = cur.fetchall()
for row in virat_data:
    print(f"  • {row[1]}: {row[2]} runs, {row[3]} matches")

# 📊 2. Match Records
print("\n3. PLAYER WITH HIGHEST NUMBER OF MATCHES")
print("-" * 40)
cur.execute("""
    SELECT p.full_name, bs.matches 
    FROM batting_stats bs
    JOIN players p ON p.player_id = bs.player_id
    ORDER BY bs.matches DESC
    LIMIT 1;
""")
highest = cur.fetchone()
print(f"  • {highest[0]} - {highest[1]} matches")

print("\n4. PLAYER WITH LOWEST NUMBER OF MATCHES (at least 1)")
print("-" * 40)
cur.execute("""
    SELECT p.full_name, bs.matches 
    FROM batting_stats bs
    JOIN players p ON p.player_id = bs.player_id
    WHERE bs.matches > 0
    ORDER BY bs.matches ASC
    LIMIT 1;
""")
lowest = cur.fetchone()
print(f"  • {lowest[0]} - {lowest[1]} match")

# 🏏 3. Performance Insights
print("\n5. TOP 5 BEST BATSMEN (BY RUNS)")
print("-" * 40)
cur.execute("""
    SELECT DISTINCT p.full_name, bs.runs, bs.matches, f.format_name
    FROM batting_stats bs
    JOIN players p ON p.player_id = bs.player_id
    JOIN formats f ON bs.format_id = f.format_id
    ORDER BY bs.runs DESC
    LIMIT 5;
""")
top_batsmen = cur.fetchall()
for i, batsman in enumerate(top_batsmen, 1):
    print(f"  {i}. {batsman[0]} - {batsman[1]} runs ({batsman[3]})")

print("\n6. TOP 5 BOWLERS (BY MATCHES - ACTUAL BOWLERS)")
print("-" * 40)
cur.execute("""
    SELECT DISTINCT p.full_name, bws.matches, f.format_name
    FROM bowling_stats bws
    JOIN players p ON p.player_id = bws.player_id
    JOIN formats f ON bws.format_id = f.format_id
    WHERE bws.matches > 0
    ORDER BY bws.matches DESC
    LIMIT 5;
""")
top_bowlers = cur.fetchall()
for i, bowler in enumerate(top_bowlers, 1):
    print(f"  {i}. {bowler[0]} - {bowler[1]} matches ({bowler[2]})")

print("\n7. MOST AGGRESSIVE BATSMAN (HIGHEST STRIKE RATE)")
print("-" * 40)
try:
    cur.execute("""
        SELECT DISTINCT p.full_name, bs.strike_rate, bs.runs, bs.matches, f.format_name
        FROM batting_stats bs
        JOIN players p ON p.player_id = bs.player_id
        JOIN formats f ON bs.format_id = f.format_id
        WHERE bs.matches >= 10 AND bs.strike_rate IS NOT NULL AND bs.strike_rate > 0
        ORDER BY bs.strike_rate DESC
        LIMIT 1;
    """)
    aggressive = cur.fetchone()
    if aggressive:
        print(f"  • {aggressive[0]} - Strike Rate: {aggressive[1]}")
        print(f"    {aggressive[3]} matches, {aggressive[2]} runs ({aggressive[4]})")
    else:
        # Fallback: show batsman with most runs if strike rate not available
        cur.execute("""
            SELECT DISTINCT p.full_name, bs.runs, bs.matches, f.format_name
            FROM batting_stats bs
            JOIN players p ON p.player_id = bs.player_id
            JOIN formats f ON bs.format_id = f.format_id
            WHERE bs.runs > 0
            ORDER BY bs.runs DESC
            LIMIT 1;
        """)
        aggressive = cur.fetchone()
        print(f"  • {aggressive[0]} - {aggressive[1]} runs ({aggressive[3]})")
        print("    (Strike rate data not available)")
except Exception as e:
    print(f"  • Error fetching strike rate data: {e}")

print("\n8. ALL-ROUNDERS (Players with both batting and bowling records)")
print("-" * 40)
cur.execute("""
    SELECT DISTINCT p.full_name
    FROM players p
    JOIN batting_stats bs ON p.player_id = bs.player_id
    JOIN bowling_stats bws ON p.player_id = bws.player_id
    WHERE p.full_name != '' AND p.full_name IS NOT NULL
    ORDER BY p.full_name
    LIMIT 15;
""")
all_rounders = cur.fetchall()
if all_rounders:
    print("  Players with both batting and bowling records:")
    for player in all_rounders:
        if player[0] and player[0] != '-':  # Filter out empty names
            print(f"  • {player[0]}")
else:
    print("  • No players found with both batting and bowling records")

# ⚔️ 4. Custom Player Comparisons
print("\n9. ROHIT vs VIRAT - MATCHES COMPARISON")
print("-" * 40)
cur.execute("""
    SELECT 
        (SELECT bs.matches FROM batting_stats bs JOIN players p ON p.player_id = bs.player_id 
         WHERE (p.full_name LIKE '%Rohit%' OR p.full_name LIKE '%Sharma%') AND bs.format_id = 2 LIMIT 1) as rohit_odi,
        (SELECT bs.matches FROM batting_stats bs JOIN players p ON p.player_id = bs.player_id 
         WHERE (p.full_name LIKE '%Virat%' OR p.full_name LIKE '%Kohli%') AND bs.format_id = 2 LIMIT 1) as virat_odi,
        (SELECT bs.matches FROM batting_stats bs JOIN players p ON p.player_id = bs.player_id 
         WHERE (p.full_name LIKE '%Virat%' OR p.full_name LIKE '%Kohli%') AND bs.format_id = 2 LIMIT 1) - 
        (SELECT bs.matches FROM batting_stats bs JOIN players p ON p.player_id = bs.player_id 
         WHERE (p.full_name LIKE '%Rohit%' OR p.full_name LIKE '%Sharma%') AND bs.format_id = 2 LIMIT 1) as matches_needed;
""")
comparison = cur.fetchone()
if comparison[0] and comparison[1]:
    print(f"  • Rohit Sharma: {comparison[0]} ODI matches")
    print(f"  • Virat Kohli: {comparison[1]} ODI matches") 
    print(f"  • Rohit needs {comparison[2]} more matches to surpass Virat")
else:
    print("  • Could not find match data for Rohit or Virat")

print("\n10. HARBHAJAN SINGH - MATCHES TO REACH 5TH POSITION")
print("-" * 40)
cur.execute("""
    WITH top_players AS (
        SELECT DISTINCT p.full_name, bs.matches
        FROM batting_stats bs
        JOIN players p ON p.player_id = bs.player_id
        ORDER BY bs.matches DESC
        LIMIT 5
    )
    SELECT 
        (SELECT matches FROM top_players ORDER BY matches ASC LIMIT 1) as fifth_position,
        (SELECT bs.matches FROM batting_stats bs JOIN players p ON p.player_id = bs.player_id 
         WHERE p.full_name LIKE '%Harbhajan%' LIMIT 1) as harbhajan_current,
        (SELECT matches FROM top_players ORDER BY matches ASC LIMIT 1) - 
        (SELECT bs.matches FROM batting_stats bs JOIN players p ON p.player_id = bs.player_id 
         WHERE p.full_name LIKE '%Harbhajan%' LIMIT 1) as matches_needed;
""")
harbhajan_data = cur.fetchone()
if harbhajan_data[0] and harbhajan_data[1]:
    print(f"  • 5th position: {harbhajan_data[0]} matches")
    print(f"  • Harbhajan Singh: {harbhajan_data[1]} matches")
    print(f"  • Matches needed: {harbhajan_data[2]}")
else:
    print("  • Could not find match data for Harbhajan Singh")

print("\n" + "=" * 60)
print("📊 ANALYSIS COMPLETE!")
print("=" * 60)

cur.close()
conn.close()