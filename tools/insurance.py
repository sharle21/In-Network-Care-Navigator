import sqlite3

DB_PATH = 'insurance.db'
DEFAULT_NETWORK_STATUS = {"in_network": "Unknown", "copay": "N/A"}

def check_insurance_network(facilities_list: list, plan_name: str) -> list:
    """
    Checks a list of facilities against the SQLite 'insurance.db'.
    It adds 'insurance_info' to each facility dictionary in the list.
    """
    print(f"[Tool Call: check_insurance_network] Checking plan '{plan_name}' against SQLite DB")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        updated_facilities_list = []

        for facility in facilities_list:
            facility_name = facility['name']
            
            # Find any row where the plan_name matches AND
            # the provider_keyword is found anywhere inside the facility_name.
            cursor.execute(
                "SELECT * FROM networks WHERE plan_name = ? AND ? LIKE '%' || provider_keyword || '%'",
                (plan_name, facility_name)
            )
            
            row = cursor.fetchone() 
            
            if row:
                facility['insurance_info'] = {
                    "in_network": bool(row['in_network']),
                    "copay": row['copay']
                }
            else:
                facility['insurance_info'] = DEFAULT_NETWORK_STATUS
                
            updated_facilities_list.append(facility)
            
        conn.close()
        return updated_facilities_list
        
    except Exception as e:
        print(f"Error querying SQLite database: {e}")
        return facilities_list