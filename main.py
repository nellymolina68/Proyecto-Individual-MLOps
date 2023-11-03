import pandas as pd
from fastapi import FastAPI
import uvicorn 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

app = FastAPI(
    title='Proyecto MLOps',
    description='Creación Api',
    swagger_ui_parameters={"tryItOutEnabled": True}
)

df_final_f1 = None
df_final_f2 = None
df_final_f3_4 = None
df_final_f5 = None
df_final_ML = None
similarity_matrix = None
@app.on_event("startup")
async def load_data():
    global df_final_f1
    global df_final_f2
    global df_final_f3_4
    global df_final_f5
    global df_final_ML
    global similarity_matrix
    # Leer el archivo csv desde la ruta relativa y crear el dataframe global
    df_fc1 = pd.read_csv('funcion_1.csv')
    df_final_f1 = pd.DataFrame(df_fc1)
    df_fc2 = pd.read_csv('funcion_2.csv')
    df_final_f2 = pd.DataFrame(df_fc2)
    df_fc3 = pd.read_csv('funcion_3_4.csv')
    df_final_f3_4 = pd.DataFrame(df_fc3)
    df_fc5 = pd.read_csv('funcion_5.csv')
    df_final_f5 = pd.DataFrame(df_fc5)
    df_fc6 = pd.read_csv('Machine_learning.csv')
    df_final_ML = pd.DataFrame(df_fc6)

    num_cols = ['Hours_Played', 'release_year', 'sentiment_analysis']
    cat_cols = ['genres', 'app_name']

    #Crear un transformador de columnas para procesar las columnas numéricas y categóricas
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', num_cols),
            ('cat', OneHotEncoder(), cat_cols)])

     #Ajustar y transformar los datos con el preprocesador
    X_transformed = preprocessor.fit_transform(df_final_ML)

     #Calcular la matriz de similitud del coseno
    similarity_matrix = cosine_similarity(X_transformed)

print(df_final_f1)
@app.get("/")
async def index():
    return ('Construyendo mi Api')

@app.get("/about")
async def about():
    return ('Mi primera Api')
# Funcion 1
@app.get("/playtime/{genero}")
async def get_playtime(genero: str):
    # Convertir el género a minúsculas
    genero = genero.lower()
    
    # Convertir los géneros del dataframe a minúsculas
    df_final_f1['genres'] = df_final_f1['genres'].str.lower()
    
    # Verificar si el género existe en el dataframe
    if genero not in df_final_f1['genres'].unique():
        return "No se encontró el género solicitado"
    
    # Filtrar el dataframe por el género especificado
    df = df_final_f1[df_final_f1['genres'] == genero]
    
    # Encontrar el año con más horas jugadas
    max_year = df.loc[df['Hours_Played'].idxmax(), 'release_year']
    
    return {"Año de lanzamiento con más horas jugadas para Género " + genero : int(max_year)}
# Funcion 2
@app.get("/UserForGenre/{genero}")
async def get_UserForGenre(genero: str):

      # Convertir el género a minúsculas
    genero = genero.lower()
    
    # Convertir los géneros del dataframe a minúsculas
    df_final_f2['genres'] = df_final_f2['genres'].str.lower()
      # Filtrar el DataFrame por el género especificado
    df_genero = df_final_f2[df_final_f2['genres'] == genero]

    if df_genero.empty:
        return "No se encuentró el género solicitado."

    # Obtener el usuario con más horas jugadas para ese género
    usuario_mas_horas = df_genero[df_genero['Hours_Played'] == df_genero['Hours_Played'].max()]['user_id'].values[0]

    # Agrupar por año y sumar las horas jugadas
    horas_por_anio = df_genero.groupby('release_year')['Hours_Played'].sum().reset_index()

    # Ordenar las filas por año
    horas_por_anio = horas_por_anio.sort_values(by='release_year')

    
    # Redondear los valores en la lista de acumulación de horas jugadas a 2 decimales
    horas_por_anio['Hours_Played'] = horas_por_anio['Hours_Played'].round(2)

    # Crear una lista de diccionarios con la acumulación de horas jugadas por año
    lista_horas_por_anio = [{"Año": anio, "Horas": horas} for anio, horas in zip(horas_por_anio['release_year'], horas_por_anio['Hours_Played'])]

    # Crear el diccionario de retorno
    resultado = {"Usuario con más horas jugadas para " + genero: usuario_mas_horas, "Horas jugadas": lista_horas_por_anio}

    return resultado
