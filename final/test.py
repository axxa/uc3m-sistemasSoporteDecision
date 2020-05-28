# Prolog - Auto Generated #
import os, uuid, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
import pandas

os.chdir(u'C:/Users/asan1/PythonEditorWrapper_f6d90d8f-1b01-417d-afbd-1301e138411b')
dataset = pandas.read_csv('input_df_b72dc528-e521-43d1-8cb1-322d5eaa3c98.csv')

matplotlib.pyplot.figure(figsize=(5.55555555555556,4.16666666666667), dpi=72)
matplotlib.pyplot.show = lambda args=None,kw=None: matplotlib.pyplot.savefig(str(uuid.uuid1()))
# Original Script. Please update your script content here and once completed copy below section back to the original editing window #
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

df_auxiliar = pandas.DataFrame(dataset.instrument)
df_auxiliar = df_auxiliar.drop_duplicates()
auxiliar_arr = np.array(df_auxiliar['instrument'])
inst_number = 15
if auxiliar_arr.size > inst_number:
    ref_instrument = auxiliar_arr[inst_number]
    dataset = dataset[dataset['instrument'] == ref_instrument]
    fuente = dataset['fuente'].iloc[0]
    dataset['reporting_date'] = dataset['reporting_date'].str[:10]
    dataset['reporting_date'] = dataset['reporting_date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    dataset= dataset.groupby(['reporting_date']).sum()
    dataset=dataset.sort_index()


    fig, ax = plt.subplots()
    ax.plot_date(dataset.index,dataset['valor_operacion'], linestyle='-')
    ax.plot_date(dataset.index,dataset['valor_operacion'])
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.set(xlabel='Fecha', ylabel='Valor operacion',title=fuente + ': ' + ref_instrument)
    fig.autofmt_xdate()
    ax.grid()

plt.show()


# Epilog - Auto Generated #
os.chdir(u'C:/Users/asan1/PythonEditorWrapper_f6d90d8f-1b01-417d-afbd-1301e138411b')
