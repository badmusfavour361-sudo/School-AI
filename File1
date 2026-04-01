import streamlit as st
import google.generativeai as genai

# --- 1. BRANDING & UI ---
st.set_page_config(page_title="OAU AI", page_icon="🎓")

# Header section with your specific branding
st.title("OAU AI")
st.markdown("### *The link to the right information*")
st.divider()

# --- 2. CONFIGURATION ---
# Replace the string below with your actual API key from Google AI Studio
GOOGLE_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)

# Setting the Part Adviser personality
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=(
        "You are the OAU AI Part Adviser. "
        "Your goal is to provide precise academic information based ONLY on the "
        "official handbooks and documents provided. If you are unsure, tell the student "
        "to consult their HOD. Always try to cite the page number."
    )
)

# --- 3. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Box
if prompt := st.chat_input("Ask about MEE 205, admission, or faculty rules..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display AI response
    with st.chat_message("assistant"):
        with st.spinner("Verifying official records..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("Connection error. Please check your API key or data source.")
