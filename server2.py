from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import io
import pandas as pd
import datetime

from io import BytesIO
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["http://localhost:65263/#/servidor","http://localhost:56951" ,"http://localhost:60160"], # O usa ["http://localhost:63946"] para más seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def convertir_valor(valor):
    if pd.isna(valor):
        return ""
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float)):
        return int(valor) if valor == int(valor) else float(valor)
    if isinstance(valor, (datetime.datetime, datetime.date)):
        return valor.isoformat()
    return str(valor)


@app.post("/analizar_excel/")
async def analizar_excel(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), engine="openpyxl")

        # Ejemplo de análisis: contar filas y columnas
        resumen = {
            "n_filas": df.shape[0],
            "n_columnas": df.shape[1],
            "columnas": df.columns.tolist()
        }

        return {"estado": "ok", "resumen": resumen}
    
    except Exception as e:
        return {"estado": "error", "detalle": str(e)}

@app.post("/analizar_excel_tipado/")
async def analizar_excel_tipado(file: UploadFile = File(...)):
   
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), engine="openpyxl")
        if df.empty:
          return {"estado": "error", "detalle": "El archivo está vacío"}
        resultado = {"prueba":"pepito de los palotes"}
    except Exception as e:
        return {"estado": "error", "detalle": str(e)}
@app.get("/saludo/")
def saludar():
    return {"mensaje": "Hola mundo"}




   



    
  
    

   # for col in df.columns:
   #     nombre = str(df.iloc[0, col])
    #    datos = [convertir_valor(df.iloc[row, col]) for row in range(1, len(df))]
     #   resultado[f"columna_{col}"] = {
      #      "nombre": nombre,
      #      "datos": datos
      #  }

