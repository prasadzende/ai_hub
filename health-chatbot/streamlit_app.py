import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agent.agentic_workflow import GraphBuilder

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Health Chatbot",
    page_icon="🧑‍⚕️",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("🧑‍⚕️ AI Health Chatbot")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.graph = GraphBuilder(model_provider="lmstudio")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get chatbot response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Stream the response
        for event in st.session_state.graph().stream({
            "messages": [{"role": "user", "content": prompt}]
        }, {"recursion_limit": 100}):
            for value in event.values():
                response_content = value["messages"][-1].content
                full_response = response_content
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})