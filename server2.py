from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
import pandas as pd
import datetime
import numpy as np
import re
from dateutil import parser
import json





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
    if isinstance(valor, str):
        # Limpieza básica: quitar espacios y caracteres invisibles
        valor_limpio = valor.strip()

        # Detectar si parece una fecha (evita strings como "123/456/7890")
        if re.match(r"^\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}$", valor_limpio):
            try:
                fecha = parser.parse(valor_limpio, dayfirst=True)
                return fecha.isoformat()
            except (ValueError, OverflowError):
                pass  # No era una fecha válida

        # También puedes intentar parsear fechas con palabras (como "11 Sep 2024")
        try:
            fecha = parser.parse(valor_limpio, dayfirst=True, fuzzy=True)
            return fecha.isoformat()
        except (ValueError, OverflowError):
            pass


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
    print("estamos en el servidorrr")
    try:
        contents = await file.read()
        extension = file.filename.split(".")[-1].lower()

        if extension not in ["xls", "xlsx", "csv"]:
            print("el fichero no excel ni csv")
            return JSONResponse(content={"estado": "error", "detalle": "Formato no soportado"})
        if extension == "csv":
         print("la extension esss csv")
         df = pd.read_csv(BytesIO(contents))
         df = df.applymap(convertir_valor)

         datos_dict = {"csv": df.to_dict(orient="list")}
        else:
            print("la extension essss xlrd o xlsx")
            engine = "xlrd" if extension == "xls" else "openpyxl"
            hojas = pd.read_excel(BytesIO(contents), sheet_name=None, engine=engine)
            datos_dict = {
             nombre_hoja: df.applymap(convertir_valor).to_dict(orient="list")
             for nombre_hoja, df in hojas.items()
            }

           
            
        return JSONResponse(content={"estado": "ok", "datos": datos_dict})

    except Exception as e:
        print("detallerrr error "+str(e))
        return JSONResponse(content={"estado": "error", "detalle": str(e)})

  #      df = pd.read_excel(BytesIO(contents), engine="openpyxl")
   #     if df.empty:
   #       return JSONResponse(content={"estado": "error", "detalle": "El archivo está vacío"})
          
    #    df_convertido = df.applymap(convertir_valor)
   #     datos_dict = df_convertido.to_dict(orient="list")
   #     return JSONResponse(content={"estado": "ok", "datos": datos_dict})

 #   except Exception as e:
   #     JSONResponse(content={"estado": "error", "detalle": str(e)})


    


@app.get("/saludo/")
def saludar():
    return {"mensaje": "Hola mundo"}
