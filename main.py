from fastapi import FastAPI
import pandas as pd
from fastapi.responses import JSONResponse
import pyarrow

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/developer/{dev}")
def developer(dev: str):
    # Se leen los datos y se crea el DataFrame
    steamGamesDf = pd.read_parquet('data/steamGames.parquet')
    # Se crea un DataFrame filtrado de acuerdo al developer
    filteredDf = steamGamesDf[steamGamesDf['developer'].str.lower() == dev.lower()]
    # Se guardan los valores del total de juegos y la cantidad de juegos gratuitos agrupados por año
    totalApps = filteredDf.groupby('release_year').size().reset_index(name = 'Cantidad de Items')
    filteredDf = filteredDf.dropna(subset = ['price'])
    freeApps = filteredDf[filteredDf['price'] == 0].groupby('release_year').size().reset_index(name = 'free_items')
    # Se crea el DataFrame resultado con la cantidad de juegos, el porcentaje de estos que son gratuítos, y el año
    result = pd.merge(totalApps, freeApps, on = 'release_year', how = 'left').fillna(0)
    result.rename(columns = {'release_year': 'Año'}, inplace = True)
    result['Contenido Free'] = ((result['free_items'] / result['Cantidad de Items']) * 100).round(2).astype(str) + '%'
    result = result[['Año','Cantidad de Items','Contenido Free']].reset_index(drop = True)
    result = result.to_dict(orient = 'records')
    return JSONResponse(content = result)

@app.get("/userdata/{userId}")
def userData(userId: str):
    # Se leen los datos y se crea el DataFrame
    userRecommendDf = pd.read_parquet('data/userReviewsExploded.parquet')
    userItemsDf = pd.read_parquet('data/userItemsExploded.parquet')
    userItemCountDf = pd.read_parquet('data/userItemCount.parquet')
    steamGamesPriceDf = pd.read_parquet('data/steamGamesPrice.parquet')
    # Se crean DataFrame filtrando por usuario
    userRecommendDf = userRecommendDf[userRecommendDf['user_id'] == userId].reset_index(drop = True)
    userItemsDf = userItemsDf[userItemsDf['user_id'] == userId].reset_index(drop = True)
    userItemsDf = pd.merge(userItemsDf,steamGamesPriceDf,how = 'left',on = 'item_id')
    userItemCountDf = userItemCountDf[userItemCountDf['user_id'] == userId].reset_index(drop = True)
    # Se compone el DataFrame de respuesta conteniendo el ID de usuariom, el dinero gastado de acuerdo a sus ítems, el porcentaje de recomendación y la cantidad de ítems
    resultData = {'Usuario': [userId]}
    resultDf = pd.DataFrame(resultData)
    resultDf['Dinero Gastado'] = pd.to_numeric(userItemsDf['price'], errors = 'coerce').sum()
    resultDf['% de recomendación'] = ((userRecommendDf['recommend'].mean()) * 100).round(2).astype(str) + '%'
    resultDf['Cantidad de Items'] = userItemCountDf['items_count']
    result = resultDf.to_dict(orient = 'records')
    return JSONResponse(content = result)

@app.get("/userforgenre/{genre}")
def userForGenre(genre: str):
    # Se leen los datos y se crea el DataFrame
    steamGamesGenresDf = pd.read_parquet('data/steamGamesGenresExploded.parquet')
    userItemsExplodedDf = pd.read_parquet('data/userItemsExploded.parquet')
    # Se filtra el DataFrame buscando el género solicitado entre los géneros del juego
    steamGamesGenresDf = steamGamesGenresDf[steamGamesGenresDf['genres'].str.lower() == genre.lower()]
    # Se une el DataFrame con los géneros al DataFrame que contiene a los usuarios con sus ítems
    steamGamesGenresDf = pd.merge(steamGamesGenresDf[['item_id','release_year']],userItemsExplodedDf,how = 'left',on = 'item_id')
    # Se descartan todas las instancias que no contengan tiempo de juego
    steamGamesGenresDf = steamGamesGenresDf.dropna(subset = 'playtime')
    # Se agrupan de acuerdo al ID de usuario teniendo en cuenta el tiempo total de juego y se recupera al usuario que posee mayor cantidad de tiempo acumulado
    userId = steamGamesGenresDf.groupby('user_id')['playtime'].sum().reset_index().sort_values(by = 'playtime',ascending = False).iloc[0,0]
    # Se filtra el DataFrame de acuerdo al usuario recuperado, se agrupa conforme al año de lanzamiento de los juegos y se suma el tiempo jugado
    steamGamesGenresDf = steamGamesGenresDf[steamGamesGenresDf['user_id'] == userId].groupby('release_year')['playtime'].sum().reset_index().sort_values(by = 'release_year',ascending = False)
    # Una vez se tiene toda la información, se transforman los datos y se crea el DataFrame de respuesta
    steamGamesGenresDf['playtime'] = (steamGamesGenresDf['playtime']/60).round(2)
    steamGamesGenresDf.rename(columns = {'release_year': 'Año'}, inplace = True)
    steamGamesGenresDf.rename(columns = {'playtime': 'Horas jugadas'}, inplace = True)
    resultPlaytime = steamGamesGenresDf.to_dict(orient = 'records')
    result = {'Usuario con más horas jugadas para género ' + genre:userId,'Horas':resultPlaytime}
    return JSONResponse(content = result)

