import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import datetime 

def trends(ticker, start='2000-01-01', end=None, sensibilidad=None, escala='linear'):
    '''
    Encuentra maximos y mínimos locales dada una sensibilidad (cantidad de velas de la ventana local)
    Gráfico 1: Precios de cierre con mínimos y máximos encontrados
    Grafico 2: Precios de cierre con lineas de soportes y resistencias desde cada máximo y mínimo encontrado
    Gráfico 3: Precios de cierre con zona alcista, bajista o lateral en función de las pendientes de los últimos pares de mínimos y máximos encontrados 
    '''

    if not end:
        end = datetime.datetime.now().strftime('%Y-%m-%d')
        
    data = yf.download(ticker, auto_adjust=True, start=start, end=end)
    k = sensibilidad if sensibilidad else len(data)//40
    
    r_max = data.Close.rolling(k).max()
    max_back = (data.Close == r_max)
    max_fw = max_back.shift(-k).rolling(k).sum() == 0
    data['loc_max'] = max_back & max_fw

    r_min = data.Close.rolling(k).min()
    min_back = (data.Close == r_min)
    min_fw = min_back.shift(-k).rolling(k).sum() == 0
    data['loc_min'] = min_back & min_fw

    pmin = data.loc[data['loc_min']==True].Close.pct_change()
    pmax = data.loc[data['loc_max']==True].Close.pct_change()
    vmin = r_min.loc[data['loc_min']==True]
    vmax = r_max.loc[data['loc_max']==True]

    r = pd.concat([pmin,pmax,vmin,vmax], axis=1, keys=['pMin','pMax','vMin','vMax'])
    ultima_pmax = r.pMax.fillna(method='ffill')
    ultima_pmin = r.pMin.fillna(method='ffill')

    r['tipo'] = 0
    r.loc[(ultima_pmax > 0) & (ultima_pmin > 0),'tipo'] = 1
    r.loc[(ultima_pmax < 0) & (ultima_pmin < 0),'tipo'] = -1

    data = pd.concat([data,r], axis=1).fillna(method='ffill')
    fig, ax = plt.subplots(figsize=(15,12), nrows=3)
    
    ax[0].plot(data.Close, 'k', lw=0.5)
    ax[0].plot(data.Close.loc[data.loc_max==True], lw=0, marker='o', markersize=15, alpha=0.5, color='green')
    ax[0].plot(data.Close.loc[data.loc_min==True], lw=0, marker='o', markersize=15, alpha=0.5, color='red')

    ax[1].plot(data.Close, 'k', lw=0.5)
    ax[1].plot(data.vMin, 'r--', lw=1.5, alpha=1)
    ax[1].plot(data.vMax, 'g--', lw=1.5, alpha=1)
    
    ax[2].fill_between(data.index,data.Close, where=data.tipo==1, color='tab:green', alpha=0.7)
    ax[2].fill_between(data.index,data.Close, where=data.tipo==-1, color='tab:red', alpha=0.7)
    ax[2].fill_between(data.index,data.Close, where=data.tipo==0, color='gray', alpha=0.2)
    ax[2].plot(data.Close, 'k', lw=0.5, alpha=1)

    titulos = [f'Máximos y mínimos locales (ventana {k} velas)','Soportes y Resistencias','Zonas por Tendencia Post-Observación pares de Min y Max']
    for i in range(3):
        ax[i].set_yscale(escala)
        ax[i].set_title(titulos[i], y=0.88, fontsize=16, color='gray')

    plt.subplots_adjust(hspace=0)
    return data.dropna()



def waves(ticker, start='2000-01-01', end=None, sensibilidad=None, escala='linear'):
    
    if not end:
        end = datetime.datetime.now().strftime('%Y-%m-%d')
        
    data = yf.download(ticker, auto_adjust=True, start=start, end=end)
    k = sensibilidad if sensibilidad else len(data)//40

    r_max = data.Close.rolling(k).max()
    max_back = (data.Close == r_max)
    max_fw = max_back.shift(-k).rolling(k).sum() == 0
    data['loc_max'] = max_back & max_fw

    r_min = data.Close.rolling(k).min()
    min_back = (data.Close == r_min)
    min_fw = min_back.shift(-k).rolling(k).sum() == 0
    data['loc_min'] = min_back & min_fw

    vmin = r_min.loc[data['loc_min']==True]
    vmax = r_max.loc[data['loc_max']==True]

    r = pd.concat([vmin,vmax], axis=1, keys=['vMin','vMax'])
    r['fecha'] = r.index
    for idx, row in r.iterrows():
        if (r.loc[idx].vMin>0) & (r.shift().loc[idx].vMin>0):
            fmax = data.loc[(data.index > r.fecha.shift().loc[idx]) & (data.index < row['fecha']) ].Close.idxmax()
            vmax = data.loc[(data.index > r.fecha.shift().loc[idx]) & (data.index < row['fecha']) ].max().Close
            d = pd.DataFrame({'vMax':vmax, 'fecha':fmax}, index=[fmax])
            r = pd.concat([r,d],sort=False)
        if (r.loc[idx].vMax>0) & (r.shift().loc[idx].vMax>0):
            fmin = data.loc[(data.index > r.fecha.shift().loc[idx]) & (data.index < row['fecha']) ].Close.idxmin()
            vmin = data.loc[(data.index > r.fecha.shift().loc[idx]) & (data.index < row['fecha']) ].min().Close
            d = pd.DataFrame({'vMin':vmin, 'fecha':fmin}, index=[fmin])
            r = pd.concat([r,d],sort=False)   
    r.sort_index(inplace=True)
    r['valor'] = r[['vMin','vMax']].max(axis=1)

    data = pd.concat([data,r], axis=1).fillna(method='ffill')
    fig, ax = plt.subplots(figsize=(15,6), nrows=1)
    
    ax.plot(data.Close, 'k', lw=0.5, alpha=0.2)
    ax.plot(r.vMax,  marker='o', markersize=10, alpha=0.5, color='k')
    ax.plot(r.vMin, marker='o', markersize=10, alpha=0.5, color='k')
    ax.plot(r.valor, '--k', lw=1)

    ax.set_yscale(escala)
    ax.set_title('Ondas', y=0.88, fontsize=16, color='gray')

    plt.subplots_adjust(hspace=0)
    return r

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()