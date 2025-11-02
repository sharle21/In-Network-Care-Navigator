import requests

# This is the public URL you gave them
TRIAGE_API_URL = "https://a1b2-c3d4-e5f6.ngrok.io/triage" 

def triage_symptoms(symptom_description: str) -> dict:
    """
    This function is now just an API client. It calls the 
    MedGemma microservice running in Google Colab.
    """
    print(f"[Tool Call: Triage] Calling MedGemma API for: '{symptom_description}'")
    
    try:
        # Make the API call to your Colab notebook
        response = requests.post(
            TRIAGE_API_URL,
            json={"symptoms": symptom_description},
            timeout=30 # Give it 30 seconds, as MedGemma is a large model
        )
        
        response.raise_for_status() # Raise an error if the API call fails
        
        data = response.json() # This will be {"triage_level": "ER", ...}
        
        # --- Map the API output to what the Orchestrator expects ---
        triage_level = data.get("triage_level", "Urgent Care")
        
        if triage_level == "ER":
            return {"triage_level": "Emergency", "required_resource": "ER"}
        elif triage_level == "Urgent Care":
            return {"triage_level": "Urgent", "required_resource": "X-ray"} # or "Stitches"
        else:
            return {"triage_level": "Urgent", "required_resource": "Doctor"}

    except Exception as e:
        print(f"Error calling Triage API: {e}")
        # Fallback if your server is down
        return {"triage_level": "Urgent", "required_resource": "Doctor"}