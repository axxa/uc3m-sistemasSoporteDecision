import pandas as pd
import numpy as np
import os.path

import constants as c


def merge_dfs(left_df, right_df, column_name):
    return pd.merge(left_df, right_df, on=column_name, how='left').fillna(0)


def podarDataInicial(clientes_x_bizum_pd, transacciones_pd):
    # poda_con_bizum = clientes_x_bizum_pd['instalado'] == 0
    clientes_x_bizum_pd = clientes_x_bizum_pd[clientes_x_bizum_pd['instalado'] == 0]
    # poda_desempleados = clientes_x_bizum_pd['tipo_empleo'] != 'parado'
    clientes_x_bizum_pd = clientes_x_bizum_pd[clientes_x_bizum_pd['tipo_empleo'] != 'parado']
    transacciones_pd = transacciones_pd[transacciones_pd['tipo'] != 'Ingreso']
    return clientes_x_bizum_pd, transacciones_pd


def prepararFull(file_name):
    clientes_pd = pd.read_csv('clientes.txt', sep=",")
    bizum_pd = pd.read_csv('bizum.txt', sep=",")
    bizum_pd = bizum_pd.rename(columns={'id': 'idClientes'})
    transacciones_pd = pd.read_csv('transacciones.txt', sep=",")
    clientes_x_bizum_pd = merge_dfs(clientes_pd, bizum_pd, 'idClientes')
    clientes_x_bizum_pd, transacciones_pd = podarDataInicial(clientes_x_bizum_pd, transacciones_pd)

    dict = {}
    for index, row in transacciones_pd.iterrows():
        if dict.get(row['idCliente']) is None:
            array = np.zeros(5)
        else:
            array = dict.get(row['idCliente'])
        idx_arr = c.tipo_trx.get(row['tipo'])
        array[idx_arr] = array[idx_arr] + row['importe']
        dict.update({row['idCliente']: array})

    for index, row in clientes_x_bizum_pd.iterrows():
        array = dict.get(row['idClientes'])
        if array is not None:
            clientes_x_bizum_pd.loc[index, "Comercio alimentación"] = array[0]
            clientes_x_bizum_pd.loc[index, "Restaurante"] = array[1]
            clientes_x_bizum_pd.loc[index, "Seguros"] = array[2]
            clientes_x_bizum_pd.loc[index, "Centro deportivo"] = array[3]
            clientes_x_bizum_pd.loc[index, "Centro escolar"] = array[4]
            clientes_x_bizum_pd.loc[index, "supera_4_eur"] = ((array[0] + array[1] + array[2] +
                                                              array[3] + array[4]) * 0.02) > 4

    writer = pd.ExcelWriter(file_name, engine='openpyxl')
    clientes_x_bizum_pd.to_excel(writer, 'data', index=False)

    writer.save()
    writer.close()


def scorize(full_pd, file_name):
    full_pd['score'] = 0
    for index, row in full_pd.iterrows():
        # sexo
        sexo = c.scores.get(row['sexo'])
        full_pd.loc[index, "score"] += c.scores.get(row['sexo'])
        # edad
        edad = row['edad']
        if 20 <= row['edad'] < 25: grupo_edad = 0
        elif 25 <= row['edad'] < 35: grupo_edad = 1
        elif 35 <= row['edad'] < 45: grupo_edad = 2
        elif 45 <= row['edad']: grupo_edad = 3
        else: grupo_edad = 4
        full_pd.loc[index, "score"] += c.scores.get('edad')[grupo_edad]
        # Trx
        full_pd.loc[index, "score"] += c.scores.get('Comercio alimentación')[grupo_edad] * row['Comercio alimentación']
        full_pd.loc[index, "score"] += c.scores.get('Restaurante')[grupo_edad] * row['Restaurante']
        full_pd.loc[index, "score"] += c.scores.get('Seguros')[grupo_edad] * row['Seguros']
        full_pd.loc[index, "score"] += c.scores.get('Centro deportivo')[grupo_edad] * row['Centro deportivo']
        full_pd.loc[index, "score"] += c.scores.get('Centro escolar')[grupo_edad] * row['Centro escolar']
        # tipo_empleo
        full_pd.loc[index, "score"] += c.scores.get(row['tipo_empleo'])
        # hijos
        if row['numero_hijos'] is None or row['numero_hijos'] > 0:
            score_hijos = c.scores.get('hijos')
        else:
            score_hijos = c.scores.get('no_hijos')
        full_pd.loc[index, "score"] += score_hijos[0] * row['Comercio alimentación']
        full_pd.loc[index, "score"] += score_hijos[1] * row['Restaurante']
        full_pd.loc[index, "score"] += score_hijos[2] * row['Seguros']
        full_pd.loc[index, "score"] += score_hijos[3] * row['Centro deportivo']
        full_pd.loc[index, "score"] += score_hijos[4] * row['Centro escolar']

        score_cp = c.scores.get(str(row['cp'])[:2])
        if score_cp is None:
            score_cp = 0.001
        full_pd.loc[index, "score"] += score_cp

    writer = pd.ExcelWriter(file_name, engine='openpyxl')
    full_pd.to_excel(writer, 'data', index=False)

    writer.save()
    writer.close()


def generate_statistic_data(data_array: np.array):
    std = np.std(data_array)
    mean = np.mean(data_array)
    mean_plus_std = mean + std
    mean_minus_std = mean - std
    return std, mean, mean_plus_std, mean_minus_std


# Estrategias de seleccion:
# 1. Inicialmente se deben elegir 3000 clientes a los cuales repartir los bonos-> el 1% de las
#    transacciones de estos clientes seran nuestra ganancia
# 2. Se tiene la opcion de comprar mas codigos promocionales a 4$ cada uno-> 2% sobre transacciones
# Insight: se pueden tomar dos caminos:
# ** Elegir los 3000 clientes mas gruesos para repartir los codigos promocinales y no comprar mas codigos
# ** Segmentar dos grupos de clientes, primer grupo de 3000 en el cual se eligen los clientes constantes
#    con transacciones entre n> sumatorio tx cliente > 0.
#    Segundo grupo con clientes gruesos entre sumatorio tx cliente > n
if __name__ == '__main__':
    file_name = 'full.xlsx'
    if not os.path.isfile(file_name):
        prepararFull(file_name)

    df = pd.read_excel(file_name)
    if "score" not in df:
        scorize(df, file_name)

    df = df.dropna()
    stat_arr = np.array(df['score'])
    std, mean, mean_plus_std, mean_minus_std = generate_statistic_data(stat_arr)

    escogidos = df[df['score'] >= mean_plus_std]
    # escogidos_top = escogidos[escogidos['supera_4_eur']==True]
    # provisionales = df[df['score'] >= mean]

    escogidos = escogidos.sort_values(by='score', ascending=False)

    escogidos = escogidos.reset_index(drop=True)
    # escogidos_top = escogidos_top.reset_index(drop=True)

    writer = pd.ExcelWriter('resultados.xlsx', engine='openpyxl')
    escogidos.to_excel(writer, 'escogidos', index=False)
    # escogidos_top.to_excel(writer, 'escogidos_top', index=False)
    # provisionales.to_excel(writer, 'provisionales', index=False)


    writer.save()
    writer.close()
