import urllib.request
import urllib.parse
import json

LOGIN_URL = "http://127.0.0.1:8000/api/v1/auth/login"
CLIENTS_URL = "http://127.0.0.1:8000/api/v1/clients"
SEARCH_URL = "http://127.0.0.1:8000/api/v1/clients/search"

# 1. Login
data = urllib.parse.urlencode({"username": "admin@demo.com", "password": "password123"}).encode()
req = urllib.request.Request(LOGIN_URL, data=data, method="POST")
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    token = res["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. Get clients
req = urllib.request.Request(CLIENTS_URL, headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    print("TOTAL CLIENTES EN BD:", res["total"])
    print("KEYS DEVUELTAS:", list(res.keys()))
    for c in res["clients"]:
        print(f" -> #{c['id']} {c.get('razon_social')} | Doc: {c.get('numero_fiscal')} | Tel: {c.get('telefono_principal')}")

# 3. Test Search
req = urllib.request.Request(f"{SEARCH_URL}?query=Falcon", headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    print("BUSQUEDA 'Falcon':", len(res["clients"]), "encontrado(s)")

# 4. Test Create with camelCase
new_cust = {
    "razonSocial": "Comercializadora del Centro C.A.",
    "nombreComercial": "ComCentro",
    "numeroFiscal": "J-55443322-1",
    "telefonoPrincipal": "+584120001122",
    "correoPrincipal": "contacto@comcentro.com",
    "direccionFiscal": "Zona Industrial Calle 4",
    "estatus": "Activo"
}
req = urllib.request.Request(CLIENTS_URL, data=json.dumps(new_cust).encode(), headers=headers, method="POST")
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    print("CLIENTE CREADO VIA CAMELCASE:", res["id"], res["razon_social"])
