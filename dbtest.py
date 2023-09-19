import sqlite3

def create_database():
    # Connect to SQLite database; create the file if doesn't exist
    conn = sqlite3.connect("agricultural_enterprise.db")
    cursor = conn.cursor()

    # Create Farms table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Farms (
        farm_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        area_in_acres REAL
    );
    """)

    # Create Crops table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Crops (
        crop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ideal_season TEXT,
        average_yield_per_acre REAL
    );
    """)

    # Create Farmers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Farmers (
        farmer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact_number TEXT,
        years_of_experience INTEGER
    );
    """)

    # Create Equipment table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Equipment (
        equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT,
        farm_id INTEGER,
        FOREIGN KEY(farm_id) REFERENCES Farms(farm_id)
    );
    """)

    # Create Cultivation table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Cultivation (
        cultivation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER,
        crop_id INTEGER,
        farmer_id INTEGER,
        date_planted TEXT,
        estimated_harvest_date TEXT,
        FOREIGN KEY(farm_id) REFERENCES Farms(farm_id),
        FOREIGN KEY(crop_id) REFERENCES Crops(crop_id),
        FOREIGN KEY(farmer_id) REFERENCES Farmers(farmer_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Financials (
        financial_id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER,
        revenue REAL,
        expenditure REAL,
        profit REAL,
        year INTEGER,
        month INTEGER,
        FOREIGN KEY(farm_id) REFERENCES Farms(farm_id)
    );
    """)

    # Create SocialImpact table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SocialImpact (
        impact_id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER,
        community_engagement TEXT,
        sustainability_index REAL,
        social_initiatives TEXT,
        FOREIGN KEY(farm_id) REFERENCES Farms(farm_id)
    );
    """)

    # Create Employee table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employee (
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        position TEXT,
        salary REAL,
        farm_id INTEGER,
        FOREIGN KEY(farm_id) REFERENCES Farms(farm_id)
    );
    """)

    # Create CustomerFeedback table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CustomerFeedback (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_id INTEGER,
        rating REAL,
        comments TEXT,
        FOREIGN KEY(crop_id) REFERENCES Crops(crop_id)
    );
    """)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
