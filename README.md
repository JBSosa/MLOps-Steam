# MLOps-Steam

## Introducción

Este proyecto simula las funciones de un ingeniero MLOps, que combina las responsabilidades de un ingeniero de datos y un científico de datos, para la plataforma internacional de videojuegos Steam. La tarea consiste en desarrollar un Producto Mínimo Viable utilizando datos proporcionados, con el objetivo de implementar una API en un servicio en la nube. El producto final debe incluir la aplicación de dos modelos de Machine Learning: en primer lugar, un análisis de sentimientos de los comentarios de los usuarios de los juegos, y en segundo lugar, la capacidad de recomendar juegos basándose en el nombre de un juego y/o en los gustos específicos de un usuario.

## Contexto

Valve Corporation desarrolló Steam como una plataforma de distribución digital de videojuegos, lanzada en septiembre de 2003. Inicialmente concebida para proporcionar actualizaciones automáticas a los juegos de Valve, la plataforma se expandió para incluir juegos de terceros. Con más de 325 millones de usuarios y un catálogo que supera los 25.000 juegos, Steam ha desempeñado un papel significativo en la industria del entretenimiento digital. Es relevante señalar que las cifras proporcionadas por SteamSpy se remontan hasta el año 2017, ya que a principios de 2018, Steam modificó la forma en que se obtienen las estadísticas, lo que limita la disponibilidad de datos más precisos.

## Datos

Para este proyecto se proporcionaron tres archivos JSON:

* **australian_user_reviews.json** es un dataset que contiene los comentarios que los usuarios realizaron sobre los juegos que consumen, además de datos adicionales como si recomiendan o no ese juego, emoticones de gracioso y estadísticas de si el comentario fue útil o no para otros usuarios. También presenta el id del usuario que comenta con su url del perfil y el id del juego que comenta.

* **australian_users_items.json** es un dataset que contiene información sobre los juegos que juegan todos los usuarios, así como el tiempo acumulado que cada usuario jugó a un determinado juego.

* **output_steam_games.json** es un dataset que contiene datos relacionados con los juegos en sí, como los título, el desarrollador, los precios, características técnicas, etiquetas, entre otros datos.

## Tareas desarrolladas

### Transformaciones

Se llevó a cabo el proceso de Extracción, Transformación y Carga (ETL) de los tres conjuntos de datos proporcionados. Dos de estos conjuntos estaban anidados, lo que significa que contenían columnas con diccionarios o listas de diccionarios. Se implementaron diversas estrategias para transformar las claves de esos diccionarios en columnas independientes. Posteriormente, se procedió a completar valores nulos en variables esenciales para el proyecto y se eliminaron columnas con una cantidad significativa de valores nulos o que no aportaban al proyecto, con el objetivo de optimizar el rendimiento de la API y considerando las restricciones de almacenamiento en el despliegue. Para llevar a cabo estas transformaciones, se hizo uso de la biblioteca Pandas.

