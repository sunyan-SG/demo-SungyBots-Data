import streamlit as st
import pandas as pd
from pandasai import Agent
from pandasai.llm.openai import OpenAI
from pandasai import SmartDatalake, SmartDataframe
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from pandasai.responses.streamlit_response import StreamlitResponse
import matplotlib.pyplot as plt
import os
import statsmodels.api
from scipy import stats

## should initialize st.state variables in below way
# if "openai_key" not in st.session_state:
#    st.session_state.openai_key = None

st.session_state.openai_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AIBot for Business Data",
                   layout="wide",
                   page_icon=":books::parrot:")

st.title("AI Chatbot for Business Intelligence & Analytics")

st.sidebar.markdown(
    """
    ### Message from SungyBots:
    Very welcome to try the chatbot developed by SungyBots!!
    Any further queries, feel free contact us: contact@SungyBots.com
    
    ### Instructions:
    1. Browse and upload your data files: .csv or .xlsx
    2. Click Process to read data
    3. Type your question in the box to get more insights
    """
)

# if "prompt_history" not in st.session_state:
#     st.session_state.prompt_history = []
#
# if "AI_response_history" not in st.session_state:
#     st.session_state["AI_response_history"] = []

# Create a container to display the chatbot's responses
#stream_handler = StreamHandler(st.empty())

# if "langchain_messages" not in st.session_state:
#     st.session_state["langchain_messages"] = []

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you today?")

# set up "dl"
if "dl" not in st.session_state:
    st.session_state["dl"] = []

#st.session_state.openai_key = "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"

with st.sidebar:
    # if st.session_state.get("openai_key") is None:
    #     st.session_state.openai_key = None
    #     st.session_state.uploaded_files = []
    #     #st.session_state.prompt_history = []
    #     #st.session_state.AI_response_history = []
    #     st.session_state.df = None
    #     st.session_state.dl = []
    #
    #     with st.form("API key"):
    #         key = st.text_input("OpenAI API Key", value="", type="password")
    #         if st.form_submit_button("Submit"):
    #             st.session_state.openai_key = key

    if st.session_state.get("openai_key") is not None:

        st.session_state.uploaded_files = st.file_uploader(
            "Choose a file (CSV or Excel) in long format (one data point per row).",
            type=["csv", "xlsx"],
            accept_multiple_files=True
        )
        if st.button("Process"):
            for file in st.session_state.uploaded_files:
                if file.name.endswith(".xlsx"):
                    df = pd.read_excel(file)
                elif file.name.endswith(".csv"):
                    df = pd.read_csv(file)
                else:
                    raise ValueError("File type not supported!")
                st.session_state.df = pd.DataFrame(df)
                st.session_state.dl.append(st.session_state.df)
            st.success("Data uploaded successfully!")

# if "langchain_messages" not in st.session_state:
#     st.session_state["langchain_messages"] = []

## display all the dfs
# if len(st.session_state.dl) > 0:
#     for df in st.session_state.dl:
#         st.write(df.head())

## only add the newly uploaded dfs
if len(st.session_state.dl) > 0:
    num_new_files = len(st.session_state.uploaded_files) if st.session_state.uploaded_files else 0
    start_index = len(st.session_state.dl) - num_new_files
    for df in st.session_state.dl[start_index:]:
        st.write(df.head())

# for msg in msgs.messages:
#     st.chat_message(msg.type).write(msg.content)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

prompt = st.chat_input("Your question here")
if prompt:
    if st.session_state.openai_key is None:
        st.error("Please submit your API key before using chatbot.")
    elif len(st.session_state.dl) == 0:
        st.error("Please upload your data file before using chatbot.")
    else:
        # Note: new messages are saved to history automatically by Langchain during run
        config = {"configurable": {"session_id": "any"}}
        llm = OpenAI(api_token=st.session_state.openai_key)
        agent = Agent(st.session_state.dl,
                      config={"llm": llm,
                              "enforce_privacy": True,
                              "response_parser": StreamlitResponse},
                      memory_size=10)
        response = agent.chat(prompt)
        #st.session_state.prompt_history.append(prompt)
        #st.session_state.AI_response_history.append(response)

        msgs.add_user_message(prompt)
        #msgs.add_ai_message(response)
        st.chat_message("user").write(prompt)
        #st.chat_message("ai").write(response["answer"])

        fig = plt.gcf()

        # else:
        #     st.chat_message("ai").write(response)

        #if isinstance(response, st.delta_generator.DeltaGenerator):
        if fig.get_axes():
            #st.image(response)  # Display images
            st.chat_message("ai").write("")
            st.pyplot(fig)
            msgs.add_ai_message("The response is an image, can't be saved.")
        elif isinstance(response, pd.DataFrame):
            st.chat_message("ai").write("")
            if len(response) > 20:
                st.table(response.head(5))  # Display head of table
            else:
                st.table(response)  # Display whole tables
            msgs.add_ai_message("The response is a table,can't be saved.")
        # elif isinstance(response, str):
        #     st.write(response)  # Display strings:
        else:
            st.chat_message("ai").write(response)  # Display all others
            msgs.add_ai_message(response)

