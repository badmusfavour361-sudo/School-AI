import streamlit as st
import google.generativeai as genai
import os

# --- SECTION 1: BRANDING & UI ---
st.set_page_config(page_title="OAU AI", page_icon="🎓")
st.title("OAU AI")
st.markdown("### *The link to the right information*")
st.divider()

# --- SECTION 2: AUTO-MODEL CONFIGURATION ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key in Streamlit Secrets!")

try:
    # This scout finds all models available to your account
    available_models = [
        m.name for m in genai.list_models() 
        if 'generateContent' in m.supported_generation_methods
    ]
    
    # Priority list: Flash 1.5, Pro 1.5, then anything else
    if 'models/gemini-1.5-flash' in available_models:
        selected_model = 'models/gemini-1.5-flash'
    elif 'models/gemini-1.5-pro' in available_models:
        selected_model = 'models/gemini-1.5-pro'
    else:
        selected_model = available_models[0]
        
        # --- SECTION 2: UPDATED SYSTEM INSTRUCTIONS ---
model = genai.GenerativeModel(
    model_name=selected_model,
    system_instruction=(
        "You are the OAU AI Part Adviser. Your goal is to close the information gap for students. "
        "Use ONLY the provided PDFs to answer. If the answer is not in the PDFs, "
        "say: 'I don't know, please consult your Part Adviser.' "
        ""
        "CRITICAL CITATION RULE: You must always mention the EXACT filename of the PDF "
        "and the page number for every fact you provide. "
        "Format: 'According to [Filename], Page [X]...' or 'Source: [Filename] (Page X)'."
        )
    )
    with st.sidebar:
        st.success(f"Connected to: {selected_model}")
except Exception as e:
    st.error(f"Model initialization failed: {e}")

# --- SECTION 3: SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SECTION 4: DISPLAY HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- SECTION 5: MULTI-PDF LOGIC ---
if prompt := st.chat_input("Ask about MEE 205, Further Maths, or Admission..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consulting the OAU Library..."):
            try:
                # 1. Find ALL PDFs in the folder
                all_files = os.listdir(".")
                pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]
                
                if pdf_files:
                    # 2. Prepare a list for the AI
                    docs_to_send = []
                    
                    # 3. Upload every single PDF found
                    for f in pdf_files:
                        uploaded_doc = genai.upload_file(path=f)
                        docs_to_send.append(uploaded_doc)
                    
                    # 4. Send all documents + the user's question to the brain
                    # The AI will now cross-reference all files to find the answer
                    response = model.generate_content(docs_to_send + [prompt])
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.error("No PDFs found! Please upload your handbooks to GitHub.")
            except Exception as e:
                st.error(f"Technical Error: {e}")
# --- SECTION 6: FEEDBACK & DATA COLLECTION ---
with st.sidebar:
    st.divider()
    st.subheader("Help Future Students 🚀")
    st.write("Did you face an information gap that cost you? Tell us below.")
    
    # Text area for user input
    user_problem = st.text_area("What info do you wish you had known?", placeholder="e.g., 'I didn't know MEE 205 required Further Maths'...")
    
    if st.button("Submit to OAU AI"):
        if user_problem:
            # For now, this just thanks the user. 
            # In a pro version, we would save this to a database.
            st.success("Thank you! Your experience will help the next generation.")
            # LOGGING: This prints to your Streamlit Cloud logs so you can read them later!
            print(f"USER FEEDBACK: {user_problem}")
        else:
            st.warning("Please type something before submitting.")
