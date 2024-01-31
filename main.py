from fastapi import FastAPI
import pandas as pd
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.get("/developer/{desarrollador}")
def developer(desarrollador: str):
  steamGamesData=pd.read_csv('steamGamesDf.csv')
  steamGamesDf=pd.DataFrame(steamGamesData)
  filteredDf=steamGamesDf[steamGamesDf['developer']==desarrollador]
  totalApps=filteredDf.groupby('Año').size().reset_index(name='Cantidad de Items')
  freeApps=filteredDf[filteredDf['price'].str.lower() == 'free'].groupby('Año').size().reset_index(name='free_items')
  result = pd.merge(totalApps, freeApps, on='Año', how='left').fillna(0)
  result['Contenido Free'] = ((result['free_items'] / result['Cantidad de Items']) * 100).round(2).astype(str) + '%'
  result=result[['Año','Cantidad de Items','Contenido Free']].reset_index(drop=True)
  result=result.to_dict(orient='records')
  return JSONResponse(content=result)

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