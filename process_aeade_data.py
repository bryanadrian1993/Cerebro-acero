import pandas as pd

def process_aeade_sales_data(file_path="Boletin-de-Prensa-Diciembre-2025_20260128_102856_38314145_extracted.csv", save_to_csv=False):
    """
    Procesa el archivo CSV de ventas de vehículos de AEADE.

    Args:
        file_path (str): Ruta al archivo CSV extraído del boletín de AEADE.
        save_to_csv (bool): Si es True, guarda el DataFrame procesado en un CSV.

    Returns:
        pd.DataFrame: DataFrame procesado con los datos de ventas de vehículos.
                      Retorna un DataFrame vacío si ocurre un error.
    """
    try:
        df = pd.read_csv(file_path)

        # La estructura del CSV indica que hay varias tablas sin encabezados claros.
        # Necesitamos identificar las filas que corresponden a ventas por marca, por combustible, y totales.

        # Identificar la sección de ventas por marca
        # Buscar la primera aparición de 'KIA' o una marca de vehículo típica
        idx_kia = df[df['Marca'].astype(str).str.contains('KIA', case=False, na=False)].first_valid_index()
        # Buscar la fila 'Total' para la sección de ventas por marca
        idx_total_marca = df[df['Marca'].astype(str).str.contains('Total', case=False, na=False)].first_valid_index()

        if idx_kia is None or idx_total_marca is None:
            raise ValueError("No se pudo identificar la sección de ventas por marca en el CSV.")

        # Extraer la tabla de ventas por marca
        df_marcas = df.loc[idx_kia:idx_total_marca].copy()
        df_marcas.columns = ['marca', 'dic_24', 'dic_25', 'ene_dic_24', 'ene_dic_25']
        df_marcas = df_marcas[df_marcas['marca'].astype(str).str.contains('OTRAS MARCAS|Total', case=False, na=False) == False] # Quitar 'Otras Marcas' y 'Total' si se van a analizar individualmente
        
        # Convertir columnas numéricas
        for col in ['dic_24', 'dic_25', 'ene_dic_24', 'ene_dic_25']:
            df_marcas[col] = pd.to_numeric(df_marcas[col], errors='coerce')
        df_marcas.dropna(subset=['marca'], inplace=True) # Eliminar filas sin marca

        # --- Identificar la sección de ventas por combustible ---
        # Buscar la fila 'GASOLINA'
        idx_gasolina = df[df['Marca'].astype(str).str.contains('GASOLINA', case=False, na=False)].first_valid_index()
        # Buscar la fila 'Total' para la sección de ventas por combustible
        idx_total_combustible = df.loc[idx_gasolina:][df.loc[idx_gasolina:]['Marca'].astype(str).str.contains('Total', case=False, na=False)].first_valid_index()
        idx_total_combustible = idx_gasolina + idx_total_combustible # Ajustar el índice a la original

        if idx_gasolina is None or idx_total_combustible is None:
            st.warning("No se pudo identificar la sección de ventas por tipo de combustible en el CSV.")
            df_combustible = pd.DataFrame()
        else:
            df_combustible = df.loc[idx_gasolina:idx_total_combustible].copy()
            df_combustible.columns = ['tipo_combustible', 'dic_24', 'dic_25', 'ene_dic_24', 'ene_dic_25']
            df_combustible = df_combustible[df_combustible['tipo_combustible'].astype(str).str.contains('Total', case=False, na=False) == False]
            for col in ['dic_24', 'dic_25', 'ene_dic_24', 'ene_dic_25']:
                df_combustible[col] = pd.to_numeric(df_combustible[col], errors='coerce')
            df_combustible.dropna(subset=['tipo_combustible'], inplace=True)

        # --- Identificar la sección de ventas de motos (o la siguiente gran tabla) ---
        # Asumiendo que hay un separador o un conjunto de NaN antes de esta tabla.
        # Voy a buscar el patrón de tener 5 columnas de datos, similar a las anteriores
        # Y que la primera columna no sea una marca de auto ya procesada.
        idx_motos = df[df['Marca'].astype(str).str.contains('SHINERAY', case=False, na=False)].first_valid_index()
        # Buscar la siguiente fila 'Total' si existe, o el final del archivo
        idx_end_motos = df.loc[idx_motos:][df.loc[idx_motos:]['Marca'].astype(str).str.contains('Total', case=False, na=False)].first_valid_index()
        
        if idx_motos is None:
            df_motos = pd.DataFrame()
        else:
            # Si idx_end_motos es None, significa que no hay un "Total" específico para motos,
            # así que tomamos desde idx_motos hasta el final donde haya datos.
            if idx_end_motos is None:
                df_motos = df.loc[idx_motos:].copy()
            else:
                df_motos = df.loc[idx_motos : idx_motos + idx_end_motos].copy()

            df_motos.columns = ['marca_moto', 'dic_24', 'dic_25', 'ene_dic_24', 'ene_dic_25'] # Renombrar a 5 columnas
            df_motos = df_motos.iloc[:, :5] # Asegurarse de tomar solo las 5 primeras columnas
            df_motos = df_motos[df_motos['marca_moto'].astype(str).str.contains('Total|OTRAS MARCAS', case=False, na=False) == False]
            for col in ['dic_24', 'dic_25', 'ene_dic_24', 'ene_dic_25']:
                df_motos[col] = pd.to_numeric(df_motos[col], errors='coerce')
            df_motos.dropna(subset=['marca_moto'], inplace=True)


        # Consolidar en un diccionario para fácil acceso
        processed_data = {
            "ventas_por_marca": df_marcas,
            "ventas_por_combustible": df_combustible,
            "ventas_motos": df_motos
        }

        if save_to_csv:
            for key, df_data in processed_data.items():
                if not df_data.empty:
                    output_file = f"aeade_{key}_diciembre_2025.csv"
                    df_data.to_csv(output_file, index=False, encoding='utf-8')
                    print(f"Datos de {key} guardados en '{output_file}'")
        
        return processed_data

    except Exception as e:
        print(f"Ocurrió un error al procesar el archivo CSV de AEADE: {e}")
        return {"ventas_por_marca": pd.DataFrame(), "ventas_por_combustible": pd.DataFrame(), "ventas_motos": pd.DataFrame()}

if __name__ == "__main__":
    aeade_data = process_aeade_sales_data(save_to_csv=True)
    if not aeade_data["ventas_por_marca"].empty:
        print("\nPrimeras 5 filas de ventas por marca:")
        print(aeade_data["ventas_por_marca"].head().to_string())
    
    if not aeade_data["ventas_por_combustible"].empty:
        print("\nPrimeras 5 filas de ventas por combustible:")
        print(aeade_data["ventas_por_combustible"].head().to_string())

    if not aeade_data["ventas_motos"].empty:
        print("\nPrimeras 5 filas de ventas de motos:")
        print(aeade_data["ventas_motos"].head().to_string())
