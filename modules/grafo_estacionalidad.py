import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import Counter
import numpy as np
from matplotlib import font_manager
from wrangling import wrangling


#cargo df que fue exportado como json
df_estacional = wrangling()

#desde y hasta
desde = df_estacional.Año[0]
hasta = df_estacional.Año[len(df_estacional.Año)-1]


##Averiguamos cuantas muestras hoy por mes
muestras_x_mes = Counter(df_estacional.Mes)

#sacamos una lista con la cantidad acumulada de muestras por mes, mas adelante eso va a ser la posicion de los xticks
def acumula_muestras (distancias):
    distancias_acum = [0]
    for distancia in list(distancias.keys()):
        distancias_acum.append(distancias[distancia])
    distancias_acum = np.add.accumulate(distancias_acum).tolist()
    return distancias_acum

muestrasxMes_acum = acumula_muestras(muestras_x_mes)

def segmenta(lista):
  #Separa las listas en una lista que contiene nuevas listas por mes
  listaMeses=[]
  for i in range(12):
    listaMeses.append(lista[muestrasxMes_acum[i]:muestrasxMes_acum[i+1]])
  
  return listaMeses

  
#Funcion que agrega NaN para correr las muestras horizontalmente
def corrimientoMuestras(datos, promedio):
  datos_corridos = segmenta(datos)
  meida_corrida = segmenta(promedio)
  for i in range(12):
    for x in range(muestrasxMes_acum[i]):
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

col_width = col_width_size(muestras_x_mes)

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
    anios = list(Counter(df_estacional.Año.to_list()).keys())
    tabla = maxMinLista(datos)
    
    #Para el ICA: 1° 2021 / 2° Promedio / 3° Desvio / 4° Max /  5° Minimo / 6 variacion
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
            out.append(agrega_variacion(muestras_x_mes, vari))
    return out

def hace_tabla (ax, datos, vari, col_width, items, redondeo):
        

        lista_meses = list(muestras_x_mes.keys())

        tabla = ax.table(
                datosTabla(datos, vari, ultimoanio(datos), items, redondeo),
                colLabels=lista_meses,
                #rowLabels=['Máx','Min','Prom','2021', 'Q1', 'Q2', 'Q3','Std'],
                rowLabels= items,
                colWidths=col_width,
                loc='bottom',
                bbox=[0, 0.2, 1, 0.8],
                )

        tabla.auto_set_font_size(False)
        tabla.set_fontsize(12)

        return tabla

class Grafo_Estacionalidad:
    def __init__(self, df, *nom_columnas_dato, tituloax1: str = None, tituloax2: str= None, items_tabla = ('ultiAnio', 'med','desvio','max','min','varInter')):
        self.df = df
        self.nom_columnas_dato =nom_columnas_dato
        self.tituloax1 = tituloax1
        self.tituloax2 = tituloax2
        self.width = 20
        self.length = 20
        self.axes_ratio = (15,8)
        self.fig = None
        self.ejes = None
        self.colors = ['gold','blueviolet', 'blueviolet', 'gold']
        self.items_tabla= items_tabla
        self.redondeo = 1
        self.table_titles = [None]*2

    def set_table_items(self, items: list):
        self.items_tabla = items

    def get_table_items(self):
        return self.items_tabla
    def set_size(self,w,l):
        self.width = w
        self.length = l

    def set_colors(self, colors):
        self.colors = colors

    def hacer_grafo(self):
        # specify the custom font to use
        font_dirs = ['./fonts/HelveticaNeueLTStd-Cn.otf']
        font_files = font_manager.findSystemFonts(fontpaths=font_dirs)

        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)

        # set font
        plt.rcParams['font.family'] = 'Helvetica'


        axes_ratio = [self.axes_ratio[1] for _ in self.nom_columnas_dato]
        axes_ratio.insert(0,self.axes_ratio[0])

        self.fig, ejes = plt.subplots(3,1, gridspec_kw={'height_ratios': axes_ratio})
        
        self.fig.set_size_inches(self.width,self.length)

        self.ejes = ejes

        ax1 = ejes[0]
        ax2 = ejes[0]
        ax_tabla1 = ejes[1]
        ax_tabla2 = ejes[2]
        
        columna1 = self.nom_columnas_dato[0]
        columna2 = self.nom_columnas_dato[1]
        
        dat1= self.df[columna1].to_list()
        dat2= self.df[columna2].to_list()

        media_columna1 = f'{columna1}_media'
        media_columna2 = f'{columna2}_media'

        med1= self.df[media_columna1].to_list()
        med2= self.df[media_columna2].to_list()

        vari_columna1 = f'{columna1}_var'
        vari_columna2 = f'{columna2}_var'

        vari1 = self.df[vari_columna1].to_list()
        vari2 = self.df[vari_columna2].to_list()

        datos_corridos1, media_corrida1 = corrimientoMuestras(dat1, med1)
        datos_corridos2, media_corrida2 = corrimientoMuestras(dat2, med2)


        for i in range(12):
            ax1.plot(datos_corridos1[i], color = "gold", linewidth=2)
            ax1.plot(media_corrida1[i], color = "darkblue", linewidth=2)
        
        for i in range(12):
            ax2.plot(datos_corridos2[i], color = "blueviolet")
            ax2.plot(media_corrida2[i], color = "orange")
        #dibujo lineas verticales por mes
        for muestras in muestrasxMes_acum:
            ax1.axvline(muestras, color='grey', linestyle='--' )
            ax2.axvline(muestras, color='grey', linestyle='--' )
            
        ax1.set_xmargin(0)
        ax2.set_xmargin(0)
        ax1.set_xticks([])
        ax2.set_xticks([])

        

        
        #agrega las tablas
        hace_tabla(ax_tabla1, dat1, vari1, col_width, self.items_tabla, self.redondeo)
        hace_tabla(ax_tabla2, dat2, vari2, col_width, self.items_tabla, self.redondeo)
        ax_tabla1.axis("off")
        ax_tabla2.axis("off")
        #ax_tabla1.axis('tight')
        #ax_tabla2.axis('tight')

        ax1.set_title(self.tituloax1, fontsize = 20)

        ax_tabla1.set_title(self.table_titles[0], fontsize = 20)
        ax_tabla2.set_title(self.table_titles[1], fontsize = 20)

        plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.2, 
                    wspace=0.4, 
                    hspace=0.2)

        self.fig.tight_layout()


        return self.fig, self.ejes

    def set_redondeo(self, redondeo):
        self.redondeo=redondeo

    def set_legends(self, *nombres):
        custom_lines = [Line2D([0], [0], color='gold', lw=4),
                Line2D([0], [0], color='blueviolet', lw=4)]

        self.ejes[0].legend(custom_lines, list(nombres), loc=8, fontsize=12)
        #for ax in self.ejes:
        #    ax.legend(custom_lines, list(nombres), loc=8, fontsize=12)


    def get_fig(self):
        return self.fig
    
    def debug(self):
        return self.df['v_expo_media']

    def show(self):
        plt.show()
    
    def set_title(self,title: str):
        self.tituloax1 = title
        
    def set_table_title(self, table_title: list[str]):
        self.table_titles = table_title
        
    def print(self, directorio):
        self.fig.savefig(directorio, transparent=False, dpi=300, bbox_inches = "tight")

        