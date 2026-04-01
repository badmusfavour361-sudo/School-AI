import streamlit as st
import google.generativeai as genai
import os
# 4. Input and Logic (Smart Search Version)
if prompt := st.chat_input("Ask about MEE courses or OAU rules..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching for official documents..."):
            try:
                # 1. This looks through your GitHub folder for ANY PDF
                all_files = os.listdir(".")
                pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]
                
                if pdf_files:
                    # 2. It picks the first PDF it finds (no matter the name)
                    target_pdf = pdf_files[0]
                    
                    # 3. It uploads that file to the AI 'Brain'
                    doc = genai.upload_file(path=target_pdf)
                    
                    # 4. It asks the AI to answer based on that document
                    response = model.generate_content([doc, prompt])
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    # If you forgot to upload the PDF to GitHub, it tells you here
                    st.error("No PDF found! Please upload your MEE Handbook to your GitHub repository.")
            except Exception as e:
                st.error(f"Technical Error: {e}")

