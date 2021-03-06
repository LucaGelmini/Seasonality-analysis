import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib as mpl
from collections import Counter
import numpy as np
from matplotlib import font_manager
from modules.config import path_indices, path_dolares
from modules.wrangling import wrangling_indices, wrangling_dolares


this = sys.modules[__name__]
this.df_estacional = None
this.muestras_x_mes = None
this.muestrasxMes_acum = None
this.col_with = None

#sacamos una lista con la cantidad acumulada de muestras por mes, mas adelante eso va a ser la posicion de los xticks
def acumula_muestras (distancias):
    distancias_acum = [0]
    for distancia in list(distancias.keys()):
        distancias_acum.append(distancias[distancia])
    distancias_acum = np.add.accumulate(distancias_acum).tolist()
    return distancias_acum

def wrangler(name: str = 'indice_VPQ'):
    if name == 'indice_VPQ':
        this.df_estacional = wrangling_indices(path=path_indices)
        setea_constantes()
        return this.df_estacional
    if name == 'dolares':
        this.df_estacional = wrangling_dolares(path=path_dolares)
        setea_constantes()
        return this.df_estacional
    else:
        return 'error'
    

def setea_constantes():
        this.muestras_x_mes = Counter(this.df_estacional.Mes)
        this.muestrasxMes_acum = acumula_muestras(this.muestras_x_mes)
        this.col_width = col_width_size(this.muestras_x_mes)




def segmenta(lista):
  '''Separa las listas en una lista que contiene nuevas listas por mes'''
  listaMeses=[]
  for i in range(12):
    listaMeses.append(lista[this.muestrasxMes_acum[i]:this.muestrasxMes_acum[i+1]])
  
  return listaMeses

  

def corrimientoMuestras(datos, promedio):
    '''Funcion que agrega NaN para correr las muestras horizontalmente'''
    datos_corridos = segmenta(datos)
    meida_corrida = segmenta(promedio)
    for i in range(12):
        for x in range(this.muestrasxMes_acum[i]):
            datos_corridos[i].insert(x, None)
            meida_corrida[i].insert(x, None)
    return datos_corridos, meida_corrida


  #Extraemos solo los valores del 2021
def ultimoanio(datos):
  segmentado = segmenta(datos)
  return [mes[len(mes)-1] for mes in segmentado]



def maxMinLista (val):
  segmentado = segmenta(val)
  extremosEstac = []
  for mes in segmentado:
    max_val = max(mes)
    max_idx = mes.index(max_val)
    min_val = min(mes)
    min_idx = mes.index(min_val)
    maxi = (max_val,max_idx)
    mini = (min_val,min_idx)
    media = sum(mes)/len(mes)

    #Cuartiles
    mes_sin_nan = []
    for v in mes:
      if(not np.isnan(v)):
        mes_sin_nan.append(v)
    qs = list(np.quantile(mes_sin_nan, [0.25, 0.5, 0.75]))
    q1s = qs[0]
    q2s = qs[1]
    q3s = qs[2]

    #Desviacion estandar
    std = np.std(mes_sin_nan)


    extremosEstac.append([maxi,mini,media,q1s,q2s,q3s,std])

  
  #Aca traspongo la matriz para que coincida con el formato de matplotlib
  extremosEstac = list(zip(*extremosEstac[::-1]))
  for i, ex in enumerate(extremosEstac):
    extremosEstac[i] = list(extremosEstac[i])
    extremosEstac[i].reverse()
  return extremosEstac

#determino el ancho de las columnas
def col_width_size(muestras_x_mes):
    col_width = []
    muestrasxMes = list(muestras_x_mes.values())
    for muestra in muestrasxMes:
        col_width.append(muestra/sum(muestrasxMes))
    return  col_width



def puntoyComa(a):
  return '{:,}'.format(a).replace(',','~').replace('.',',').replace('~','.')

#funcion que agrega los cuartiles
def agrega_cuartiles(tabla):
    lista_cuartiles = []
    lista_cuartiles.append([puntoyComa(round(q1)) for q1 in tabla[3]])
    lista_cuartiles.append([puntoyComa(round(q2)) for q2 in tabla[4]])
    lista_cuartiles.append([puntoyComa(round(q3)) for q3 in tabla[5]])

    return lista_cuartiles

def agrega_desv(tabla, redondeo):
    return [puntoyComa(round(sd, redondeo)) for sd in tabla[6]]

def agrega_ulimoAnio(ultiAnio, redondeo):
    ultiAnio_string = []
    for val in ultiAnio:
        if (np.isnan(val)):
            redondo = '--'
        else:
            redondo = puntoyComa(round(val, redondeo))
        ultiAnio_string.append(redondo) #2021 en el 1er lugar
    return ultiAnio_string

def agrega_maximos(tabla, anios, redondeo):
    maximos_string =[]
    for max in tabla[0]:
        numeros = puntoyComa(round(max[0], redondeo))
        maximos_string.append(f'{numeros} ({anios[max[1]]})')
    return maximos_string

