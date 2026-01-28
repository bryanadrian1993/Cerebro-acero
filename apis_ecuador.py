import pandas as pd
import streamlit as st
import requests
import zipfile
import io
import os
import glob

# URL estable del API del Banco Mundial para descargar los datos de inflación (IPC % anual)
URL_INFLACION_BANCO_MUNDIAL = "https://api.worldbank.org/v2/en/indicator/FP.CPI.TOTL.ZG?downloadformat=csv"

@st.cache_data(ttl=86400) # Cache por 24 horas
def obtener_inflacion_anual_banco_mundial():
    """
    Descarga, descomprime y procesa los datos de inflación anual de Ecuador
    desde el API del Banco Mundial.

    Returns:
        pandas.DataFrame: Un DataFrame con 'año' e 'inflacion_pct'.
                          Retorna un DataFrame vacío si ocurre un error.
    """
    try:
        # 1. Descargar el archivo ZIP
        response = requests.get(URL_INFLACION_BANCO_MUNDIAL)
        response.raise_for_status()  # Lanza un error si la descarga falla

        # 2. Descomprimir en memoria
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            # Encontrar el archivo CSV dentro del ZIP (generalmente el que no es de metadatos)
            csv_filename = None
            for name in zf.namelist():
                if 'API_FP.CPI.TOTL.ZG' in name and 'Metadata' not in name:
                    csv_filename = name
                    break
            
            if not csv_filename:
                raise ValueError("No se encontró el archivo CSV de datos en el ZIP.")

            with zf.open(csv_filename) as f:
                # 3. Leer el CSV
                # Los archivos del BM tienen 4 filas de metadatos al inicio
                df = pd.read_csv(f, skiprows=4)

        # 4. Procesar y limpiar los datos
        # Filtrar solo para Ecuador
        df_ecuador = df[df['Country Code'] == 'ECU'].copy()

        # "Derretir" el DataFrame para pasar de formato ancho a largo
        # De: | Country | 2000 | 2001 | ...
        # A:  | Country | Year | Value |
        df_long = df_ecuador.melt(
            id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'],
            var_name='año',
            value_name='inflacion_pct'
        )

        # Limpieza final
        df_final = df_long[['año', 'inflacion_pct']].copy()
        df_final.dropna(subset=['inflacion_pct'], inplace=True)
        df_final['año'] = pd.to_numeric(df_final['año'])
        
        df_final = df_final.sort_values(by='año').reset_index(drop=True)

        return df_final

    except Exception as e:
        st.error(f"Error al obtener datos del Banco Mundial: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=86400) # Cache por 24 horas
def obtener_ipco_historico_local():
    """
    Lee los archivos de Excel del IPCO desde la carpeta local 'data_ipco',
    los procesa y los combina en una única serie de tiempo.

    Returns:
        pandas.DataFrame: Un DataFrame con 'fecha' e 'ipco_general'.
                          Retorna un DataFrame vacío si ocurre un error.
    """
    try:
        search_path = os.path.join('data_ipco', '*indice_general*.xlsx')
        general_files = glob.glob(search_path)

        if not general_files:
            st.warning("No se encontró el archivo '...indice_general...' en la carpeta 'data_ipco'.")
            return pd.DataFrame()

        # Usar el primer archivo encontrado que coincida
        file_path = general_files[0]

        df = pd.read_excel(
            file_path,
            sheet_name='DATOS GRAF',
            header=None,
            usecols=[1, 2] # Columnas B y C
        )
        
        df.columns = ['fecha', 'ipco_general']

        # Limpieza de datos
        df.dropna(inplace=True)
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df['ipco_general'] = pd.to_numeric(df['ipco_general'], errors='coerce')
        df.dropna(subset=['fecha', 'ipco_general'], inplace=True)

        df_final = df.sort_values(by='fecha').reset_index(drop=True)
        
        return df_final

    except Exception as e:
        st.error(f"Error al procesar el archivo local del IPCO: {e}")
        return pd.DataFrame()


def process_ipi_data(file_path="1. Indice Nacional.csv", save_to_csv=True):
    """
    Procesa el archivo CSV del IPI-M para extraer datos del sector metalmecánico,
    los transforma a formato largo y opcionalmente los guarda en un CSV.

    Args:
        file_path (str): Ruta al archivo CSV '1. Indice Nacional.csv'.
        save_to_csv (bool): Si es True, guarda el DataFrame procesado en un CSV.

    Returns:
        pd.DataFrame: DataFrame con los datos filtrados del sector metalmecánico en formato largo.
                      Retorna un DataFrame vacío si ocurre un error.
    """
    try:
        # Cargar el archivo CSV. Es probable que necesitemos especificar el delimitador y la codificación.
        df = pd.read_csv(file_path, encoding='latin1', delimiter=',', skiprows=5)

        # Renombrar columnas para mayor claridad
        new_columns = []
        for col in df.columns:
            if 'CIIU' in col:
                new_columns.append('ciiu')
            elif 'Descripci' in col:
                new_columns.append('descripcion')
            elif 'Nivel' in col:
                new_columns.append('nivel')
            else:
                new_columns.append(col.lower().replace('-', '_').replace('.', ''))
        df.columns = new_columns
        
        # Identificar las filas relevantes para el sector metalmecánico
        metalmecanico_keywords = [
            "metal", "metales", "maquinaria", "equipo", "fabricacion", "productos primarios"
        ]

        # Filtrar filas que contengan alguna de las palabras clave en la columna 'descripcion'
        if 'descripcion' not in df.columns:
            raise KeyError("La columna 'descripcion' no se encontró después de renombrar.")

        metalmecanico_df = df[
            df['descripcion'].astype(str).str.contains('|'.join(metalmecanico_keywords), case=False, na=False)
        ].copy()

        # Las columnas de datos son las que representan los meses
        date_columns = [col for col in metalmecanico_df.columns if col not in ['nivel', 'ciiu', 'descripcion']]

        # Convertir las columnas de datos a tipo numérico, forzando errores a NaN
        for col in date_columns:
            metalmecanico_df[col] = pd.to_numeric(metalmecanico_df[col], errors='coerce')

        # Transformar de formato ancho a formato largo
        df_long = metalmecanico_df.melt(
            id_vars=['nivel', 'ciiu', 'descripcion'],
            value_vars=date_columns,
            var_name='fecha',
            value_name='ipi_valor'
        )

        # Convertir la columna 'fecha' a formato de fecha
        def parse_date(date_str):
            month_map = {
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
                'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
            }
            parts = date_str.split('_')
            month = month_map.get(parts[0])
            year = '20' + parts[1]
            if month and year:
                return pd.to_datetime(f"{year}-{month}-01")
            return pd.NaT
            
        df_long['fecha'] = df_long['fecha'].apply(parse_date)

        # Eliminar filas con fechas no válidas o valores IPI nulos
        df_long.dropna(subset=['fecha', 'ipi_valor'], inplace=True)

        # Ordenar por CIIU y fecha
        df_long.sort_values(by=['ciiu', 'fecha'], inplace=True)

        if save_to_csv:
            output_file = "ipi_metalmecanico_historico_ciiu.csv"
            df_long.to_csv(output_file, index=False, encoding='utf-8')
            st.success(f"Datos del sector metalmecánico guardados en '{output_file}'")

        return df_long

    except FileNotFoundError:
        st.error(f"Error: El archivo '{file_path}' no se encontró.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo CSV: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=86400) # Cache por 24 horas
def get_ipi_metalmecanico_historico_ciiu(source_csv_path="1. Indice Nacional.csv", processed_csv_path="ipi_metalmecanico_historico_ciiu.csv"):
    """
    Obtiene los datos históricos del IPI-M para el sector metalmecánico (CIIU).
    Si el archivo CSV procesado existe, lo carga. De lo contrario, lo genera
    a partir del archivo fuente.

    Args:
        source_csv_path (str): Ruta al archivo CSV fuente ('1. Indice Nacional.csv').
        processed_csv_path (str): Ruta al archivo CSV procesado.

    Returns:
        pd.DataFrame: DataFrame con los datos del IPI-M del sector metalmecánico.
    """
    try:
        if os.path.exists(processed_csv_path):
            df = pd.read_csv(processed_csv_path)
            df['fecha'] = pd.to_datetime(df['fecha'])
            return df
        else:
            # Si el archivo procesado no existe, lo generamos
            st.info(f"Generando datos del IPI-M metalmecánico desde '{source_csv_path}'...")
            return process_ipi_data(file_path=source_csv_path, save_to_csv=True)
    except Exception as e:
        st.error(f"Error al obtener los datos históricos del IPI-M metalmecánico: {e}")
        return pd.DataFrame()


def process_aeade_sales_data(file_path="Boletin-de-Prensa-Diciembre-2025_20260128_102856_38314145_extracted.csv", save_to_csv=True):
    """
    Procesa el archivo CSV de ventas de vehículos de AEADE.

    Args:
        file_path (str): Ruta al archivo CSV extraído del boletín de AEADE.
        save_to_csv (bool): Si es True, guarda el DataFrame procesado en un CSV.

    Returns:
        dict: Un diccionario con DataFrames procesados para "ventas_por_marca",
              "ventas_por_combustible" y "ventas_motos".
              Retorna un diccionario con DataFrames vacíos si ocurre un error.
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
        idx_total_combustible = df.loc[idx_gasolina:].reset_index(drop=True)[df.loc[idx_gasolina:]['Marca'].astype(str).str.contains('Total', case=False, na=False)].first_valid_index()
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
        idx_end_motos = df.loc[idx_motos:].reset_index(drop=True)[df.loc[idx_motos:]['Marca'].astype(str).str.contains('Total', case=False, na=False)].first_valid_index()
        
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
                    st.success(f"Datos de {key} guardados en '{output_file}'")
        
        return processed_data

    except Exception as e:
        print(f"Ocurrió un error al procesar el archivo CSV de AEADE: {e}")
        return {"ventas_por_marca": pd.DataFrame(), "ventas_por_combustible": pd.DataFrame(), "ventas_motos": pd.DataFrame()}


@st.cache_data(ttl=86400) # Cache por 24 horas
def get_aeade_ventas_por_marca(source_csv_path="Boletin-de-Prensa-Diciembre-2025_20260128_102856_38314145_extracted.csv", processed_csv_path="aeade_ventas_por_marca_diciembre_2025.csv"):
    """
    Obtiene los datos de ventas de vehículos por marca de AEADE.
    Si el archivo CSV procesado existe, lo carga. De lo contrario, lo genera
    a partir del archivo fuente.
    """
    try:
        if os.path.exists(processed_csv_path):
            df = pd.read_csv(processed_csv_path)
            return df
        else:
            st.info(f"Generando datos de ventas por marca de AEADE desde '{source_csv_path}'...")
            processed_data = process_aeade_sales_data(file_path=source_csv_path, save_to_csv=True)
            return processed_data.get("ventas_por_marca", pd.DataFrame())
    except Exception as e:
        st.error(f"Error al obtener los datos de ventas por marca de AEADE: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=86400) # Cache por 24 horas
def get_aeade_ventas_por_combustible(source_csv_path="Boletin-de-Prensa-Diciembre-2025_20260128_102856_38314145_extracted.csv", processed_csv_path="aeade_ventas_por_combustible_diciembre_2025.csv"):
    """
    Obtiene los datos de ventas de vehículos por tipo de combustible de AEADE.
    Si el archivo CSV procesado existe, lo carga. De lo contrario, lo genera
    a partir del archivo fuente.
    """
    try:
        if os.path.exists(processed_csv_path):
            df = pd.read_csv(processed_csv_path)
            return df
        else:
            st.info(f"Generando datos de ventas por combustible de AEADE desde '{source_csv_path}'...")
            processed_data = process_aeade_sales_data(file_path=source_csv_path, save_to_csv=True)
            return processed_data.get("ventas_por_combustible", pd.DataFrame())
    except Exception as e:
        st.error(f"Error al obtener los datos de ventas por combustible de AEADE: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=86400) # Cache por 24 horas
def get_aeade_ventas_motos(source_csv_path="Boletin-de-Prensa-Diciembre-2025_20260128_102856_38314145_extracted.csv", processed_csv_path="aeade_ventas_motos_diciembre_2025.csv"):
    """
    Obtiene los datos de ventas de motos de AEADE.
    Si el archivo CSV procesado existe, lo carga. De lo contrario, lo genera
    a partir del archivo fuente.
    """
    try:
        if os.path.exists(processed_csv_path):
            df = pd.read_csv(processed_csv_path)
            return df
        else:
            st.info(f"Generando datos de ventas de motos de AEADE desde '{source_csv_path}'...")
            processed_data = process_aeade_sales_data(file_path=source_csv_path, save_to_csv=True)
            return processed_data.get("ventas_motos", pd.DataFrame())
    except Exception as e:
        st.error(f"Error al obtener los datos de ventas de motos de AEADE: {e}")
        return pd.DataFrame()


# --- Bloque de prueba ---
if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.title("Prueba del Módulo `apis_ecuador.py`")
    
    st.header("1. Inflación Anual (Banco Mundial)")
    st.write("Probando la función `obtener_inflacion_anual_banco_mundial()`...")

    inflacion_data = obtener_inflacion_anual_banco_mundial()

    if not inflacion_data.empty:
        st.success("¡Datos de inflación anual del Banco Mundial obtenidos correctamente!")
        st.dataframe(inflacion_data.tail())
        import plotly.express as px
        fig1 = px.bar(inflacion_data, x='año', y='inflacion_pct', title='Inflación Anual en Ecuador (Fuente: Banco Mundial)')
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.error("No se pudieron obtener los datos de inflación.")

    st.write("---")

    st.header("2. IPCO Histórico (Local)")
    st.write("Probando la función `obtener_ipco_historico_local()`...")

    ipco_data = obtener_ipco_historico_local()

    if not ipco_data.empty:
        st.success("¡Datos del IPCO obtenidos y procesados correctamente desde el archivo local!")
        st.dataframe(ipco_data.tail())
        import plotly.express as px
        fig2 = px.line(ipco_data, x='fecha', y='ipco_general', title='Índice de Precios de la Construcción (General)')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.error("No se pudieron obtener los datos del IPCO. Asegúrate de que el archivo '...indice_general...' esté en la carpeta 'data_ipco'.")
    
    st.write("---")

    st.header("3. IPI-M Metalmecánico Histórico (INEC)")
    st.write("Probando la función `get_ipi_metalmecanico_historico_ciiu()`...")

    ipi_metalmecanico_data = get_ipi_metalmecanico_historico_ciiu()

    if not ipi_metalmecanico_data.empty:
        st.success("¡Datos del IPI-M metalmecánico obtenidos y procesados correctamente!")
        st.dataframe(ipi_metalmecanico_data.tail())
    else:
        st.error("No se pudieron obtener los datos del IPI-M metalmecánico. Asegúrate de que '1. Indice Nacional.csv' esté en la carpeta principal.")
    
    st.write("---")

    st.header("4. Ventas de Vehículos AEADE")
    st.write("Probando las funciones `get_aeade_ventas_por_marca()`, `get_aeade_ventas_por_combustible()`, `get_aeade_ventas_motos()`...")

    ventas_marca = get_aeade_ventas_por_marca()
    if not ventas_marca.empty:
        st.success("¡Datos de ventas por marca de AEADE obtenidos correctamente!")
        st.dataframe(ventas_marca.head())
    else:
        st.error("No se pudieron obtener los datos de ventas por marca de AEADE.")

    ventas_combustible = get_aeade_ventas_por_combustible()
    if not ventas_combustible.empty:
        st.success("¡Datos de ventas por combustible de AEADE obtenidos correctamente!")
        st.dataframe(ventas_combustible.head())
    else:
        st.error("No se pudieron obtener los datos de ventas por combustible de AEADE.")
    
    ventas_motos = get_aeade_ventas_motos()
    if not ventas_motos.empty:
        st.success("¡Datos de ventas de motos de AEADE obtenidos correctamente!")
        st.dataframe(ventas_motos.head())
    else:
        st.error("No se pudieron obtener los datos de ventas de motos de AEADE.")



