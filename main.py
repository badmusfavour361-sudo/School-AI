import streamlit as st
import google.generativeai as genai
import os

# --- 1. BRANDING ---
st.set_page_config(page_title="OAU AI", page_icon="🎓")
st.title("OAU AI")
st.markdown("### *The link to the right information*")
st.divider()

# --- 2. CONFIGURATION ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key in Streamlit Secrets!")

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction="You are the OAU AI Part Adviser. Use ONLY the provided PDF. If the answer isn't there, say: 'I don't know, please consult your Part Adviser.' Always cite the page number."
)

# --- 3. THE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about MEE 205 or Admission..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking official records..."):
            try:
                # MAKE SURE YOUR PDF ON GITHUB IS NAMED EXACTLY THIS:
                pdf_path = "mee_handbook.pdf" 
                
                if os.path.exists(pdf_path):
                    doc = genai.upload_file(path=pdf_path)
                    response = model.generate_content([doc, prompt])
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.error(f"Error: I can't find '{pdf_path}' in your GitHub files. Please check the name!")
            except Exception as e:
                st.error(f"Technical Error: {e}")
