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

