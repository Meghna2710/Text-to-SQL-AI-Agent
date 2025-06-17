from langchain_community.llms import Ollama
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langgraph.graph import StateGraph
from typing import TypedDict
import re

# --- Use local model via Ollama
llm = Ollama(model="mistral")

# --- Load database
db = SQLDatabase.from_uri("sqlite:///sample.db")

# --- Define the state structure
class GraphState(TypedDict):
    question: str
    sql: str
    query_result: str
    summary: str

# --- SQL generation prompt
sql_prompt = PromptTemplate(
    input_variables=["question", "table_info"],
    template="""
You are an expert in SQL. Write only the SQL query for the given question and schema.

Tables:
{table_info}

Question:
{question}

SQL Query:
"""
)

sql_chain = LLMChain(llm=llm, prompt=sql_prompt)

# --- SQL generation node
def generate_sql_node(state: GraphState) -> GraphState:
    table_info = db.get_table_info()
    raw_output = sql_chain.run({
        "question": state["question"],
        "table_info": table_info
    })
    match = re.search(r"```sql\s*(.*?)```", raw_output, re.DOTALL | re.IGNORECASE)
    if match:
        sql = match.group(1).strip()
    else:
        sql = raw_output.split(";")[0].strip() + ";"
    return {"question": state["question"], "sql": sql}

# --- SQL execution node
def execute_sql_node(state: GraphState) -> GraphState:
    try:
        result = db.run(state["sql"])
        formatted_result = "\n".join([str(row) for row in result])
        return {"sql": state["sql"], "query_result": formatted_result}
    except Exception as e:
        return {"sql": state["sql"], "query_result": f"Error: {e}"}

# --- Natural language summarization prompt
summary_prompt = PromptTemplate(
    input_variables=["question", "query_result"],
    template="""
You are an assistant. Given a user's question and the result of a SQL query, write a concise natural language answer.
If the result contains an error, explain it clearly.

Question:
{question}

Query Result:
{query_result}

Answer:
"""
)

summary_chain = LLMChain(llm=llm, prompt=summary_prompt)

# --- Summary node
def summarize_node(state: GraphState) -> GraphState:
    query_result = state["query_result"]
    question = state["question"]
    if query_result.strip().lower().startswith("error:"):
        return {"summary": f"There was an error executing the SQL query: {query_result}"}
    summary = summary_chain.run({
        "question": question,
        "query_result": query_result
    })
    return {"summary": summary.strip()}

# --- Define the LangGraph workflow
workflow = StateGraph(GraphState)
workflow.add_node("SQLGenerator", generate_sql_node)
workflow.add_node("SQLExecutor", execute_sql_node)
workflow.add_node("Summarizer", summarize_node)

workflow.set_entry_point("SQLGenerator")
workflow.add_edge("SQLGenerator", "SQLExecutor")
workflow.add_edge("SQLExecutor", "Summarizer")
workflow.set_finish_point("Summarizer")

graph = workflow.compile()

# --- Main callable function
def run_text_to_sql_graph(nl_question: str):
    result = graph.invoke({"question": nl_question})
    return result["sql"], result["summary"]
