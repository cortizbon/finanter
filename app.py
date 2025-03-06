import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd
from plotly.subplots import make_subplots
from utils import DEPTOS_SGR, DIC_COLORES, DEPTOS_PRES, DIC_DEPTOS

st.set_page_config(layout='wide')



st.title("Finanzas territoriales")

tab1, tab2, tab3 = st.tabs(['Regalías', 'Presupuesto', 'Sistema General de Participaciones'])

gdf = gpd.read_parquet('./datasets/muns.parquet')
pop = pd.read_csv('./datasets/pop.csv')
pop2 = pd.read_csv('./datasets/pop2.csv')
custom_palette = ["#2F399B", "#dd722a", "#F7B261", "#009999", "#81D3CD", "#CBECEF", "#D9D9ED",
                  "#2F399B", "#dd722a", "#F7B261", "#009999", "#81D3CD", "#CBECEF", "#D9D9ED",
                  "#2F399B", "#dd722a", "#F7B261", "#009999", "#81D3CD", "#CBECEF", "#D9D9ED",
                  "#2F399B", "#dd722a", "#F7B261", "#009999", "#81D3CD", "#CBECEF", "#D9D9ED"]


with tab1:
    col1, col2 = st.columns([3, 2])
    with col1: 

        deptos = DEPTOS_SGR.copy()
        depto = st.selectbox("Seleccione el departamento: ", deptos)
        sgr_g = pd.read_csv(f'./datasets/deptos_sgr/{depto}_sgr.csv')

        periodos = sgr_g['Periodo'].sort_values().unique().tolist()
        per = st.select_slider("Seleccione el periodo: ", periodos)
        sgr_g = sgr_g[(sgr_g['Periodo'] == per)]

        cuentas = sgr_g['C1'].sort_values().unique().tolist()
        cuenta = st.selectbox("Seleccione el departamento: ", cuentas)
        sgr_g = sgr_g[(sgr_g['C1'] == cuenta)]

        sgr_g = sgr_g[['Periodo','mpio_cdpmp', 'Valor_25']]
        pop = pop[pop['NombreDepto'] == depto]
        pop['mpio_cdpmp'] = pop['mpio_cdpmp'].astype('int')
        sgr_g = sgr_g.merge(pop, how='left')

        sgr_g['Valor_25_pop'] = sgr_g['Valor_25'] / sgr_g['Población']

        sgr_g = sgr_g.astype({'mpio_cdpmp':'int'})
        gdf = gdf.astype({'mpio_cdpmp':'int'})


        mapa = gpd.GeoDataFrame(sgr_g.merge(gdf))


    with col2:
        fig, ax = plt.subplots(1, 1, figsize=(5, 3))
        mapa.plot(column='Valor_25_pop', ax=ax, legend=True)
        ax.set_axis_off()


        st.pyplot(fig)

with tab2:
    col1, col2 = st.columns([3, 2])
    with col1: 

        deptos = DEPTOS_PRES.copy()
        depto = st.selectbox("Seleccione el departamento: ", deptos)
        pres = pd.read_csv(f'./datasets/deptos_pres/{depto}_pres.csv')
        pres = pres[pres['Nombre DANE Departamento'] == depto]

        rubros_i = pres['RUBRO'].unique().tolist()
        custom_map_i = dict(zip(rubros_i, custom_palette))

        ents = pres['NOMBRE_ENTIDAD'].sort_values().unique().tolist()
        ent = st.selectbox("Seleccione entidad", ents)

        filtro = pres[pres['NOMBRE_ENTIDAD'] == ent]
        
        tab = filtro.groupby(['Año','RUBRO'])['Presupuesto Definitivo'].sum().reset_index()

        fig1 = px.area(tab, 
               x='Año',
               y='Presupuesto Definitivo',
               color='RUBRO',
              title='Ingresos',
              color_discrete_map=custom_map_i)

        fig = make_subplots(rows=1, cols=1)

        for trace in fig1.data:
            fig.add_trace(trace, row=1, col=1)

                # Update layout (optional: remove legend)
        fig.update_layout(title="Histórico", showlegend=False)


        fig.update_layout(title_text=ent,
                        showlegend=False)

        st.plotly_chart(fig)


        periodos = pres['Año'].sort_values().unique().tolist()

    with col2:
        per = st.select_slider("Seleccione el periodo: ", periodos)
        pres = pres[(pres['Año'] == per)]

        

        cuentas = pres[pres['CODIGO_ENTIDAD'] / 1000 != pres['Cód. DANE Departamento'].astype(float)]['RUBRO'].sort_values().unique().tolist()
        cuenta = st.selectbox("Seleccione el tipo de ingreso: ", cuentas)
        pres = pres[(pres['RUBRO'] == cuenta)]

        pres = pres.rename(columns={'CODIGO_ENTIDAD':'mpio_cdpmp'})
        pres = pres[['Año','mpio_cdpmp', 'Valor_25']]
        pres = pres.astype({'mpio_cdpmp':'int'})
        pop2 = pop2[pop2['NombreDepartamento'] == depto.lower().capitalize()]
        pop2['mpio_cdpmp'] = pop2['mpio_cdpmp'].astype('int')
        pres = pres.merge(pop2, how='right')
 

        pres['Valor_25_pop'] = pres['Valor_25'] / pres['Población']

        pres = pres.astype({'mpio_cdpmp':'int'})
        gdf = gdf.astype({'mpio_cdpmp':'int'})
        gdf['cod_depto'] = gdf['mpio_cdpmp'].astype(str).str[:-3].astype(int)
        gdf['Depto'] = gdf['cod_depto'].map(DIC_DEPTOS)
        gdf = gdf[gdf['Depto'] == depto]

        mapa = gpd.GeoDataFrame(pres.merge(gdf, how='left').dropna(subset='geometry'))
        
        fig, ax = plt.subplots(1, 1, figsize=(5, 3))
        mapa.plot(column='Valor_25_pop', ax=ax, legend=True)
        ax.set_axis_off()


        st.pyplot(fig)
with tab3:
    st.link_button('Link to SGP', 'https://sgp-ofiscal.streamlit.app')