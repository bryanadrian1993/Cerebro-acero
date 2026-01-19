import pandas as pd
import random

# CATÁLOGO OFICIAL - Import Aceros S.A. 2021
# Productos según catálogo oficial: Catalogo-importaceros-2021-web.pdf
# Empresa: +20 años distribuyendo acero en Ecuador
# Web: www.importaceros.com | Quito - Ecuador

productos = [
    # ===== VIGAS ESTRUCTURALES =====
    {"id": "VIGA-IPE-80", "nombre": "Viga IPE 80", "categoria": "Vigas"},
    {"id": "VIGA-IPE-100", "nombre": "Viga IPE 100", "categoria": "Vigas"},
    {"id": "VIGA-IPE-120", "nombre": "Viga IPE 120", "categoria": "Vigas"},
    {"id": "VIGA-IPE-140", "nombre": "Viga IPE 140", "categoria": "Vigas"},
    {"id": "VIGA-IPE-160", "nombre": "Viga IPE 160", "categoria": "Vigas"},
    {"id": "VIGA-IPE-180", "nombre": "Viga IPE 180", "categoria": "Vigas"},
    {"id": "VIGA-IPE-200", "nombre": "Viga IPE 200", "categoria": "Vigas"},
    {"id": "VIGA-IPE-240", "nombre": "Viga IPE 240", "categoria": "Vigas"},
    {"id": "VIGA-IPE-300", "nombre": "Viga IPE 300", "categoria": "Vigas"},
    {"id": "VIGA-HEB-100", "nombre": "Viga HEB 100", "categoria": "Vigas"},
    {"id": "VIGA-HEB-120", "nombre": "Viga HEB 120", "categoria": "Vigas"},
    {"id": "VIGA-HEB-140", "nombre": "Viga HEB 140", "categoria": "Vigas"},
    {"id": "VIGA-HEB-160", "nombre": "Viga HEB 160", "categoria": "Vigas"},
    {"id": "VIGA-HEB-200", "nombre": "Viga HEB 200", "categoria": "Vigas"},
    {"id": "VIGA-HEB-240", "nombre": "Viga HEB 240", "categoria": "Vigas"},
    {"id": "VIGA-HEB-300", "nombre": "Viga HEB 300", "categoria": "Vigas"},
    {"id": "VIGA-IPN-80", "nombre": "Viga IPN 80", "categoria": "Vigas"},
    {"id": "VIGA-IPN-100", "nombre": "Viga IPN 100", "categoria": "Vigas"},
    {"id": "VIGA-IPN-120", "nombre": "Viga IPN 120", "categoria": "Vigas"},
    {"id": "VIGA-IPN-160", "nombre": "Viga IPN 160", "categoria": "Vigas"},
    {"id": "VIGA-UPN-80", "nombre": "Viga UPN 80", "categoria": "Vigas"},
    {"id": "VIGA-UPN-100", "nombre": "Viga UPN 100", "categoria": "Vigas"},
    {"id": "VIGA-UPN-120", "nombre": "Viga UPN 120", "categoria": "Vigas"},
    {"id": "VIGA-UPN-160", "nombre": "Viga UPN 160", "categoria": "Vigas"},
    {"id": "VIGA-UPN-200", "nombre": "Viga UPN 200", "categoria": "Vigas"},
    
    # ===== TUBERÍAS INOXIDABLES =====
    {"id": "TUBO-INOX-304-1/2", "nombre": "Tubo Redondo Inox 304 1/2\"", "categoria": "Tuberías"},
    {"id": "TUBO-INOX-304-3/4", "nombre": "Tubo Redondo Inox 304 3/4\"", "categoria": "Tuberías"},
    {"id": "TUBO-INOX-304-1", "nombre": "Tubo Redondo Inox 304 1\"", "categoria": "Tuberías"},
    {"id": "TUBO-INOX-304-1.5", "nombre": "Tubo Redondo Inox 304 1 1/2\"", "categoria": "Tuberías"},
    {"id": "TUBO-INOX-304-2", "nombre": "Tubo Redondo Inox 304 2\"", "categoria": "Tuberías"},
    {"id": "TUBO-INOX-316-1", "nombre": "Tubo Redondo Inox 316 1\"", "categoria": "Tuberías"},
    {"id": "TUBO-INOX-316-1.5", "nombre": "Tubo Redondo Inox 316 1 1/2\"", "categoria": "Tuberías"},
    {"id": "TUBO-INOX-316-2", "nombre": "Tubo Redondo Inox 316 2\"", "categoria": "Tuberías"},
    {"id": "TUBO-CUAD-INOX-20x20", "nombre": "Tubo Cuadrado Inox 20x20mm", "categoria": "Tuberías"},
    {"id": "TUBO-CUAD-INOX-25x25", "nombre": "Tubo Cuadrado Inox 25x25mm", "categoria": "Tuberías"},
    {"id": "TUBO-CUAD-INOX-30x30", "nombre": "Tubo Cuadrado Inox 30x30mm", "categoria": "Tuberías"},
    {"id": "TUBO-CUAD-INOX-40x40", "nombre": "Tubo Cuadrado Inox 40x40mm", "categoria": "Tuberías"},
    
    # ===== TUBERÍAS GALVANIZADAS =====
    {"id": "TUBO-GALV-1/2", "nombre": "Tubo Galvanizado 1/2\"", "categoria": "Tuberías"},
    {"id": "TUBO-GALV-3/4", "nombre": "Tubo Galvanizado 3/4\"", "categoria": "Tuberías"},
    {"id": "TUBO-GALV-1", "nombre": "Tubo Galvanizado 1\"", "categoria": "Tuberías"},
    {"id": "TUBO-GALV-1.5", "nombre": "Tubo Galvanizado 1 1/2\"", "categoria": "Tuberías"},
    {"id": "TUBO-GALV-2", "nombre": "Tubo Galvanizado 2\"", "categoria": "Tuberías"},
    {"id": "TUBO-GALV-3", "nombre": "Tubo Galvanizado 3\"", "categoria": "Tuberías"},
    {"id": "TUBO-GALV-4", "nombre": "Tubo Galvanizado 4\"", "categoria": "Tuberías"},
    
    # ===== PLANCHAS INOXIDABLES =====
    {"id": "PLANCHA-INOX-304-2B", "nombre": "Plancha Inoxidable 304 2B", "categoria": "Planchas"},
    {"id": "PLANCHA-INOX-304-BA", "nombre": "Plancha Inoxidable 304 BA", "categoria": "Planchas"},
    {"id": "PLANCHA-INOX-304-N4", "nombre": "Plancha Inoxidable 304 N°4", "categoria": "Planchas"},
    {"id": "PLANCHA-INOX-316-2B", "nombre": "Plancha Inoxidable 316 2B", "categoria": "Planchas"},
    {"id": "PLANCHA-INOX-316-BA", "nombre": "Plancha Inoxidable 316 BA", "categoria": "Planchas"},
    {"id": "PLANCHA-INOX-430-2B", "nombre": "Plancha Inoxidable 430 2B", "categoria": "Planchas"},
    
    # ===== PLANCHAS GALVANIZADAS =====
    {"id": "PLANCHA-GALV-G60", "nombre": "Plancha Galvanizada G60", "categoria": "Planchas"},
    {"id": "PLANCHA-GALV-G90", "nombre": "Plancha Galvanizada G90", "categoria": "Planchas"},
    
    # ===== PLANCHAS NEGRAS =====
    {"id": "PLANCHA-NEGRO-LAF", "nombre": "Plancha Negra LAF (Laminada en Frío)", "categoria": "Planchas"},
    {"id": "PLANCHA-NEGRO-LAC", "nombre": "Plancha Negra LAC (Laminada en Caliente)", "categoria": "Planchas"},
    {"id": "PLANCHA-NAVAL-A36", "nombre": "Plancha Naval A36", "categoria": "Planchas"},
    
    # ===== PERFILERÍA =====
    {"id": "ANGULAR-25x25", "nombre": "Angular 25x25mm", "categoria": "Perfilería"},
    {"id": "ANGULAR-30x30", "nombre": "Angular 30x30mm", "categoria": "Perfilería"},
    {"id": "ANGULAR-40x40", "nombre": "Angular 40x40mm", "categoria": "Perfilería"},
    {"id": "ANGULAR-50x50", "nombre": "Angular 50x50mm", "categoria": "Perfilería"},
    {"id": "PLATINA-INOX-25x3", "nombre": "Platina Inox 25x3mm", "categoria": "Perfilería"},
    {"id": "PLATINA-INOX-30x3", "nombre": "Platina Inox 30x3mm", "categoria": "Perfilería"},
    {"id": "PLATINA-INOX-40x5", "nombre": "Platina Inox 40x5mm", "categoria": "Perfilería"},
    {"id": "CANAL-U-80", "nombre": "Canal U 80mm", "categoria": "Perfilería"},
    {"id": "CANAL-U-100", "nombre": "Canal U 100mm", "categoria": "Perfilería"},
    
    # ===== LOSA DECK =====
    {"id": "LOSA-DECK-0.75", "nombre": "Losa Deck 0.75mm", "categoria": "Losa Deck"},
    {"id": "LOSA-DECK-0.90", "nombre": "Losa Deck 0.90mm", "categoria": "Losa Deck"},
    {"id": "LOSA-DECK-1.00", "nombre": "Losa Deck 1.00mm", "categoria": "Losa Deck"},
    
    # ===== CUBIERTAS =====
    {"id": "CUBIERTA-GALV-TRAPEZOIDAL", "nombre": "Cubierta Galvanizada Trapezoidal", "categoria": "Cubiertas"},
    {"id": "CUBIERTA-GALV-ONDULADA", "nombre": "Cubierta Galvanizada Ondulada", "categoria": "Cubiertas"},
    {"id": "CUBIERTA-PREPINTADA", "nombre": "Cubierta Prepintada", "categoria": "Cubiertas"},
    
    # ===== ACCESORIOS =====
    {"id": "ACC-PASAMANOS-INOX", "nombre": "Accesorios Pasamanos Inox", "categoria": "Accesorios"},
    {"id": "ACC-VIDRIO-TEMPLADO", "nombre": "Accesorios para Vidrio Templado", "categoria": "Accesorios"},
    {"id": "PERNOS-AUTOPERF", "nombre": "Pernos Autoperforantes", "categoria": "Accesorios"},
    {"id": "TRASLUCIDOS", "nombre": "Translúcidos", "categoria": "Accesorios"}
]

datos = []

print("Generando inventario simulado...")

for prod in productos:
    stock_minimo = random.randint(50, 200)
    # A propósito hacemos que algunos tengan poco stock para que salga la alerta roja
    stock_actual = random.randint(10, 300) 
    
    datos.append({
        "sku": prod["id"],
        "producto": prod["nombre"],
        "stock_actual": stock_actual,
        "stock_minimo": stock_minimo,
        "categoria": prod["categoria"]
    })

# Convertir a DataFrame y guardar
df = pd.DataFrame(datos)
df.to_csv("inventario_simulado.csv", index=False)

print("✅ Archivo 'inventario_simulado.csv' creado con éxito.")