import streamlit as st
import google.generativeai as genai
import os

# 1. Page Setup
st.set_page_config(page_title="OAU AI", page_icon="🎓")
st.title("OAU AI")
st.markdown("### *The link to the right information*")
st.divider()

# 2. Initialize Session State (This fixes the AttributeError)
# This MUST happen before you try to append to st.session_state.messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. API Configuration
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key in Streamlit Secrets!")

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    system_instruction=(
        "You are the OAU AI Part Adviser. Use ONLY the provided PDF. "
        "If the answer is not in the PDF, say: 'I don't know, please consult your Part Adviser.' "
        "Always try to cite the page number."
    )
)

# Temporary Debugging Code
with st.sidebar:
    st.write("Available Models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                st.write(m.name)
    except Exception as e:
        st.write(f"Could not list models: {e}")
# 4. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Input and AI Logic
if prompt := st.chat_input("Ask about MEE 205 or OAU regulations..."):
    # Now that the list is initialized above, this line will work perfectly
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
