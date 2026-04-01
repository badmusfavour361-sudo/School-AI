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
        
    model = genai.GenerativeModel(
        model_name=selected_model,
        system_instruction=(
            "You are the OAU AI Part Adviser. Use ONLY the provided PDF. "
            "If the answer is not in the PDF, say: 'I don't know, please consult your Part Adviser.' "
            "Always cite the page number."
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

# --- SECTION 5: SMART SEARCH & LOGIC ---
if prompt := st.chat_input("Ask about MEE 205 or Admission..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking official records..."):
            try:
                # This finds any PDF in your folder automatically
                all_files = os.listdir(".")
                pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]
                
                if pdf_files:
                    target_pdf = pdf_files[0]
                    doc = genai.upload_file(path=target_pdf)
                    response = model.generate_content([doc, prompt])
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.error("No PDF found! Please upload your OAU Handbook to GitHub.")
            except Exception as e:
                st.error(f"Technical Error: {e}") 