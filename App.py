import os
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

# ── Page config ─
st.set_page_config(
    page_title="Netflix SQL Agent",
    page_icon="🎬",
    layout="wide",
)

# ── Clean Modern Dark Theme ──
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
<head>
  <link rel="stylesheet" href="https://fonts.googleapis.com">
</head>


html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Responsive for smaller screens */
@media (max-width: 768px) {
    .main-title h1 {
        font-size: 2.5rem;
    }
}


.stApp {
    background-color: #0f0f0f;
    color: #e6e6e6;
}

/* Center content */
.block-container {
    padding-top: 8rem;
    max-width: 1200px;
}

/* Header */
.main-title {
    text-align: center;
    margin-bottom: 1.0rem;
}

.main-title h1 {
    font-size: 3rem;
    color: #E50914;
    font-weight: 700;
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 3px; 
}

.main-title p {
    color: #aaa;
    font-size: 0.95rem;
}

/* Chat bubbles */
.stChatMessage {
    border-radius: 14px !important;
    padding: 0.19rem !important;
}

/* User bubble */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background-color: #1f1f1f !important;
}

/* Assistant bubble */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background-color: #161616 !important;
    border: 1px solid #262626 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #121215 !important;
    border-right: 1px solid #1f1f1f;
    margin-bottom: 15px !important;
}

/* Buttons */
.stButton button {
    background-color: #b20710!important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 500 !important;
    margin-top: 1px !important;
}


/* Input */
textarea {
    background-color: #1a1a1a !important;
    color: #e6e6e6 !important;
    border-radius: 5px !important;
    border: 1px solid #2a2a2a !important;
    padding: 1rem !important;
}

/* Remove Streamlit branding */
#MainMenu, footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# ── Header ──

st.markdown("""
<div class="main-title">
    <h1>🎬 NETFLIX SQL Agent</h1>
    <p>Natural language to SQL powered by GPT-4.1 + LangGraph</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    show_tool_calls = st.toggle("Show agent reasoning", value=True)
    top_k = st.slider("Max results per query", min_value=1, max_value=20, value=5)

    st.markdown("---")
    st.markdown("### 💡 Example questions")
    example_questions = [
        "Which movie has the longest duration?",
        "Which genre on average has the longest duration?",
        "What are the top 5 most common genres?",
        "How many unique type are in the netflix table?",
    ]
    for q in example_questions:
        if st.button(q, key=q):
            st.session_state.pending_question = q

    st.markdown("---")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ── Agent setup (cached so it only runs once) ──
@st.cache_resource
def load_agent(top_k: int):
    api_key = st.secrets["OPENAI_API_KEY"]
    if not api_key:
        st.error("OPENAI_API_KEY not found. Add it to your .env file.")
        st.stop()

    model = ChatOpenAI(model="gpt-4.1", api_key=api_key, streaming=True)

    DATABASE_URL = (
        "mssql+pyodbc://@localhost/netflix"
        "?driver=ODBC+Driver+17+for+SQL+Server"
        "&trusted_connection=yes"
    )
    db = SQLDatabase.from_uri(DATABASE_URL)

    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    tools = toolkit.get_tools()

    system_prompt = f"""
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {db.dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples, always limit your query to at most {top_k} results.

Order results by a relevant column to return the most interesting examples.
Never query all columns from a table — only ask for relevant columns.

You MUST double check your query before executing it. If you get an error,
rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

Always start by looking at the tables in the database, then query the schema
of the most relevant tables before answering.
"""

    agent = create_react_agent(model, tools, prompt=system_prompt)
    return agent


agent = load_agent(top_k)

# ── Session state ───
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render existing chat history ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🎬" if msg["role"] == "assistant" else "🧑"):
        st.markdown(msg["content"])
        if msg.get("tool_calls") and show_tool_calls:
            with st.expander(f"🔍 Agent used {len(msg['tool_calls'])} tool(s)", expanded=False):
                for tc in msg["tool_calls"]:
                    st.markdown(f"**Tool:** `{tc['tool']}`")
                    st.code(tc["input"], language="sql" if "sql" in tc["tool"].lower() else "text")
                    if tc.get("output"):
                        st.markdown("**Result:**")
                        st.code(tc["output"], language="text")
                    st.markdown("---")

# ── Handle sidebar example question clicks ───
if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")
else:
    prompt = st.chat_input("Ask something about the Netflix database...")

# ── Process new message ───
if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    # Stream agent response
    with st.chat_message("assistant", avatar="🎬"):
        response_placeholder = st.empty()
        tool_calls_collected = []
        full_response = ""

        with st.spinner("Thinking..."):
            for step in agent.stream(
                {"messages": [{"role": "user", "content": prompt}]},
                stream_mode="values",
            ):
                last_msg = step["messages"][-1]
                msg_type = last_msg.__class__.__name__

                # Tool call messages
                if msg_type == "AIMessage" and last_msg.tool_calls:
                    for tc in last_msg.tool_calls:
                        tool_calls_collected.append({
                            "tool": tc["name"],
                            "input": tc["args"].get("query") or str(tc["args"]),
                            "output": None,
                        })

                # Tool result messages
                elif msg_type == "ToolMessage":
                    if tool_calls_collected:
                        tool_calls_collected[-1]["output"] = last_msg.content[:500]

                # Final AI response
                elif msg_type == "AIMessage" and not last_msg.tool_calls:
                    full_response = last_msg.content
                    response_placeholder.markdown(full_response)

        # Show tool calls if enabled
        if tool_calls_collected and show_tool_calls:
            with st.expander(f"🔍 Agent used {len(tool_calls_collected)} tool(s)", expanded=False):
                for tc in tool_calls_collected:
                    st.markdown(f"**Tool:** `{tc['tool']}`")
                    st.code(tc["input"], language="sql" if "sql" in tc["tool"].lower() else "text")
                    if tc.get("output"):
                        st.markdown("**Result:**")
                        st.code(tc["output"], language="text")
                    st.markdown("---")

    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "tool_calls": tool_calls_collected,
    })
