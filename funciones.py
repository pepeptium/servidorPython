from datetime import datetime, date
from io import BytesIO
from dateutil import parser
import re
import server2 
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd

def es_fecha(valor) -> bool:
    if isinstance(valor, (datetime, date)):
        return True

    if isinstance(valor, str):
        try:
            parser.parse(valor, dayfirst=True, fuzzy=False)
            return True
        except (ValueError, OverflowError):
            return False

    return False

from datetime import datetime

from datetime import datetime

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

def cargar_excel_con_explorador():
    """
    Abre el explorador de archivos, carga el archivo Excel y devuelve un objeto tipo archivo.
    """
    Tk().withdraw()
    ruta_archivo = askopenfilename(
        title="Selecciona un archivo Excel",
        filetypes=[("Archivos Excel o CSV", "*.xlsx *.xls *.csv")]
    )

    if not ruta_archivo:
        print("No se seleccionó ningún archivo.")
        return None

    return ArchivoSimulado(ruta_archivo)

class ArchivoSimulado:
    def __init__(self, ruta):
        self.filename = ruta.split("/")[-1]
        with open(ruta, "rb") as f:
            self._contenido = f.read()

    async def read(self):
        return self._contenido
    
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
async def probar():
    archivo = cargar_excel_con_explorador()
    if archivo:
        contenido = await archivo.read()
        extension = archivo.filename.split(".")[-1].lower()
        if extension == "csv":
            df = pd.read_csv(BytesIO(contenido))
        else:
            engine = "xlrd" if extension == "xls" else "openpyxl"
            df = pd.read_excel(BytesIO(contenido), engine=engine)
        print(df.head()) 
        
ruta=cargar_excel_con_explorador()


#esfecha=convertir_a_datetime('2025-01-01T00:00:00')
#print("convertir_a_datetime funcion " )
#print(esfecha)
#print(type(esfecha))

#v1=server2.convertir_valor('2025-01-01T00:00:00')
#print(type(v1))
#lista=["02/01/2025","02/01/2025","01/01/2025","04/01/2025"]
#lista1=['2025-01-01T00:00:00', '2025-02-02T00:00:00', '2025-03-06T00:00:00', '2025-04-07T00:00:00', '2025-05-09T00:00:00']
#resultado = list(map(server2.convertir_valor, lista1))

#tipo=server2.tipo_mas_frecuente(resultado)
#print("tipo de la lista")
#print(tipo.__name__)
#print(" isinstance(v, (datetime, date))")
#print( isinstance(v1, (datetime, date)))

#print("v1",v1)

#v=isinstance("01/01/2025", (datetime, date))
#print(v)


