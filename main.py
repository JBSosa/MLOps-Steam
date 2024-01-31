from fastapi import FastAPI
import pandas as pd
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.get("/developer/{desarrollador}")
def developer(desarrollador: str):
  steamGamesData=pd.read_csv('steamGames.csv')
  steamGamesDf=pd.DataFrame(steamGamesData)
  filteredDf=steamGamesDf[steamGamesDf['developer']==desarrollador]
  totalApps=filteredDf.groupby('Año').size().reset_index(name='Cantidad de Items')
  freeApps=filteredDf[filteredDf['price'].str.lower() == 'free'].groupby('Año').size().reset_index(name='free_items')
  result = pd.merge(totalApps, freeApps, on='Año', how='left').fillna(0)
  result['Contenido Free'] = ((result['free_items'] / result['Cantidad de Items']) * 100).round(2).astype(str) + '%'
  result=result[['Año','Cantidad de Items','Contenido Free']].reset_index(drop=True)
  result=result.to_dict(orient='records')
  return JSONResponse(content=result)

@app.get("/userdata/{userId}")
def userdata(userId: str):
  #Cargar CSV
  userRecommendData=pd.read_csv('userReviewsExploded.csv')
  userItemsData=pd.read_csv('userItemsExploded.csv')
  userItemCountData=pd.read_csv('userItemCount.csv')
  gamePriceData=pd.read_csv('steamGamesPrice.csv')
  #Convertir a DataFrame
  userRecommendDf=pd.DataFrame(userRecommendData)
  userItemsDf=pd.DataFrame(userItemsData)
  userItemCountDf=pd.DataFrame(userItemCountData)
  gamePriceDf=pd.DataFrame(gamePriceData)
  #Filtrar por usuario
  userRecommendDf=userRecommendDf[userRecommendDf['user_id']==userId].reset_index(drop=True)
  userItemsDf=userItemsDf[userItemsDf['user_id']==userId].reset_index(drop=True)
  userItemsDf=pd.merge(userItemsDf,gamePriceDf,how='left',left_on='item_id',right_on='id')
  userItemCountDf=userItemCountDf[userItemCountDf['user_id']==userId].reset_index(drop=True)
  #Componer DataFrame de respuesta
  resultData={'Usuario': [userId]}
  resultDf=pd.DataFrame(resultData)
  resultDf['Dinero Gastado']=pd.to_numeric(userItemsDf['price'], errors='coerce').sum()
  resultDf['% de recomendación']=(userRecommendDf['recommend'].mean()) * 100
  resultDf['Cantidad de Items']=userItemCountDf['items_count']
  result=resultDf.to_dict(orient='records')
  return JSONResponse(content=result)

@app.get("/userforgenre")
def UserForGenre(genero: str):
  return

@app.get("/bestdeveloperyear")
def best_developer_year(año: int): 
  return

@app.get("/developerreviewsanalysis")
def developer_reviews_analysis(desarrolladora: str):
  return