from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.get("/developer")
def developer(desarrollador: str):
  return

@app.get("/userdata")
def userdata(User_id: str): 
  return

@app.get("/userforgenre")
def UserForGenre(genero: str):
  return

@app.get("/bestdeveloperyear")
def best_developer_year(año: int): 
  return

@app.get("/developerreviewsanalysis")
def developer_reviews_analysis(desarrolladora: str):
  return