from datetime import datetime, date
from dateutil import parser
import re
import server2 

def es_fecha(valor) -> bool:
    if isinstance(valor, (datetime, date)):
        return True

    if isinstance(valor, str):
        valor_limpio = valor.strip()

        # Traducir meses en español a inglés (si aplica)
        MESES_ES = {
            "enero": "January", "febrero": "February", "marzo": "March", "abril": "April",
            "mayo": "May", "junio": "June", "julio": "July", "agosto": "August",
            "septiembre": "September", "octubre": "October", "noviembre": "November", "diciembre": "December"
        }
        for esp, eng in MESES_ES.items():
            patron = r"\b" + re.escape(esp) + r"\b"
            if re.search(patron, valor_limpio, flags=re.IGNORECASE):
                valor_limpio = re.sub(patron, eng, valor_limpio, flags=re.IGNORECASE)
                break

        # Intentar parsear como fecha
        try:
            parser.parse(valor_limpio, dayfirst=True, fuzzy=False)
            return True
        except (ValueError, OverflowError):
            return False

    return False

esfecha=es_fecha("01/01/2025")
v1=server2.convertir_valor("01/01/2025")
print(type(v1))
lista=["02/01/2025","02/01/2025","01/01/2025","04/01/2025"]
resultado = list(map(server2.convertir_valor, lista))

tipo=server2.tipo_mas_frecuente(resultado)
print("tipo de la lista")
print(tipo.__name__)
print(" isinstance(v, (datetime, date))")
print( isinstance(v1, (datetime, date)))

print("v1",v1)
#v=isinstance("01/01/2025", (datetime, date))
#print(v)