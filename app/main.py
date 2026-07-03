from fastapi import FastAPI

app = FastAPI()

@app.post("/optimize")
def optimize():
    return {"message":"This is a prompt optimizer"}