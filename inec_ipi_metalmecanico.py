# Este archivo contiene datos extraídos del PDF "PRESENTACION_RESULTADOS_IPI-M_2020_09.pdf"
# Los datos corresponden a las incidencias mensuales y anuales para el sector metalmecánico
# para septiembre de 2020.

# Nota: Estos datos son muy limitados y no representan la serie histórica completa.
# Para un análisis completo, se necesita el archivo de datos tabulares (Excel o CSV)
# del "Banco de Datos Abiertos" del INEC.

# Incidencias mensuales (septiembre 2020) - Página 9 y 12 del PDF
incidencias_mensuales = {
    "Productos metalicos, maquinaria y equipo": {
        "valor": 0.961,
        "desglose": {
            "Productos metalicos fabricados, excepto maquinaria y equipo": 8.431,
            "Equipo de transporte": 5.463,
            "Maquinaria y aparatos electricos": 0.262
        }
    }
}

# Incidencias anuales (septiembre 2020) - Página 15 y 18 del PDF
incidencias_anuales = {
    "Productos metalicos, maquinaria y equipo": {
        "desglose": {
            "Productos metalicos fabricados, excepto maquinaria y equipo": 11.971,
            "Equipo de transporte": 11.967,
            "Metales Basicos": 6.655,
            "Maquinaria para usos generales": 2.663,
            "Maquinaria y aparatos electricos": 0.405,
        }
    }
}

# Divisiones CIIU - Incidencias mensuales (página 13)
incidencias_mensuales_ciiu = {
    "Fabricacion de productos elaborados de metal, excepto...": 1.673
}

# Divisiones CIIU - Incidencias anuales (página 19)
incidencias_anuales_ciiu = {
    "Fabricacion de productos elaborados de metal, excepto maquinaria y equipo": 2.614,
    "Fabricacion de metales comunes": 1.454
}

def obtener_datos_pdf():
    """
    Retorna los datos extraídos del PDF del IPI-M de septiembre 2020.
    """
    return {
        "incidencias_mensuales": incidencias_mensuales,
        "incidencias_anuales": incidencias_anuales,
        "incidencias_mensuales_ciiu": incidencias_mensuales_ciiu,
        "incidencias_anuales_ciiu": incidencias_anuales_ciiu
    }

if __name__ == "__main__":
    datos = obtener_datos_pdf()
    print("Datos extraídos del PDF:")
    import json
    print(json.dumps(datos, indent=4))
