from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from io import BytesIO
import pandas as pd
import re
from dateutil import parser
from typing import Dict, List, Any, Type
from collections import Counter
import math
from datetime import datetime, date
from dateutil import parser
import json








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
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()

    if isinstance(valor, str):
        valor_limpio = valor.strip()

        # Traducir meses en español a inglés
       
        formatos = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y",
        "%m/%d/%Y %H:%M:%S"
    ]
    
        for formato in formatos:
                try:
                    return datetime.strptime(valor, formato)
                except ValueError:
                    continue
        MESES_ES = {
            "enero": "January", "febrero": "February", "marzo": "March", "abril": "April",
            "mayo": "May", "junio": "June", "julio": "July", "agosto": "August",
            "septiembre": "September", "octubre": "October", "noviembre": "November", "diciembre": "December"
        }

        for esp, eng in MESES_ES.items():
            patron = r"\b" + re.escape(esp) + r"\b"
            if re.search(patron, valor_limpio, flags=re.IGNORECASE):
                valor_limpio = re.sub(patron, eng, valor_limpio, flags=re.IGNORECASE)
                break  # solo reemplaza el primero que encuentre
        # Intentar parsear directamente sin regex previa
        try:
            fecha = parser.parse(valor_limpio, dayfirst=True, fuzzy=False)
            return fecha.isoformat()
        except (ValueError, OverflowError):
            pass

    return valor


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
            print("hoja importada en servidor")
            print(datos_dict)

          #falta convertir datos
        analisis = analizar_datos_dict(datos_dict)
   
       # print("analisisss", json.dumps(analisis, indent=2, ensure_ascii=False))
       # df_convertido = datos_dict.applymap(convertir_valor)
 
       
        content = {
                "estado": "ok",
                "datos": datos_dict,
                "&&estadistica&&": analisis
                    }
        return JSONResponse(content)
        
            
      

    except Exception as e:
        print("detallerrr error "+str(e))
        return JSONResponse(content={"estado": "error", "detalle": str(e)})
    

def convertir_a_datetime(valor: str):
    """
    Intenta convertir un string (incluyendo ISO 8601) a datetime.
    Si no es posible, devuelve el string original.
    """
    if not isinstance(valor, str):
        return valor

    # 1️⃣ Intentar formato ISO 8601 (Python 3.7+)
    try:
        return datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        pass

    # 2️⃣ Intentar formatos comunes (incluyendo con 'T')
    formatos = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y",
        "%m/%d/%Y %H:%M:%S"
    ]
    
    for formato in formatos:
        try:
            return datetime.strptime(valor, formato)
        except ValueError:
            continue
    
    # 3️⃣ Si no se pudo convertir, devolver el string original
    return valor

def tipo_mas_frecuente(valores: List[Any]) -> Type:
    """
    Devuelve el tipo de dato más frecuente en la lista de valores.
    Ignora los valores None.
    """
    tipo_contador = Counter()

    for v in valores:
        if v is None:
            continue
        elif isinstance(v, (datetime, date)):
            tipo_contador[datetime] += 1
        elif isinstance(v, bool):
            tipo_contador[bool] += 1
        elif isinstance(v, int):
            tipo_contador[int] += 1
        elif isinstance(v, float):
            tipo_contador[float] += 1
        elif isinstance(v, str):
            tipo_contador[str] += 1
        else:
            tipo_contador[type(v)] += 1  # fallback

    tipo_dominante, _ = tipo_contador.most_common(1)[0]
    return tipo_dominante
def es_nulo(v: Any, tipo_dominante: Type) -> bool:
    if v is None:
        return True
    if isinstance(v, float) and math.isnan(v):
        return True
    if isinstance(v, str) and v.strip().lower() in ["", "null", "nan"]:
        return True
    if not isinstance(v, tipo_dominante):
        return True
    return False

def analizar_datos_dict(datos_dict: Dict[str, Dict[str, List[Any]]]) ->Dict[str, Dict[str, Dict[str, Any]]]:
    resultado = {}

    for nombre_hoja, columnas in datos_dict.items():
        hoja_resultado = {}

        for nombre_columna, valores in columnas.items():

            tipoColumna=tipo_mas_frecuente(valores)
            valores_validos = [v for v in valores if not es_nulo(v, tipoColumna)]
            nulos = len(valores) - len(valores_validos)
            analisis = {
                "tipo_dominante": tipoColumna.__name__,
                "nulos": nulos,
                "unicos": len(set(valores_validos))

            }
            if tipoColumna in [int, float]:
                n = len(valores_validos)
                media = sum(valores_validos) / n if n > 0 else None
                varianza = sum((x - media) ** 2 for x in valores_validos) / n if n > 0 else None
                std = math.sqrt(varianza) if varianza is not None else None

                analisis.update({
                    "count": n,
                    "mean": media,
                    "std": std,
                    "min": min(valores_validos) if valores_validos else None,
                    "max": max(valores_validos) if valores_validos else None,
                })

            elif tipoColumna in [datetime, date]:
                fechas = [v for v in valores_validos if isinstance(v, (datetime, date))]
                fechas_ordenadas = sorted(fechas)
                rango = (fechas_ordenadas[-1] - fechas_ordenadas[0]).days if len(fechas_ordenadas) >= 2 else None

                # Distribuciones
                por_dia = Counter(f.day for f in fechas)
                por_mes = Counter(f.month for f in fechas)
                por_anio = Counter(f.year for f in fechas)
                por_semana = Counter(f.strftime("%A") for f in fechas)

                analisis.update({
                    "count": len(fechas),
                    "min_date": fechas_ordenadas[0].isoformat() if fechas_ordenadas else None,
                    "max_date": fechas_ordenadas[-1].isoformat() if fechas_ordenadas else None,
                    "range_days": rango,
                    "por_dia_mes": dict(por_dia),
                    "por_mes": dict(por_mes),
                    "por_anio": dict(por_anio),
                    "por_dia_semana": dict(por_semana)
                })

            

            elif tipoColumna is bool:
                contador = Counter(valores_validos)
                analisis.update({
                    "count": len(valores_validos),
                    "true": contador.get(True, 0),
                    "false": contador.get(False, 0),
                })
            elif tipoColumna is str:
                contador = Counter(valores_validos)
                mas_comun = contador.most_common(1)[0] if contador else (None, 0)

                analisis.update({
                    "count": len(valores_validos),
                    "unique": len(set(valores_validos)),
                    "most_common": mas_comun[0],
                    "freq": mas_comun[1],
                })

            hoja_resultado[nombre_columna] = analisis

        resultado[nombre_hoja] = hoja_resultado
    
    return resultado






@app.get("/saludo/")
def saludar():
    return {"mensaje": "Hola mundo"}

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

