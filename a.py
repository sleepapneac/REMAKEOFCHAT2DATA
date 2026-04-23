import streamlit as st
from pandasai import Agent
import pandas as pd
from pandasai_local import LocalLLM
import sqlite3
import tempfile
import os
# default endpoint given by lm studio, obviously adjustable here
llm = LocalLLM(api_base="http://localhost:1234/v1")
file = st.file_uploader("FILE UPLOAD", type=["csv", "json", "db", "sqlite"])
if file and (message := st.chat_input("Type your message...")):
    if file.name.endswith('.json'):
        df = pd.read_json(file)
    elif file.name.endswith(('.db', '.sqlite')):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        conn = sqlite3.connect(tmp_path)
        # for some reason sqlite still forces grabbing first table manually, so...
        first_table = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn).iloc[0, 0]
        df = pd.read_sql(f"SELECT * FROM {first_table}", conn)
        conn.close()
        os.unlink(tmp_path)
    else: pd.read_csv(file)
    agent = Agent(df, config={"llm": llm})
    st.chat_message("", avatar=("a.jpg")).write(message)
    with st.spinner("Give it a sec... or grab an RTX PRO 5000", show_time=True):
        # responds with scary binary code without the instruction, dunno why, so leave this hehe :3
        instruction = message + "\n\n(IMPORTANT! Your final user facing response is a natural string. NEVER return just the raw database information. Explain your response, i.e. if you are querying a database for anime recommendations, explain why you believe user would like your choices of anime you pick from the database.)"
        response = agent.chat(instruction)
        st.chat_message("", avatar=("a.jpg")).write(response)