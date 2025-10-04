import sqlite3
import os

def migrate_database():
    """Safely migrate the database to add group_name field without losing data"""
    
    db_path = 'soccer_championship.db'
    
    if not os.path.exists(db_path):
        print("Database doesn't exist yet. Creating new one...")
        return
    
    print("Starting database migration...")
    
    # Connect to existing database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if group_name column already exists
        cursor.execute("PRAGMA table_info(teams)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'group_name' not in columns:
            print("Adding group_name column to teams table...")
            
            # Add the new column with a default value
            cursor.execute("ALTER TABLE teams ADD COLUMN group_name VARCHAR(10)")
            
            # Update existing teams to have a default group
            cursor.execute("UPDATE teams SET group_name = 'A' WHERE group_name IS NULL")
            
            print("✅ group_name column added successfully!")
        else:
            print("✅ group_name column already exists!")
        
        # Commit changes
        conn.commit()
        print("Database migration completed successfully!")
        
        # Show current data
        cursor.execute("SELECT COUNT(*) FROM tournaments")
        tournament_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM teams")
        team_count = cursor.fetchone()[0]
        
        print(f"Current data: {tournament_count} tournaments, {team_count} teams")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()








