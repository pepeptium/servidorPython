from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
from io import BytesIO

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O usa ["http://localhost:63946"] para más seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
