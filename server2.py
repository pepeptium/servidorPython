from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
import pandas as pd
import datetime
import numpy as np


from io import BytesIO
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"], # O usa ["http://localhost:63946"] para más seguridad
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
          return JSONResponse(content={"estado": "error", "detalle": "El archivo está vacío"})
        
        df_convertido = df.applymap(convertir_valor)
        datos_dict = df_convertido.to_dict(orient="list")
        return JSONResponse(content={"estado": "ok", "datos": datos_dict})

    except Exception as e:
        JSONResponse(content={"estado": "error", "detalle": str(e)})

    


@app.get("/saludo/")
def saludar():
    return {"mensaje": "Hola mundo"}