Los detalles del ETL se puede ver en [ETL](https://github.com/JBSosa/MLOps-Steam/blob/main/Notebooks/ETL.ipynb).

### Feature engineering

Para cumplir con la solicitud de aplicar un análisis de sentimiento a los comentarios de los usuarios en este proyecto, se ha introducido una nueva columna denominada 'sentiment_analysis'. Esta columna sustituye a la que originalmente contenía los comentarios, clasificando los sentimientos de los mismos de acuerdo con la siguiente escala:

* 0 si es malo,
* 1 si es neutral o esta sin review
* 2 si es positivo.

En este proyecto, centrado en la realización de una prueba de concepto, se ha implementado un análisis de sentimiento básico mediante Vader, una biblioteca de procesamiento de lenguaje natural (NLP) en Python. El propósito de esta metodología es asignar un valor numérico a un texto, específicamente a los comentarios dejados por los usuarios para un juego determinado, con el fin de representar si el sentimiento expresado en el texto es negativo, neutral o positivo.

La metodología toma como entrada una revisión de texto, utiliza Vader para calcular la polaridad de sentimiento y clasifica la revisión como negativa, neutral o positiva según la polaridad calculada. En este caso, se han considerado las polaridades por defecto del modelo, que utiliza umbrales de -0.05 y 0.05. Las polaridades por debajo de -0.05 se clasifican como negativas, por encima de 0.05 como positivas, y las polaridades entre ambos umbrales se consideran neutrales.

Además, con el objetivo de optimizar los tiempos de respuesta de las consultas en la API y considerando las limitaciones de almacenamiento en el servicio de nube para el despliegue de la API, se han creado dataframes auxiliares para cada una de las funciones solicitadas. Estos dataframes auxiliares se han almacenado en formato parquet, que proporciona una compresión y codificación eficiente de los datos.

Todos los detalles del desarrollo se pueden ver en la Jupyter Notebook [Sentiment_Analysis](https://github.com/JBSosa/MLOps-Steam/blob/main/Notebooks/Sentiment_Analysis.ipynb).

### Análisis exploratorio de los datos

Se llevó a cabo un Análisis Exploratorio de Datos (EDA) sobre los tres conjuntos de datos sometidos al proceso de Extracción, Transformación y Carga (ETL). El objetivo principal fue identificar las variables que podrían ser utilizadas en la creación del modelo de recomendación. Para llevar a cabo este análisis, se empleó la biblioteca Pandas para la manipulación de datos, así como las librerías Matplotlib y Seaborn para la visualización.

Específicamente para el modelo de recomendación, se decidió construir un dataframe específico que incluyera el identificador del usuario que realizó los comentarios, los nombres de los juegos a los que se les realizaron comentarios y una columna de calificación que se generó mediante la combinación del análisis de sentimiento y las recomendaciones de juegos. Este enfoque permitirá utilizar estas variables clave en la creación del modelo de recomendación.

El desarrollo de este análisis se encuentra en la Jupyter Notebook [EDA](https://github.com/JBSosa/MLOps-Steam/blob/main/Notebooks/EDA.ipynb)

### Modelo de aprendizaje automático

Se ha desarrollado un modelo de recomendación que genera listas de 5 juegos, ya sea ingresando el nombre de un juego. En el primer enfoque, el modelo se basa en una relación ítem-ítem, evaluando la similitud de un juego con el resto y recomendando aquellos juegos que son más similares. En el segundo enfoque, el modelo emplea un filtro usuario-juego, identificando usuarios similares y recomendando juegos que hayan gustado a esos usuarios afines.

Ambos modelos se han implementado utilizando algoritmos basados en la memoria, específicamente abordando el problema del filtrado colaborativo. Estos algoritmos utilizan toda la base de datos para encontrar usuarios similares al usuario activo, es decir, aquellos para los cuales se desea realizar recomendaciones. Se emplean las preferencias de usuarios similares para predecir las valoraciones del usuario activo.

Para medir la similitud entre los juegos (itemSimilarity), se ha aplicado la similitud del coseno. Esta métrica, comúnmente utilizada en sistemas de recomendación y análisis de datos, evalúa la similitud entre dos conjuntos de datos o elementos. Se calcula mediante el coseno del ángulo entre los vectores que representan dichos datos o elementos, proporcionando una medida cuantitativa de su similitud.

El desarrollo para la creación de los dos modelos se presenta en la Jupyter Notebook [Machine_Learning](https://github.com/JBSosa/MLOps-Steam/blob/main/Notebooks/Machine_Learning.ipynb).

### Desarrollo de API

Para el desarrolo de la API se decidió utilizar el framework FastAPI, creando las siguientes funciones:

* **developer**: Esta función recibe como parámetro 'developer', que es la empresa desarrolladora del juego, y devuelve la cantidad de items que desarrolla dicha empresa y el porcentaje de contenido Free por año por sobre el total que desarrolla.
    * **Endpoint**: /developer/{dev}

* **userData**: Esta función tiene por parámentro 'userId' y devulve la cantidad de dinero gastado por el usuario, el porcentaje de recomendaciones que realizó sobre la cantidad de reviews que se analizan y la cantidad de items que consume el mismo.
    * **Endpoint**: /userdata/{userId}

* **userForGenre**: Esta función recibe como parámetro el género de un videojuego y devuelve el top 5 de los usuarios con más horas de juego en el género ingresado, indicando el id del usuario y el url de su perfil.
    * **Endpoint**: /userforgenre/{genre}

* **bestDeveloperYear**: En esta función se ingresa un año de consulta y devuelve el top 3 de desarrolladores con juegos MÁS recomendados por usuarios para el año dado.
    * **Endpoint**: /bestdeveloperyear/{year}

* **developerReviewsAnalysis**: Esta función recibe como parámetro un desarrollador y devuelve un diccionario con el nombre del desarrollador como llave y una lista con la cantidad total de registros de reseñas de usuarios que se encuentren categorizados con un análisis de sentimiento como valor positivo o negativo.
    * **Endpoint**: /developerreviewsanalysis/{dev}

* **recommendItem**: Esta función recibe como parámetro el nombre de un juego y devuelve una lista con 5 juegos recomendados similares al ingresado.
    * **Endpoint**: /recommenditem/{itemId}

El desarrollo de las funciones de consultas generales se puede ver en la Jupyter Notebook [Funciones_API](https://github.com/JBSosa/MLOps-Steam/blob/main/Notebooks/Funciones_API.ipynb).

El código para generar la API se encuentra en el archivo [main.py](https://github.com/JBSosa/MLOps-Steam/blob/main/main.py). En caso de querer ejecutar la API desde localHost se deben seguir los siguientes pasos:

- Clonar el proyecto haciendo `git clone https://github.com/JBSosa/MLOps-Steam.git`.
- Preparación del entorno de trabajo en Visual Studio Code:
    * Crear entorno `Python -m venv env`
    * Ingresar al entorno haciendo `venv\Scripts\activate`
    * Instalar dependencias con `pip install -r requirements.txt`
- Ejecutar el archivo main.py desde consola activando uvicorn. Para ello, hacer `uvicorn main:app --reload`
- Hacer Ctrl + clic sobre la dirección `http://XXX.X.X.X:XXXX` (se muestra en la consola).
- Ingresar a cualquiera de los endpoints mencioneados previamente.

### Deployment

Para el despliegue de la API, se optó por la plataforma Render, que constituye una nube unificada para la creación y ejecución de aplicaciones y sitios web. Esta plataforma facilita el despliegue automático desde GitHub, siguiendo los siguientes pasos:

- Se generó un servicio nuevo  en `render.com`, conectado al presente repositorio y utilizando Docker como Runtime.
- Finalmente, el servicio queda corriendo en [https://mlops-steam-dpiy.onrender.com/](https://mlops-steam-dpiy.onrender.com).

### Video

En este [Google Drive](https://drive.google.com/drive/folders/1dq9PX_LicSvEaXvryloWqhqPbisvLe-D?usp=drive_link) se encuentra un video explica brevemente este proyecto mostrando el funcionamiento de la API.