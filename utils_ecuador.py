"""
UTILIDADES ECUADOR - Import Aceros S.A.
Funciones específicas para operaciones en Ecuador

- Validación RUC/Cédula
- Cálculo de dígitos verificadores
- Conversión de fechas locales
- Validación de DAVs
"""

import re
from datetime import datetime

# ========================================
# VALIDACIÓN DE RUC ECUADOR
# ========================================

def validar_ruc_ecuador(ruc):
    """
    Valida si un RUC ecuatoriano es válido
    
    RUC tiene 13 dígitos:
    - Persona Natural: xx xxxxxxxxxx 001
    - Sociedad Privada: xx xxxxxxxxxx 001
    - Sociedad Pública: xx xxxxxxxxxx 0001
    
    Los primeros 2 dígitos son la provincia (01-24, 30)
    """
    
    # Limpiar espacios
    ruc = str(ruc).strip().replace('-', '').replace(' ', '')
    
    # Validar longitud
    if len(ruc) != 13:
        return {
            "valido": False,
            "error": "RUC debe tener 13 dígitos",
            "ruc": ruc
        }
    
    # Validar que sean solo números
    if not ruc.isdigit():
        return {
            "valido": False,
            "error": "RUC debe contener solo números",
            "ruc": ruc
        }
    
    # Validar provincia (primeros 2 dígitos)
    provincia = int(ruc[:2])
    provincias_validas = list(range(1, 25)) + [30]  # 01-24 + 30 (extranjeros)
    
    if provincia not in provincias_validas:
        return {
            "valido": False,
            "error": f"Código de provincia inválido: {provincia}",
            "ruc": ruc
        }
    
    # Tercer dígito determina tipo de RUC
    tercer_digito = int(ruc[2])
    
    if tercer_digito < 6:
        # Persona Natural o Sociedad Privada
        tipo = "Persona Natural" if tercer_digito < 6 else "Sociedad Privada"
        digito_verificador = calcular_digito_verificador_ruc_natural(ruc[:9])
        
        if int(ruc[9]) != digito_verificador:
            return {
                "valido": False,
                "error": "Dígito verificador incorrecto",
                "ruc": ruc,
                "tipo": tipo
            }
    
    elif tercer_digito == 6:
        # Sector Público
        tipo = "Sector Público"
        digito_verificador = calcular_digito_verificador_ruc_publico(ruc[:8])
        
        if int(ruc[8]) != digito_verificador:
            return {
                "valido": False,
                "error": "Dígito verificador incorrecto",
                "ruc": ruc,
                "tipo": tipo
            }
    
    elif tercer_digito == 9:
        # Sociedad Privada
        tipo = "Sociedad Privada"
        digito_verificador = calcular_digito_verificador_ruc_juridico(ruc[:9])
        
        if int(ruc[9]) != digito_verificador:
            return {
                "valido": False,
                "error": "Dígito verificador incorrecto",
                "ruc": ruc,
                "tipo": tipo
            }
    
    else:
        return {
            "valido": False,
            "error": f"Tipo de RUC inválido (tercer dígito: {tercer_digito})",
            "ruc": ruc
        }
    
    return {
        "valido": True,
        "ruc": ruc,
        "tipo": tipo,
        "provincia": provincia,
        "formateado": f"{ruc[:2]}-{ruc[2:10]}-{ruc[10:]}"
    }


def calcular_digito_verificador_ruc_natural(cedula):
    """Calcula dígito verificador para persona natural"""
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    
    for i, coef in enumerate(coeficientes):
        valor = int(cedula[i]) * coef
        suma += valor if valor < 10 else valor - 9
    
    residuo = suma % 10
    return 0 if residuo == 0 else 10 - residuo


def calcular_digito_verificador_ruc_juridico(ruc):
    """Calcula dígito verificador para sociedad privada"""
    coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(ruc[i]) * coeficientes[i] for i in range(9))
    
    residuo = suma % 11
    return 0 if residuo == 0 else 11 - residuo


def calcular_digito_verificador_ruc_publico(ruc):
    """Calcula dígito verificador para sector público"""
    coeficientes = [3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(ruc[i]) * coeficientes[i] for i in range(8))
    
    residuo = suma % 11
    return 0 if residuo == 0 else 11 - residuo


# ========================================
# VALIDACIÓN CÉDULA ECUADOR
# ========================================

