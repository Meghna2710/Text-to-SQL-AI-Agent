from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sql_langgraph_agent import run_text_to_sql_graph  # your logic here

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    sql: str
    answer: str

@app.post("/query", response_model=QueryResponse)
def get_sql_answer(req: QueryRequest):
    try:
        sql, answer = run_text_to_sql_graph(req.question)
        return QueryResponse(sql=sql, answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))