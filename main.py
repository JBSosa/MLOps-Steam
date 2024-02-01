from fastapi import FastAPI
import pandas as pd
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.get("/developer/{dev}")
def developer(dev: str):
  steamGamesData=pd.read_parquet('steamGames.parquet')
  steamGamesDf=pd.DataFrame(steamGamesData)
  filteredDf=steamGamesDf[steamGamesDf['developer']==dev]
  totalApps=filteredDf.groupby('release_year').size().reset_index(name='Cantidad de Items')
  filteredDf=filteredDf.dropna(subset=['price'])
  freeApps=filteredDf[filteredDf['price']==0].groupby('release_year').size().reset_index(name='free_items')
  result = pd.merge(totalApps, freeApps, on='release_year', how='left').fillna(0)
  result.rename(columns={'release_year': 'Año'}, inplace=True)
  result['Contenido Free'] = ((result['free_items'] / result['Cantidad de Items']) * 100).round(2).astype(str) + '%'
  result=result[['Año','Cantidad de Items','Contenido Free']].reset_index(drop=True)
  result=result.to_dict(orient='records')
  return JSONResponse(content=result)

@app.get("/userdata/{userId}")
def userdata(userId: str):
  userRecommendData=pd.read_parquet('userReviewsExploded.parquet')
  userItemsData=pd.read_parquet('userItemsExploded.parquet')
  userItemCountData=pd.read_parquet('userItemCount.parquet')
  gamePriceData=pd.read_parquet('steamGamesPrice.parquet')
  #Convertir a DataFrame
  userRecommendDf=pd.DataFrame(userRecommendData)
  userItemsDf=pd.DataFrame(userItemsData)
  userItemCountDf=pd.DataFrame(userItemCountData)
  gamePriceDf=pd.DataFrame(gamePriceData)
  #Filtrar por usuario
  userRecommendDf=userRecommendDf[userRecommendDf['user_id']==userId].reset_index(drop=True)
  userItemsDf=userItemsDf[userItemsDf['user_id']==userId].reset_index(drop=True)
  userItemsDf=pd.merge(userItemsDf,gamePriceDf,how='left',on='item_id')
  userItemCountDf=userItemCountDf[userItemCountDf['user_id']==userId].reset_index(drop=True)
  #Componer DataFrame de respuesta
  resultData={'Usuario': [userId]}
  resultDf=pd.DataFrame(resultData)
  resultDf['Dinero Gastado']=pd.to_numeric(userItemsDf['price'], errors='coerce').sum()
  resultDf['% de recomendación']=((userRecommendDf['recommend'].mean()) * 100).round(2).astype(str) + '%'
  resultDf['Cantidad de Items']=userItemCountDf['items_count']
  result=resultDf.to_dict(orient='records')
  return JSONResponse(content=result)

@app.get("/userforgenre/{genre}")
def UserForGenre(genre: str):
  genre=genre.lower()
  gameGenreData=pd.read_parquet('steamGamesGenres.parquet')
  userItemsExplodedData=pd.read_parquet('userItemsExploded.parquet')
  gameGenreDf=pd.DataFrame(gameGenreData)
  userItemsExplodedDf=pd.DataFrame(userItemsExplodedData)
  gameGenreDf['genres']=gameGenreDf['genres'].apply(lambda lst: [element.lower() for element in lst])
  gameGenreDf=gameGenreDf[gameGenreDf['genres'].apply(lambda x: genre in x if isinstance(x, list) else False)]
  gameGenreDf=pd.merge(gameGenreDf[['item_id','release_year']],userItemsExplodedDf,how='left',on='item_id')
  gameGenreDf=gameGenreDf.dropna(subset='playtime')
  userId=gameGenreDf.groupby('user_id')['playtime'].sum().reset_index().sort_values(by='playtime',ascending=False).iloc[0,0]
  gameGenreDf=gameGenreDf[gameGenreDf['user_id']==userId].groupby('release_year')['playtime'].sum().reset_index().sort_values(by='release_year',ascending=False)
  gameGenreDf['playtime']=(gameGenreDf['playtime']/60).round(2)
  gameGenreDf.rename(columns={'release_year': 'Año'}, inplace=True)
  gameGenreDf.rename(columns={'playtime': 'Horas jugadas'}, inplace=True)
  resultPlaytime=gameGenreDf.to_dict(orient='records')
  result={'Usuario con más horas jugadas para Género ' + genre:userId,'Horas jugadas':resultPlaytime}
  return JSONResponse(content=result)

@app.get("/bestdeveloperyear/{year}")
def best_developer_year(year: int):
  userReviewsData=pd.read_parquet('userReviewsExploded.parquet')
  steamGamesDevData=pd.read_parquet('steamGamesDev.parquet')
  userReviewsDf=pd.DataFrame(userReviewsData)
  steamGamesDevDf=pd.DataFrame(steamGamesDevData)
  userReviewsDf = userReviewsDf[(userReviewsDf['recommend'] == True) & 
                               (userReviewsDf['sentiment_analysis'] == 2) & 
                               (userReviewsDf['review_year'] == year)]
  userReviewsDf['review_year']=userReviewsDf['review_year'].astype(int)
  userReviewsDf=userReviewsDf.groupby('item_id')['recommend'].count().reset_index()
  steamGamesDevDf=pd.merge(steamGamesDevDf[['item_id','developer']],userReviewsDf,how='left',on='item_id').sort_values(by='recommend',ascending=False)
  steamGamesDevDf=steamGamesDevDf.groupby('developer')['recommend'].sum().reset_index().sort_values(by='recommend',ascending=False)
  if steamGamesDevDf.iloc[1,1]!=0:
    first=steamGamesDevDf.iloc[0,0]
    second=steamGamesDevDf.iloc[1,0]
    third=steamGamesDevDf.iloc[2,0]
    result=[{'Puesto 1':first},{'Puesto 2':second},{'Puesto 3':third}]
  else:
    result=[{'Puesto 1':None},{'Puesto 2':None},{'Puesto 3':None}]
  return JSONResponse(content=result)

@app.get("/developerreviewsanalysis/{dev}")
def developer_reviews_analysis(dev: str):
  dev=dev.lower()
  userReviewsData=pd.read_parquet('userReviewsExploded.parquet')
  steamGamesDevData=pd.read_parquet('steamGamesDev.parquet')
  userReviewsDf=pd.DataFrame(userReviewsData)
  steamGamesDevDf=pd.DataFrame(steamGamesDevData)
  steamGamesDevDf=steamGamesDevDf[steamGamesDevDf['developer'].str.lower()== dev]
  userReviewsDf=userReviewsDf.groupby('item_id')['sentiment_analysis'].agg([('positive', lambda x: (x == 2).sum()),
    ('negative', lambda x: (x == 0).sum())]).reset_index()
  steamGamesDevDf=pd.merge(steamGamesDevDf,userReviewsDf,how='left',on='item_id')
  steamGamesDevDf=steamGamesDevDf.groupby('developer')[['positive','negative']].sum().reset_index()
  positive=steamGamesDevDf.iloc[0,1].astype(int).astype(str)
  negative=steamGamesDevDf.iloc[0,2].astype(int).astype(str)
  result={steamGamesDevDf.iloc[0,0]:['Negative = ' + negative,'Positive = ' + positive]}
  return JSONResponse(content=result)