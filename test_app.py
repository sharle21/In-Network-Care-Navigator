import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Import all your tools
from tools.triage import triage_symptoms
from tools.facilities import find_local_facilities
from tools.insurance import check_insurance_network
from tools.wait_times import get_wait_time

# --- 1. SETUP ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- 2. CONFIGURE TOOLS ---

# This tells our code HOW to execute the tools Gemini requests.
TOOL_REGISTRY = {
    "triage_symptoms": triage_symptoms,
    "find_local_facilities": find_local_facilities,
    "check_insurance_network": check_insurance_network,
    "get_wait_time": get_wait_time,
}

# This tells Gemini WHAT tools it can use.
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    tools=[
        triage_symptoms,
        find_local_facilities,
        check_insurance_network,
        get_wait_time,
    ]
)

# --- 3. THE SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are "CareCompass," a helpful and compassionate care navigator. Your goal is to
find the best in-network care options for a user based on their symptoms, 
location, and insurance plan.

You will follow a strict, multi-step plan:
1.  **Triage:** First, you MUST call `triage_symptoms` to understand the user's
    medical need (e.g., "ER", "X-ray", "Doctor").
2.  **Find:** Second, you MUST call `find_local_facilities` using the user's
    location and the `required_resource` from step 1.
3.  **Check Insurance:** Third, you MUST call `check_insurance_network` using the
    list of facilities from step 2 and the user's plan.
4.  **Get Wait Times:** Fourth, for each in-network facility, you MUST call
    `get_wait_time`.
5.  **Summarize:** Finally, you MUST present the results to the user.

**Summary Rules:**
-   Start with a brief, empathetic statement and clearly state the triage result.
-   Create a "Recommended" option. This should be the *closest* facility that
    is *in-network* and *has the required resources*.
-   Create a "Other In-Network Options" section.
-   Create a "⚠️ Out-of-Network" section.
-   For each facility, clearly list:
    -   Name and Address
    -   Est. Wait Time
    -   Insurance Status (e.g., "✅ In-Network")
    -   Est. Co-pay
-   Your tone should be clear, calm, and reassuring. Do NOT add any medical
    advice that is not from the triage tool.
"""

# --- 4. THE STREAMLIT APP ---

st.set_page_config(layout="wide")
st.title("CareCompass 🧭")
st.markdown("Your AI assistant for finding the right care, right now.")

# Create the input fields
symptoms = st.text_area("1. Describe your symptoms", "I have terrible chest pain and shortness of breath.")
location = st.text_input("2. What is your location?", "Arlington, VA")
insurance = st.text_input("3. What is your insurance plan?", "Aetna PPO")

# The "Find Care" button
if st.button("Find Care"):
    
    # --- This is the main "agent" logic ---
    with st.spinner("Analyzing your options... This may take a moment."):
        try:
            # 1. Format the user's prompt
            full_prompt = f"""
            {SYSTEM_PROMPT}
            
            User: I am in {location}, my plan is {insurance}, and I am having {symptoms}.
            """

            # 2. Start the chat
            chat = model.start_chat()
            response = chat.send_message(full_prompt)

            # 3. The Agent Loop
            while response.candidates[0].content.parts[0].function_call:
                function_calls = response.candidates[0].content.parts
                function_responses = []
                
                # This is a temporary "memory" for this turn, to pass
                # the facility list from one tool to the next.
                session_data = {}

                # Show the user what the agent is "thinking"
                call_names = [call.function_call.name for call in function_calls]
                st.info(f"🧠 Thinking... (Calling tools: {', '.join(call_names)})")

                for call in function_calls:
                    fn_call = call.function_call
                    fn_name = fn_call.name
                    
                    if fn_name not in TOOL_REGISTRY:
                        print(f"Error: Gemini tried to call unknown function '{fn_name}'")
                        continue
                        
                    fn_to_call = TOOL_REGISTRY[fn_name]
                    args = dict(fn_call.args)
                    
                    # --- Dependency Injection ---
                    # Check if this tool needs data from a *previous* tool
                    if fn_name == "check_insurance_network":
                        args["facilities_list"] = session_data.get("facilities", [])
                    
                    # --- Call the actual Python tool function ---
                    result = fn_to_call(**args)
                    
                    # --- Update our session with new data ---
                    if fn_name == "find_local_facilities":
                        session_data["facilities"] = result
                    if fn_name == "check_insurance_network":
                        session_data["facilities"] = result # Store the *updated* list
                    
                    function_responses.append(
                        {
                            "name": fn_name,
                            "response": result,
                        }
                    )
                
                # Send the tool results *back* to Gemini
                response = chat.send_message(
                    [genai.protos.Part(
                        function_response = genai.protos.FunctionResponse(
                            name=fr["name"],
                            response={"result": json.dumps(fr["response"])} 
                        )
                    ) for fr in function_responses]
                )
            
            # 4. The Loop is done. Get the final answer.
            final_answer = response.text
            st.success("Here are your personalized recommendations!")
            st.markdown(final_answer)
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.error("Please try again. If the error persists, the Triage API (Person A's Colab) might be offline.")