@app.get("/bestdeveloperyear/{year}")
def bestDeveloperYear(year: int):
    # Se cargan los datos y se crean los DataFrame
    userReviewsExplodedDf = pd.read_parquet('data/userReviewsExploded.parquet')
    steamGamesDevDf = pd.read_parquet('data/steamGamesDev.parquet')
    # Se filtra el DataFrame de acuerdo al año solicitado eliminando los juegos no recomendados, y con análisis de sentimiento neutral o negativo
    userReviewsExplodedDf = userReviewsExplodedDf[(userReviewsExplodedDf['recommend'] == True) & 
                                            (userReviewsExplodedDf['sentiment_analysis'] == '2') & 
                                            (userReviewsExplodedDf['review_year'] == year)]
    userReviewsExplodedDf['review_year'] = userReviewsExplodedDf['review_year'].astype(int)
    # Se agrupan las reseñas de acuedo al ID del juego sumando la cantidad de recomendaciones
    userReviewsExplodedDf = userReviewsExplodedDf.groupby('item_id')['recommend'].count().reset_index()
    # Se crea un DataFrame que contenga el ID del juego, el desarrollador y la suma de recomendaciones
    steamGamesDevDf = pd.merge(steamGamesDevDf[['item_id','developer']],userReviewsExplodedDf,how = 'left',on = 'item_id').sort_values(by = 'recommend',ascending = False)
    # Se agrupa de acuerdo al desarrollador y a la suma de recomendaciones
    steamGamesDevDf = steamGamesDevDf.groupby('developer')['recommend'].sum().reset_index().sort_values(by = 'recommend',ascending = False)
    # Se revisa que el primer valor no sea 0 para descartar años en los que no se tenga registro de las reseñas y se recuperan los tres primeros lugares
    if steamGamesDevDf.iloc[1,1]!= 0:
        first = steamGamesDevDf.iloc[0,0]
        second = steamGamesDevDf.iloc[1,0]
        third = steamGamesDevDf.iloc[2,0]
        result = [{'Puesto 1':first},{'Puesto 2':second},{'Puesto 3':third}]
    else:
        result = [{'Puesto 1':None},{'Puesto 2':None},{'Puesto 3':None}]
    return JSONResponse(content = result)

@app.get("/developerreviewsanalysis/{dev}")
def developerReviewsAnalysis(dev: str):
    # Se cargan los datos y se crean los DataFrame
    userReviewsExplodedDf = pd.read_parquet('data/userReviewsExploded.parquet')
    steamGamesDevDf = pd.read_parquet('data/steamGamesDev.parquet')
    # Se filtra el DataFrame de desarrolladores de acuerdo al desarrollador solicitado
    steamGamesDevDf = steamGamesDevDf[steamGamesDevDf['developer'].str.lower() == dev.lower()]
    # Se agrupa el DataFrame de reseñas de acuerdo al ID del juego agregando una columna para la suma de comentarios positivos y otra para la de negativos
    userReviewsExplodedDf = userReviewsExplodedDf.groupby('item_id')['sentiment_analysis'].agg([('positive', lambda x: (x == '2').sum()),
        ('negative', lambda x: (x == '0').sum())]).reset_index()
    # Se crea el DataFrame de respuesta
    steamGamesDevDf = pd.merge(steamGamesDevDf,userReviewsExplodedDf,how = 'left',on = 'item_id')
    steamGamesDevDf = steamGamesDevDf.groupby('developer')[['positive','negative']].sum().reset_index()
    positive = steamGamesDevDf.iloc[0,1].astype(int).astype(str)
    negative = steamGamesDevDf.iloc[0,2].astype(int).astype(str)
    result = {steamGamesDevDf.iloc[0,0]:['Negative = ' + negative,'Positive = ' + positive]}
    return JSONResponse(content = result)

@app.get("/recommenditem/{itemId}")
def recommendItem(itemId: str):
    # Se cargan los datos y se crea el DataFrame
    itemSimDf = pd.read_parquet('data/itemSim.parquet')
    counter = 1
    result = {'Aquí hay juegos similares a': itemId,'1':'','2':'','3':'','4':'','5':''}
    # Se buscan los ítems con mayor similitud y se añaden al resultado
    for item in itemSimDf.sort_values(by = itemId, ascending = False).index[1:6]:
        result[str(counter)] = item
        counter +=1
    return JSONResponse(content = result)