import pandas as pd
from collections import Counter
from time import strptime

def var_inter(df, col_name: str):
    return df[col_name].pct_change(periods=12, fill_method='bfill')

def repite_medias(df_target, media_col):
    media = []
    muestras_x_mes = Counter(df_target.Mes)
    for i, valor in enumerate(media_col):
        for _ in range(list(muestras_x_mes.values())[i]):
            media.append(valor)
    return media

def wrangling():
    #### Importamos el excel como dataFrame ####
    serie_precios = '../data/datos para grafico de subseries.xlsx'
    df_valores = pd.read_excel(serie_precios)

    #### Elimino primer fila vacia#####
    df_valores.drop(0,inplace=True)

    ##### Armo una columna con el año y otra con el mes ####
    mes_año = list(map(lambda x: x.split('-'),df_valores.Periodo))
    año = [int(f'20{d[1]}') for d in mes_año]
    df_valores['Año'] = año
    df_valores['Mes'] = [d[0] for d in mes_año]
    del df_valores['Periodo']

    ### Creo una columna con el numero de mes
    df_valores['Mes_num'] = df_valores.Mes.apply(lambda m: strptime(m,'%b').tm_mon)

    #### Casteo los valores a float ####
    df_valores.Expo = df_valores.Expo.apply(lambda x: float(x.replace(',', '')))
    df_valores.Impo = df_valores.Impo.apply(lambda x: float(x.replace(',', '')))

    #### Calculo la variación interanual #####
    df_valores['v_x_var'] = var_inter(df_valores, 'Expo')
    df_valores['v_m_var'] = var_inter(df_valores, 'Impo')

    df_valores = df_valores.sort_values(['Mes_num', 'Año'])

    ### Se adjuntan columnas con el promedio anual ###
    medias = df_valores.groupby(['Mes_num']).mean()
    df_valores['v_x_media'] = repite_medias(df_valores, medias.Expo)
    df_valores['v_m_media'] = repite_medias(df_valores, medias.Impo)
    del medias

    #### Filtro solo para enero y febrero. Ordeno las columnas ####
    #df_valores = df_valores[(df_valores.Mes == 'Jan') | (df_valores.Mes == 'Feb') ]
    df_valores = df_valores[['Mes_num',
                            'Año',
                            'Mes',
                            'Expo',
                            'v_x_var',
                            'v_x_media',
                            'Impo',
                            'v_m_var',
                            'v_m_media']]
    df_valores.reset_index(inplace = True, drop = True)
    df_valores = df_valores.rename(columns={"Expo": "v_x", "Impo": "v_m"})
    
    return df_valores