def validar_cedula_ecuador(cedula):
    """
    Valida si una cédula ecuatoriana es válida
    Cédula tiene 10 dígitos
    """
    
    cedula = str(cedula).strip().replace('-', '').replace(' ', '')
    
    if len(cedula) != 10:
        return {
            "valido": False,
            "error": "Cédula debe tener 10 dígitos",
            "cedula": cedula
        }
    
    if not cedula.isdigit():
        return {
            "valido": False,
            "error": "Cédula debe contener solo números",
            "cedula": cedula
        }
    
    # Validar provincia
    provincia = int(cedula[:2])
    if provincia not in range(1, 25) and provincia != 30:
        return {
            "valido": False,
            "error": f"Código de provincia inválido: {provincia}",
            "cedula": cedula
        }
    
    # Calcular dígito verificador
    digito_verificador = calcular_digito_verificador_ruc_natural(cedula[:9])
    
    if int(cedula[9]) != digito_verificador:
        return {
            "valido": False,
            "error": "Dígito verificador incorrecto",
            "cedula": cedula
        }
    
    return {
        "valido": True,
        "cedula": cedula,
        "provincia": provincia,
        "formateado": f"{cedula[:2]}-{cedula[2:9]}-{cedula[9]}"
    }


# ========================================
# CÁLCULO DE TRIBUTOS ADUANEROS
# ========================================

def calcular_tributos_importacion_ecuador(valor_fob_usd, partida_arancelaria="7208"):
    """
    Calcula tributos de importación para Ecuador
    
    Parámetros:
    - valor_fob_usd: Valor FOB en dólares
    - partida_arancelaria: Código arancelario (default acero)
    
    Retorna diccionario con breakdown de costos
    """
    
    # Determinar arancel según partida
    aranceles = {
        "7208": 0.05,   # Acero laminado en caliente (5%)
        "7209": 0.05,   # Acero laminado en frío (5%)
        "7210": 0.10,   # Acero galvanizado (10%)
        "7212": 0.05,   # Acero recubierto (5%)
        "7213": 0.05,   # Alambrón (5%)
        "7214": 0.05,   # Barras de acero (5%)
        "7216": 0.15,   # Perfiles de acero (15%)
    }
    
    tasa_arancelaria = aranceles.get(partida_arancelaria[:4], 0.05)
    
    # ARANCEL (Ad Valorem)
    arancel = valor_fob_usd * tasa_arancelaria
    
    # FODINFA (0.5% sobre CIF)
    # Asumimos flete = 10% FOB, seguro = 0.5% FOB
    valor_cif = valor_fob_usd * 1.105
    fodinfa = valor_cif * 0.005
    
    # BASE IMPONIBLE IVA
    base_iva = valor_cif + arancel + fodinfa
    
    # IVA 15% (cambió en Ecuador desde 2024)
    iva = base_iva * 0.15
    
    # TOTAL TRIBUTOS
    total_tributos = arancel + fodinfa + iva
    
    # COSTO LANDED (incluye otros gastos)
    flete_estimado = valor_fob_usd * 0.10
    seguro_estimado = valor_fob_usd * 0.005
    agente_aduanero = 350 + (valor_fob_usd * 0.002)
    almacenaje_puerto = 45 * 5  # 5 días promedio
    transporte_local = 200
    
    otros_gastos = flete_estimado + seguro_estimado + agente_aduanero + almacenaje_puerto + transporte_local
    
    costo_landed = valor_fob_usd + total_tributos + otros_gastos
    
    return {
        "valor_fob_usd": round(valor_fob_usd, 2),
        "partida_arancelaria": partida_arancelaria,
        "tasa_arancelaria_porcentaje": tasa_arancelaria * 100,
        
        # Tributos
        "arancel_usd": round(arancel, 2),
        "fodinfa_usd": round(fodinfa, 2),
        "iva_15_usd": round(iva, 2),
        "total_tributos_usd": round(total_tributos, 2),
        
        # Otros gastos
        "flete_usd": round(flete_estimado, 2),
        "seguro_usd": round(seguro_estimado, 2),
        "agente_aduanero_usd": round(agente_aduanero, 2),
        "almacenaje_usd": round(almacenaje_puerto, 2),
        "transporte_local_usd": round(transporte_local, 2),
        "total_otros_gastos_usd": round(otros_gastos, 2),
        
        # Totales
        "costo_landed_usd": round(costo_landed, 2),
        "incremento_sobre_fob_porcentaje": round((costo_landed - valor_fob_usd) / valor_fob_usd * 100, 1),
        "tributos_porcentaje_fob": round(total_tributos / valor_fob_usd * 100, 1)
    }


# ========================================
# FORMATO FECHAS ECUADOR
# ========================================

def formatear_fecha_ecuador(fecha_str):
    """
    Convierte fecha de formato SENAE/SRI a formato legible
    
    Formatos aceptados:
    - "2026-01-19" → "19 de enero de 2026"
    - "19/01/2026" → "19 de enero de 2026"
    """
    
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    
    # Detectar formato
    if "-" in fecha_str:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    elif "/" in fecha_str:
        fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
    else:
        return fecha_str
    
    return f"{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}"


# ========================================
# VALIDACIÓN NÚMERO DAV
# ========================================