# Funcion 3 
@app.get("/usersrecommend/{year}")
async def UsersRecommend(year: int):
    # Verifica si el año está en el dataframe
    if year not in df_final_f3_4['Year_Posted'].unique():
        return "No se encuentró el año solicitado"
    
    # Filtra el dataframe por el año y las recomendaciones
    df_filtered = df_final_f3_4[(df_final_f3_4['Year_Posted'] == year) & (df_final_f3_4['Recommend'] == True)]
    
    # Cuenta las recomendaciones por juego
    recommend_counts = df_filtered['title'].value_counts()
    
    # Obtiene el top 3 de juegos más recomendados
    top_3 = recommend_counts.nlargest(3)
    
    # Crea una lista para almacenar los resultados
    results = []
    
    # Itera sobre el top 3 y añade cada juego a los resultados
    for i, (game, count) in enumerate(top_3.items(), start=1):
        results.append({f"Puesto {i}": game})
    
    return results
# Funcion 4
@app.get("/usersnotrecommend/{year}")
async def UsersNotRecommend(year: int):
    # Verifica si el año está en el dataframe
    if year not in df_final_f3_4['Year_Posted'].unique():
        return "No se encuentró el año solicitado"
    
    # Filtra el dataframe por el año y las no recomendaciones
    df_filtered = df_final_f3_4[(df_final_f3_4['Year_Posted'] == year) & (df_final_f3_4['Recommend'] == False)]
    
    # Cuenta las no recomendaciones por juego
    not_recommend_counts = df_filtered['title'].value_counts()
    
    # Obtiene el top 3 de juegos menos recomendados
    top_3 = not_recommend_counts.nlargest(3)
    
    # Crea una lista para almacenar los resultados
    results = []
    
    # Itera sobre el top 3 y añade cada juego a los resultados
    for i, (game, count) in enumerate(top_3.items(), start=1):
        results.append({f"Puesto {i}": game})
    
    return results


# Funcion 5
@app.get("/sentiment_analysis/{year}")
async def sentiment_analysis(year: int):

    # Verifica si el año está en el dataframe
    if year not in df_final_f5['release_year'].unique():
        return "No se encuentró el año solicitado"
    # Filtrar el dataframe por el año dado
    df_año = df_final_f5[df_final_f5['release_year'] == year]
    
     # Contar los valores de 'sentiment_analysis'
    sentiment_counts = df_año['sentiment_analysis'].value_counts()
    
    # Crear un diccionario para almacenar los resultados
    results = {}
    
    # Mapear los valores de 'sentiment_analysis' a sus respectivas categorías
    for i in sentiment_counts.index:
        if i == 0:
            results['Negative'] = int(sentiment_counts[i])
        elif i == 1:
            results['Neutral'] = int(sentiment_counts[i])
        elif i == 2:
            results['Positive'] = int(sentiment_counts[i])
    
    return results


 #Funcion 6
@app.get("/recomendacion_juego/{item_name}")
async def recomendacion_juego(item_name: str):
     # Utilizar la matriz de similitud del coseno precargada

     # Verificar si el juego ingresado está en los datos
     if item_name not in df_final_ML['Item_name'].values:
         return "El juego no se encontró en los datos solicitados"
    
     # Obtener el índice del juego en la muestra
     item_id = df_final_ML[df_final_ML['Item_name'] == item_name].index[0]
    
     # Obtener las puntuaciones de similitud para el ítem dado
     similarity_scores = list(enumerate(similarity_matrix[item_id]))
    
     # Ordenar las puntuaciones de similitud en orden descendente
     similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
     # Obtener los índices de los juegos más similares
     similar_items = [i[0] for i in similarity_scores if df_final_ML['Item_name'].iloc[i[0]] != item_name]
    
     # Devolver los nombres de los 5 juegos más similares sin duplicados
     recommended_games = []
     for item in similar_items:
         game_name = df_final_ML['Item_name'].iloc[item]
         if game_name not in recommended_games:
             recommended_games.append(game_name)
         if len(recommended_games) == 5:
             break
    
     return "Los 5 juegos más recomendados para el juego {} son: {}".format(item_name, recommended_games)


# Ejecutar la aplicación con Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
