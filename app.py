import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Dost", layout="wide")

st.title("🇵🇰 AI Dost - Pakistan Services Assistant")
st.subheader("سوال پوچھیں - آپ کے سوالوں کے جوابات")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about NADRA, Healthcare, Education, FBR..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from backend
    with st.chat_message("assistant"):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/ask",
                json={"text": prompt, "language": "english"},
                timeout=10
            )
            
            if response.status_code == 200:
                answer = response.json()["response"]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                error_msg = "Error: Could not get response"
                st.markdown(error_msg)
        except Exception as e:
            st.markdown(f"Error: {str(e)}")