def validar_dav_ecuador(numero_dav):
    """
    Valida formato de número DAV (Declaración Aduanera de Valor)
    
    Formato: XXX-YYYY-DD-NNNNNN
    - XXX: Código aduana (018 = Guayaquil, 010 = Quito)
    - YYYY: Año
    - DD: Tipo documento (10 = Importación consumo)
    - NNNNNN: Número secuencial
    """
    
    patron = r"^\d{3}-\d{4}-\d{2}-\d{6}$"
    
    if not re.match(patron, numero_dav):
        return {
            "valido": False,
            "error": "Formato DAV inválido. Formato correcto: XXX-YYYY-DD-NNNNNN",
            "dav": numero_dav
        }
    
    partes = numero_dav.split("-")
    codigo_aduana = partes[0]
    año = partes[1]
    tipo_doc = partes[2]
    secuencial = partes[3]
    
    # Validar código aduana
    aduanas = {
        "010": "Quito",
        "018": "Guayaquil",
        "020": "Cuenca",
        "024": "Manta",
        "030": "Tulcán",
        "040": "Esmeraldas",
        "050": "Machala"
    }
    
    if codigo_aduana not in aduanas:
        return {
            "valido": False,
            "error": f"Código de aduana inválido: {codigo_aduana}",
            "dav": numero_dav
        }
    
    # Validar año
    año_actual = datetime.now().year
    if int(año) > año_actual or int(año) < 2015:
        return {
            "valido": False,
            "error": f"Año inválido: {año}",
            "dav": numero_dav
        }
    
    return {
        "valido": True,
        "dav": numero_dav,
        "aduana": aduanas[codigo_aduana],
        "año": año,
        "tipo_documento": "Importación para consumo" if tipo_doc == "10" else "Otro",
        "secuencial": secuencial
    }


# ========================================
# CONVERSIÓN DE MONTOS
# ========================================

def convertir_monto_a_palabras(monto):
    """
    Convierte un monto en dólares a palabras (para facturas)
    Ejemplo: 1234.56 → "MIL DOSCIENTOS TREINTA Y CUATRO DÓLARES CON 56/100"
    """
    
    # Esta es una versión simplificada
    # Para producción, usar librería num2words con locale español
    
    try:
        from num2words import num2words
        
        dolares = int(monto)
        centavos = int((monto - dolares) * 100)
        
        palabras = num2words(dolares, lang='es', to='currency')
        resultado = f"{palabras.upper()} CON {centavos:02d}/100"
        
        return resultado
    
    except ImportError:
        # Fallback si no está instalado num2words
        return f"${monto:,.2f} USD"


if __name__ == "__main__":
    # Tests
    print("=== VALIDACIONES ECUADOR ===\n")
    
    # Test RUC
    print("1. VALIDACIÓN RUC:")
    ruc_test = "1791251237001"
    resultado = validar_ruc_ecuador(ruc_test)
    print(f"   RUC: {ruc_test}")
    print(f"   Válido: {resultado['valido']}")
    if resultado['valido']:
        print(f"   Tipo: {resultado['tipo']}")
        print(f"   Formato: {resultado['formateado']}")
    
    # Test Cédula
    print("\n2. VALIDACIÓN CÉDULA:")
    cedula_test = "1714567890"
    resultado = validar_cedula_ecuador(cedula_test)
    print(f"   Cédula: {cedula_test}")
    print(f"   Válido: {resultado['valido']}")
    if resultado['valido']:
        print(f"   Formato: {resultado['formateado']}")
    
    # Test Tributos
    print("\n3. CÁLCULO TRIBUTOS:")
    tributos = calcular_tributos_importacion_ecuador(500000, "7208")
    print(f"   FOB: ${tributos['valor_fob_usd']:,.0f}")
    print(f"   Arancel: ${tributos['arancel_usd']:,.0f}")
    print(f"   IVA 15%: ${tributos['iva_15_usd']:,.0f}")
    print(f"   Total Tributos: ${tributos['total_tributos_usd']:,.0f}")
    print(f"   Landed Cost: ${tributos['costo_landed_usd']:,.0f}")
    print(f"   Incremento: {tributos['incremento_sobre_fob_porcentaje']}%")
    
    # Test DAV
    print("\n4. VALIDACIÓN DAV:")
    dav_test = "018-2026-10-000891"
    resultado = validar_dav_ecuador(dav_test)
    print(f"   DAV: {dav_test}")
    print(f"   Válido: {resultado['valido']}")
    if resultado['valido']:
        print(f"   Aduana: {resultado['aduana']}")
        print(f"   Año: {resultado['año']}")
    
    # Test Fecha
    print("\n5. FORMATO FECHA:")
    fecha = formatear_fecha_ecuador("2026-01-19")
    print(f"   2026-01-19 → {fecha}")
