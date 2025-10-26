from datetime import datetime, date
from dateutil import parser
import re
import server2 

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



esfecha=convertir_a_datetime('2025-01-01T00:00:00')
print("convertir_a_datetime funcion " )
print(esfecha)
print("tipo esfecha")
print(type(esfecha))

v1=server2.convertir_valor('2025-01-01T00:00:00')
print(type(v1))
lista=["02/01/2025","02/01/2025","01/01/2025","04/01/2025"]
lista1=['2025-01-01T00:00:00', '2025-02-02T00:00:00', '2025-03-06T00:00:00', '2025-04-07T00:00:00', '2025-05-09T00:00:00']
resultado = list(map(server2.convertir_valor, lista1))

tipo=server2.tipo_mas_frecuente(resultado)
print("tipo de la lista")
print(tipo.__name__)
print(" isinstance(v, (datetime, date))")
print( isinstance(v1, (datetime, date)))

print("v1",v1)
#v=isinstance("01/01/2025", (datetime, date))
#print(v)