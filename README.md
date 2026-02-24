# 🎬 Netflix SQL Agent  
Natural Language → SQL queries on Netflix dataset — powered by LangGraph & GPT-4o

# ✨ Features

- Ask questions in plain English → gets translated to correct SQL

- Streaming responses + reasoning visualization (toggle)

- Modern dark Netflix-style UI with custom CSS

- Agent re-tries on syntax errors

- Example questions & one-click sidebar

- Caching + session state for smooth UX

- Read-only secure database access


<img width="1868" height="866" alt="Netflix_ui2" src="https://github.com/user-attachments/assets/bb7a7849-0511-43cc-8720-043e5c558a3a" />



<img width="1179" height="422" alt="Netflix_ui3" src="https://github.com/user-attachments/assets/16c9c3ce-cab9-4d95-9fd1-c1c4b60a9ff7" />


<img width="1062" height="467" alt="Netflix_ui4" src="https://github.com/user-attachments/assets/b07580d7-6858-4601-b661-dd245362a85f" />


# Tech Stack

- **Frontend**: Streamlit (custom dark theme + responsive)

- **Agent Framework**: LangGraph (ReAct agent pattern)

- **LLM**: OpenAI GPT-4o (streaming)

- **Database**: Microsoft SQL Server (Netflix titles & metadata)

- **Orchestration**: LangChain SQLDatabaseToolkit

- **Other**: python-dotenv, pyodbc

## Project Structure

├── app.py                # Main Streamlit app

├── .env.example          # Copy to .env and add OPENAI_API_KEY

├── requirements.txt          

└── README.md


## Quick Start (Local)

1. Clone repo  
   ```bash
   git clone https://github.com/yourname/netflix-sql-agent.git
   cd netflix-sql-agent

Create .env and add your key 

OPENAI_API_KEY=sk-...

Install dependencies 

Bash  pip install -r requirements.txt

Run Bash: streamlit run app.py


# Security Notes

Agent restricted to SELECT queries only

No DML allowed (DROP, INSERT, UPDATE blocked in prompt)

Uses trusted connection (Windows auth) — change to username/password in production

# Roadmap / Possible Improvements

Add query explanation in natural language

Support multiple databases

Add chart visualization (Plotly/Altair)

Voice input

Deploy with Docker + auth
