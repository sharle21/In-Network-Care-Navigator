import random

def get_wait_time(facility_name: str) -> str:
    """
    Returns a mock, random wait time for a given facility.
    """
    print(f"[Tool Call: get_wait_time] Getting mock wait time for '{facility_name}'")
    
    wait_minutes = 0
    if "clinic" in facility_name.lower() or "doctors" in facility_name.lower():
        wait_minutes = random.randint(15, 60)
    elif "hospital" in facility_name.lower():
        wait_minutes = random.randint(60, 240)
    else:
        wait_minutes = random.randint(20, 45)
        
    return f"~{wait_minutes} minutes"