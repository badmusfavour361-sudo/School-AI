import streamlit as st
import google.generativeai as genai
import os

# --- SECTION 1: BRANDING & UI ---
st.set_page_config(page_title="OAU AI", page_icon="🦅")
st.title("OAU AI")
st.markdown("### *The link to the right information*")
st.divider()

# --- SECTION 2: CONFIGURATION & BRAIN INSTRUCTIONS ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key in Streamlit Secrets!")

try:
    available_models = [
        m.name for m in genai.list_models() 
        if 'generateContent' in m.supported_generation_methods
    ]
    selected_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
        
    model = genai.GenerativeModel(
        model_name=selected_model,
        system_instruction=(
            "You are the OAU AI Part Adviser. Use ONLY the provided PDFs to answer. "
            "If the answer is not in the PDFs, say: 'I don't know, please consult your Part Adviser.' "
            "CITATIONS: You must always mention the EXACT filename of the PDF "
            "and the page number for every fact. Example: 'According to MEE_Handbook.pdf, Page 5...'"
        )
    )
    with st.sidebar:
        st.success(f"Connected to: {selected_model}")
except Exception as e:
    st.error(f"Setup Error: {e}")

# --- SECTION 3: SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SECTION 4: DISPLAY HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- SECTION 5: MULTI-PDF CHAT LOGIC ---
if prompt := st.chat_input("Ask about MEE 205, Further Maths, or Admission..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching the handbooks..."):
            try:
                all_files = os.listdir(".")
                pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]
                
                if pdf_files:
                    docs_to_send = []
                    for f in pdf_files:
                        uploaded_doc = genai.upload_file(path=f)
                        docs_to_send.append(uploaded_doc)
                    
                    response = model.generate_content(docs_to_send + [prompt])
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.error("Please upload PDFs to your GitHub folder.")
            except Exception as e:
                st.error(f"Error reading PDFs: {e}")

# --- SECTION 6: THE "GREAT IFE" FEEDBACK HUB ---
with st.sidebar:
    st.divider()
    st.subheader("Help Other Great Ife Students! 🦅")
    st.write("Did you face an **information gap** that cost you? Share it below to help the next generation succeed.")
    
    user_problem = st.text_area(
        "What info do you wish you had known?", 
        placeholder="e.g., 'I didn't know MEE 205 required Further Maths'...",
        help="Your feedback helps us train the AI to bridge these gaps."
    )
    
    if st.button("Submit to the Knowledge Base"):
        if user_problem:
            st.success("Thank you, Great Ife! Your experience is now part of the solution.")
            # This logs the info so you can read it in 'Manage App' -> 'Logs'
            print(f"INFORMATION GAP REPORTED: {user_problem}")
        else:
            st.warning("Please type your experience before submitting.")

# --- SECTION 7: HIGH-SPEED CGPA CALCULATOR ---
with st.sidebar:
    st.divider()
    st.subheader("⚡ Fast CGPA Calculator")
    st.write("Paste your results below (Format: Course Unit Grade)")
    st.caption("Example: MEE201 3 A, CSC201 2 B")
    
    raw_input = st.text_area("Enter results:", placeholder="MEE201 3 A...")
    
    if st.button("Calculate Now"):
        if raw_input:
            try:
                # Mapping logic
                grade_map = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}
                total_units = 0
                total_points = 0
                
                # Split input by commas or new lines
                entries = raw_input.replace('\n', ',').split(',')
                
                for entry in entries:
                    parts = entry.strip().split()
                    if len(parts) >= 3:
                        unit = int(parts[-2]) # Takes the second to last item
                        grade = parts[-1].upper() # Takes the last item
                        
                        if grade in grade_map:
                            total_units += unit
                            total_points += (unit * grade_map[grade])
                
                if total_units > 0:
                    cgpa = total_points / total_units
                    st.metric("Your CGPA", f"{cgpa:.2f}")
                    if cgpa >= 4.5: st.balloons()
                else:
                    st.error("Invalid format. Use: Course Unit Grade")
            except Exception as e:
                st.error("Error: Please check your formatting.")