def agrega_minimos(tabla,anios, redondeo):
    minimos_string =[]
    
    for min in tabla[1]:
        numeros = puntoyComa(round(min[0], redondeo))
        minimos_string.append(f'{numeros} ({anios[min[1]]})')

    return minimos_string

def agrega_medias(tabla, redondeo):
    medias_string =[]
    for med in tabla[2]:
        numeros = puntoyComa(round(med, redondeo))
        medias_string.append(numeros)
    return medias_string

def agrega_variacion(muestras_x_mes, vari):
    variacion_string = []
    for n in acumula_muestras(muestras_x_mes)[1:]:
      if np.isnan(vari[n-1]):
        variacion_string.append('--')
      else:
        vari_por_cien = vari[n-1]*100
        variacion_string.append(f'{puntoyComa(round(vari_por_cien,1))}%')
    
    return variacion_string


def datosTabla(datos, vari, ultiAnio, items, redondeo = 1):
    anios = list(Counter(this.df_estacional.A??o.to_list()).keys())
    tabla = maxMinLista(datos)
    
    #Para el ICA: 1?? 2021 / 2?? Promedio / 3?? Desvio / 4?? Max /  5?? Minimo / 6 variacion
    out = []
    
    for item in items:
        if item == 'max':
            out.append(agrega_maximos(tabla, anios, redondeo))
        elif item == 'min':
            out.append(agrega_minimos(tabla, anios, redondeo))
        elif item == 'med':
            out.append(agrega_medias(tabla, redondeo))
        elif item == 'cuartiles':
            cuartiles = agrega_cuartiles(tabla) #devuelve tres listas [q1,q2,q3]
            for qx in cuartiles:
                out.append(qx)
        elif item == 'desvio':
            out.append(agrega_desv(tabla, redondeo))
        elif item == 'ultiAnio':
            out.append(agrega_ulimoAnio(ultiAnio, redondeo))
        elif item == 'varInter':
            out.append(agrega_variacion(this.muestras_x_mes, vari))
    return out

def hace_tabla (ax, col_width, items, datos_para_tabla):
        lista_meses = traduce_meses(list(this.muestras_x_mes.keys()))

        tabla = ax.table(
                datos_para_tabla,
                colLabels=lista_meses,
                #rowLabels=['M??x','Min','Prom','2021', 'Q1', 'Q2', 'Q3','Std'],
                rowLabels= items,
                colWidths=col_width,
                loc='bottom',
                bbox=[0, 0.2, 1, 0.8],
                )

        tabla.auto_set_font_size(False)
        tabla.set_fontsize(16)

        return tabla
    

def traduce_meses(mesesIngles: list[str]):
    traductor = {'jan': 'Ene', 'feb': 'Feb', 'mar': 'Mar',
                 'apr': 'Abr', 'may': 'May', 'jun': 'Jun',
                 'jul': 'Jul', 'aug': 'Ago', 'sep': 'Sep',
                 'oct': 'Oct', 'nov': 'Nov', 'dec': 'Dic'
    }
    if mesesIngles[0].lower()=='jan':
        return [traductor[mes.lower()] for mes in mesesIngles]
    else:
        return mesesIngles



