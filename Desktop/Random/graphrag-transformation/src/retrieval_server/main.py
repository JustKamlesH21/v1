from fastapi import FastAPI
from src.retrieval_server.query_agent import QueryAgent
from src.graph_constructor.graph_populator import GraphPopulator

app = FastAPI()

# Replace with your desired backend ('neo4j' or 'neptune')
DB_BACKEND = "neo4j"
graph_populator = GraphPopulator(DB_BACKEND)
query_agent = QueryAgent(graph_populator)

@app.get("/query/")
async def query(q: str):
    """
    Receives a query and returns the results from the query agent.
    """
    results = query_agent.retrieve(q)
    return {"query": q, "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)