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

def wrangling_valores(serie_precios = '../data/datos para grafico de subseries.xlsx'):
    #### Importamos el excel como dataFrame ####
    
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

def wrangling_indices(desde=2011, hasta=2022, path='../data/indice-precios-cantidades-valores-expo.xls'):
    INDICES_PATH = path
    df_indices = pd.read_excel(INDICES_PATH, header=None, skiprows = 5, index_col=None)
    df_indices= df_indices.rename(columns = {0:'Año', 1: 'Mes', 2:'iv_x', 3:'ip_x', 4:'iq_x', 5:'del',6:'iv_m',7:'ip_m',8:'iq_m'})
    df_indices.drop(columns="del", inplace= True)
    df_indices = df_indices[df_indices['Mes'].notna()]
    
        # paso Mes a las primeras tres letras y en lowercase
    df_indices['Mes'] = list(map(lambda m: m[:3].lower(), df_indices.Mes))
    # hacemos que cada fila diga su año, no solo los eneros
    def completa_con_anios(df_anios):
        anios = []
        arranque = int(df_anios[0])
        for i in range(len(df_anios)):
            if ((i % 12 == 0) and (i != 0)):       
                arranque+=1
                anios.append(arranque)
            else:
                anios.append(arranque)
        return anios

    df_indices['Año'] = completa_con_anios(df_indices.Año)

    # Agregamos ITI
    df_indices['ITI'] = (df_indices.ip_x / df_indices.ip_m) *100
    
    #Enumeramos los meses y los agregamos como columna al df
    def enumera_meses(df_mes):
        nombre_meses = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
        return [nombre_meses.index(i)+1 for i in df_mes]

    df_indices['Mes_num'] = enumera_meses(df_indices.Mes)


    #Agregamos columnas con la variacion interanual

    def var_inter(df, col_name: str):
        return df[col_name].pct_change(periods=12, fill_method='bfill')

    df_indices['iv_x_var']= var_inter(df_indices, 'iv_x')
    df_indices['ip_x_var']= var_inter(df_indices, 'ip_x')
    df_indices['iq_x_var']= var_inter(df_indices, 'iq_x')
    df_indices['iv_m_var']= var_inter(df_indices, 'iv_m')
    df_indices['ip_m_var']= var_inter(df_indices, 'ip_m')
    df_indices['iq_m_var']= var_inter(df_indices, 'iq_m')
    df_indices['ITI_var'] = var_inter(df_indices, 'ITI')

    #Ordenamos el df con estacionalidad
    df_indices = df_indices.sort_values(['Mes_num', 'Año'])

    #seleccionamos el dominio de la serie del df
    df_indices = df_indices.loc[(df_indices['Año'] >= desde) & (df_indices['Año'] <= hasta)]
    df_indices.reset_index(drop=True, inplace=True)

    # Hacemos un df provisorio con las medias
    medias = df_indices.groupby(['Mes_num']).mean()

    def repite_medias(df_target, media_col):
        media = []
        muestras_x_mes = Counter(df_target.Mes)
        for i, valor in enumerate(media_col):
            for _ in range(list(muestras_x_mes.values())[i]):
                media.append(valor)
        return media


    df_indices['iv_x_media'] = repite_medias(df_indices, medias.iv_x)
    df_indices['iv_m_media'] = repite_medias(df_indices, medias.iv_m)
    df_indices['ip_x_media'] = repite_medias(df_indices, medias.ip_x)
    df_indices['ip_m_media'] = repite_medias(df_indices, medias.ip_m)
    df_indices['iq_x_media'] = repite_medias(df_indices, medias.iq_x)
    df_indices['iq_m_media'] = repite_medias(df_indices, medias.iq_m)
    df_indices['ITI_media'] =  repite_medias(df_indices, medias.ITI)


    del medias
    
    
    
    
    return df_indices

def wrangling_serie_sistema(serie_precios = '../data/marzo2022/Serie original.csv', desde = 2011, hasta= 2022):
    #### Importamos el excel como dataFrame ####
    
    df_valores = pd.read_csv(serie_precios,  delimiter=";", index_col= False)

    ### La columna mes en realidad tiene solo el numero ###
    df_valores.rename(columns= {'Mes': 'Mes_num', 'Exportaciones': 'Expo', 'Importaciones': 'Impo'}, inplace= True)
    df_valores.Mes_num.apply(lambda x: int(x))
    
    #Armo la lista con los nombres de cada mes
    lista_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    df_valores['Mes'] = [lista_meses[mes_num-1] for mes_num in df_valores.Mes_num]

    #### Casteo los valores a float ####
    df_valores.Expo = df_valores.Expo.apply(lambda x: float(x.replace(',','.')))
    df_valores.Impo = df_valores.Impo.apply(lambda x: float(x.replace(',','.')))

    #ITI
    df_valores['ITI'] = (df_valores.Expo / df_valores.Impo)*100

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
                            'v_m_media'
    ]]
    df_valores.reset_index(inplace = True, drop = True)
    df_valores = df_valores.rename(columns={"Expo": "v_x", "Impo": "v_m"})
    
    df_valores = df_valores.loc[(df_valores['Año'] >= desde) & (df_valores['Año'] <= hasta)]
    df_valores.reset_index(drop=True, inplace=True)
    
    return df_valores