class Grafo_Estacionalidad:
    def __init__(self,
                 *nom_columnas_dato,
                 df,
                 tituloax1: str = None,
                 tituloax2: str= None,
                 items_tabla = ('ultiAnio', 'med','desvio','max','min','varInter'),
                 tabla_out = False):
        self.df = df
        self.columnas_dato =nom_columnas_dato
        self.tituloax1 = tituloax1
        self.tituloax2 = tituloax2
        self.width = 20
        self.length = 20
        self.axes_ratio = (15,8)
        self.fig = None
        self.ejes = None
        self.colors = ['#ecb110','blueviolet', 'blueviolet', '#ecb110']
        self.items_tabla = items_tabla
        self.nombre_filas = ('Ultimo A??o', 'Media','Desv??o estandar','M??ximo','M??nimo','Variaci??n interanual')
        self.redondeo = 1
        self.table_titles = [None]*2
        self.tabla_out = tabla_out
        self.datosTabla = list(nom_columnas_dato)
        self.linewidth = 3
        self.ticksize = 20
    ######################################## Funci??n Principal ##############################################
    ########################################                   ##############################################
    def hacer_grafo(self):
        
        font_path = '../modules/fonts/Helvetica-Neue-LT-Std-77-Bold-Condensed_22542.ttf'  # Your font path goes here
        font_manager.fontManager.addfont(font_path)
        prop = font_manager.FontProperties(fname=font_path)

        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = prop.get_name()
        

        
        columnas_dato = self.columnas_dato

        
        if self.tabla_out: # Si imprimimos una tabla tenemos que considerar el lugar que ocupa
            axes_ratio = [self.axes_ratio[1] for _ in columnas_dato]
            axes_ratio.insert(0,self.axes_ratio[0])
            n_ejes = len(columnas_dato)+1
            self.fig, ejes = plt.subplots((n_ejes),1, gridspec_kw={'height_ratios': axes_ratio})
            eje_lineas =ejes[0]
            ejes_tablas = ejes[1:]
        else:
            n_ejes = 1
            axes_ratio = self.axes_ratio
            self.fig, ejes = plt.subplots((n_ejes),1)
            eje_lineas =ejes

        
        self.fig.set_size_inches(self.width,self.length)

        self.ejes = ejes

        for count, columna_dato in enumerate(columnas_dato):
            
            columna_dato_media = f'{columna_dato}_media'
            columna_dato_vari = f'{columna_dato}_var'
            dato= self.df[columna_dato].to_list()
            media= self.df[columna_dato_media].to_list()
            variacion = self.df[columna_dato_vari].to_list()
            
            datos_corridos, media_corrida = corrimientoMuestras(dato, media)

            for i in range(12):
                eje_lineas.plot(datos_corridos[i], color = self.colors[count+(count)*(0<count)], linewidth=self.linewidth)
                eje_lineas.plot(media_corrida[i], color = self.colors[count+1+(count)*(0<count)], linewidth=self.linewidth)
            
            #dibujo lineas verticales por mes
            for muestras in this.muestrasxMes_acum:
                eje_lineas.axvline(muestras, color='grey', linestyle='--' )
                
            eje_lineas.set_xmargin(0)
            eje_lineas.set_xticks([])
            

        
            #agrega las tablas
            self.datosTabla[count] = datosTabla(dato, variacion, ultimoanio(dato), self.items_tabla, self.redondeo)
            if self.tabla_out:
                hace_tabla( ejes_tablas[count],
                            this.col_width,
                            self.nombre_filas,
                            self.datosTabla[count]
                            )
                ejes_tablas[count].axis("off")
                #ejes_tablas[count].axis('tight')

                ejes_tablas[count].set_title(self.table_titles[count], fontsize = 20)
                
                 
        
        eje_lineas.set_title(self.tituloax1, fontsize = 25)
        eje_lineas.tick_params(axis='y', which='major', labelsize=self.ticksize)
        


        plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.2, 
                    wspace=0.4, 
                    hspace=0.2)

        self.fig.tight_layout()


        return self.fig, self.ejes
    

    
    ####################################### Seters and Geters ############################################

    def set_table_items(self, items: list):
        self.items_tabla = items

    def get_table_items(self):
        return self.items_tabla
    def set_size(self,w,l):
        self.width = w
        self.length = l

    def set_colors(self, *colors: str):
        self.colors = colors
        
    def set_redondeo(self, redondeo: int):
        self.redondeo=redondeo

    def set_legends(self, *nombres: str, size = 16, location = 8):
        custom_lines = [Line2D([0], [0], color= self.colors[0], lw=4),
                Line2D([0], [0], color=self.colors[2], lw=4)]
        if self.tabla_out:
            self.ejes[0].legend(custom_lines, list(nombres), loc=location, fontsize=12, prop = {'size': size})
        else:
            self.ejes.legend(custom_lines, list(nombres), loc=location, fontsize=12, prop = {'size': size})



    def get_fig(self):
        return self.fig
    

    def show(self):
        plt.show()
    
    def set_title(self,title: str):
        self.tituloax1 = title
        
    def set_table(self, mostrar: bool):
        self.tabla_out = mostrar
        
    def set_table_title(self, table_title: list[str]):
        self.table_titles = table_title
        
    def print(self, directorio):
        self.fig.savefig(directorio, transparent=False, dpi=300, bbox_inches = "tight")
        
    def set_row_names(self, *row_names):
        self.nombre_filas = tuple(row_names)
        
    def set_ylabel (self, label: str, fontsize:int = 25):
        if self.tabla_out:
            self.ejes[0].set_ylabel(label, fontsize = fontsize)
        else:
            self.ejes.set_ylabel(label, fontsize = fontsize)
            
    def get_df(self):
        return self.df
    
    def get_columns_data(self):
        lista_de_df = []
        for columna in self.columnas_dato:
            lista_de_df.append(pd.DataFrame(segmenta(self.df[columna].to_list())))
        return lista_de_df

    def get_dfs_tablas(self):
        lista_de_tablas = []
        for tabla in self.datosTabla:
            dic_tabla = {}
            for i, col in enumerate(tabla):
                dic_tabla['mes'] = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
                dic_tabla[self.nombre_filas[i]] = col
            lista_de_tablas.append(pd.DataFrame(dic_tabla))
        return lista_de_tablas
        
    def set_lineWidth(self, w:int):
        self.linewidth = w

    def set_ticksize(self, s):
        self.ticksize = s
        
        