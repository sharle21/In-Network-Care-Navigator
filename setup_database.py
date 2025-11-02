import sqlite3

# This will create the file 'insurance.db' in your project folder
connection = sqlite3.connect('insurance.db')
cursor = connection.cursor()

# --- 1. Create the table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS networks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_name TEXT NOT NULL,
    provider_keyword TEXT NOT NULL,
    in_network BOOLEAN NOT NULL,
    copay TEXT
)
''')
print("Table 'networks' created successfully.")

# --- 2. Insert your mock data ---
network_data = [
    ('Aetna PPO', 'RightTime', True, '$75'),
    ('Aetna PPO', 'Patient First', False, '$1000+ (Out-of-Network)'),
    ('Aetna PPO', 'Adventist', True, '$300'),
    ('Aetna PPO', 'UM Capital', True, '$300'),
    ('Aetna PPO', 'MedStar', True, '$250'),
    ('Kaiser HMO', 'RightTime', False, '$900+ (Out-of-Network)'),
    ('Kaiser HMO', 'Adventist', True, '$200'),
    ('Kaiser HMO', 'UM Capital', True, '$200'),
]

cursor.executemany('''
INSERT INTO networks (plan_name, provider_keyword, in_network, copay) 
VALUES (?, ?, ?, ?)
''', network_data)
print(f"Inserted {len(network_data)} records successfully.")

# --- 3. Save (commit) the changes and close ---
connection.commit()
connection.close()