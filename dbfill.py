import sqlite3
import random

# Function to populate data
def populate_database():
    # Connect to SQLite database
    conn = sqlite3.connect("agricultural_enterprise.db")
    cursor = conn.cursor()

    # Populate Farms table
    farms = [(f'Farm_{i}', f'Location_{i}', random.uniform(50, 100)) for i in range(10)]
    cursor.executemany("INSERT INTO Farms (name, location, area_in_acres) VALUES (?, ?, ?)", farms)

    # Populate Crops table
    crops = [(f'Crop_{i}', f'Season_{i}', random.uniform(20, 40)) for i in range(10)]
    cursor.executemany("INSERT INTO Crops (name, ideal_season, average_yield_per_acre) VALUES (?, ?, ?)", crops)

    # Populate Farmers table
    farmers = [(f'Farmer_{i}', f'Contact_{i}', random.randint(5, 20)) for i in range(10)]
    cursor.executemany("INSERT INTO Farmers (name, contact_number, years_of_experience) VALUES (?, ?, ?)", farmers)

    # Populate Equipment table
    equipment = [(f'Equipment_{i}', random.choice(['Heavy', 'Light']), random.randint(1, 10)) for i in range(10)]
    cursor.executemany("INSERT INTO Equipment (name, type, farm_id) VALUES (?, ?, ?)", equipment)

    # Populate Cultivation table
    cultivation = [(random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), '2022-04-01', '2022-09-01') for i in range(10)]
    cursor.executemany("INSERT INTO Cultivation (farm_id, crop_id, farmer_id, date_planted, estimated_harvest_date) VALUES (?, ?, ?, ?, ?)", cultivation)

    # Populate Financials table
    financials = [(random.randint(1, 10), random.uniform(100000, 200000), random.uniform(50000, 100000), random.uniform(50000, 100000), 2022, random.randint(1, 12)) for i in range(10)]
    cursor.executemany("INSERT INTO Financials (farm_id, revenue, expenditure, profit, year, month) VALUES (?, ?, ?, ?, ?, ?)", financials)

    # Populate SocialImpact table
    social_impact = [(random.randint(1, 10), f'Community_{i}', random.uniform(70, 100)) for i in range(10)]
    cursor.executemany("INSERT INTO SocialImpact (farm_id, community_engagement, sustainability_index) VALUES (?, ?, ?)", social_impact)

    # Populate Employee table
    employees = [(f'Employee_{i}', f'Position_{i}', random.uniform(30000, 60000), random.randint(1, 10)) for i in range(10)]
    cursor.executemany("INSERT INTO Employee (name, position, salary, farm_id) VALUES (?, ?, ?, ?)", employees)

    # Populate CustomerFeedback table
    customer_feedback = [(random.randint(1, 10), random.uniform(2, 5), f'Comment_{i}') for i in range(10)]
    cursor.executemany("INSERT INTO CustomerFeedback (crop_id, rating, comments) VALUES (?, ?, ?)", customer_feedback)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    populate_database()
