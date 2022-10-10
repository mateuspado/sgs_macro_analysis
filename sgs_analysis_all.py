# Importa as bibliotecas
import numpy as np
import pandas as pd
import datetime as dt
import time
import ipeadatapy as ip
from bcb import sgs
from matplotlib import pyplot as plt
import seaborn as sns

comprometimento = sgs.get({'comprometimento de renda' : 19879}, start='2019-01-01')

# Busca as séries sobre concessões de crédito no SGS
credito = sgs.get({'total' : 20631,
                   'pj' : 20632,
                   'pf' : 20633,
                   'livre' : 20634,
                   'direcionado' : 20685}, start='2019-01-01', end = time.strftime("%Y-%m-%d"))

# Divide a série por 1000
credito = credito.div(1000)

# Busca a série do índice do IPCA e renomeia a coluna de valor
ipca = (
        ip.timeseries('PRECOS12_IPCA12')
        [['VALUE (-)']]
        .rename(columns = {'VALUE (-)' : 'ipca'})
        )

# Junta o data frame de crédito e ipca para ajustar na mesma data
credito_ipca = credito.join(ipca)

# Pega o deflator base (o último índice da série do ipca)
deflator_base = credito_ipca['ipca'].iloc[-1]

# Calcula o deflator para deflacionar os valores de crédito
deflator = deflator_base / credito_ipca.loc[:,['ipca']]

# Multiplica os valores pelo deflator para obter os valores reais
credito_reais = credito.mul(deflator.ipca, axis = 'index')

# Busca as séries sobre juros, spread e inadimplência no SGS
dadosmacro = sgs.get({'inadimplencia' : 21082,
                    'juro' : 20714,
                 'spread' : 20783,
                 'desemprego': 24369,
                 'credito total': 20539}, start='2019-01-01')

selic = sgs.get({'selic': 432}, start='2019-01-01')

# Juntando os dados
macrocredito = dadosmacro.merge(comprometimento, on = 'Date', how = 'left').merge(selic, on = 'Date', how = 'left').merge(credito, on = 'Date', how = 'left')
macrocredito_reais = dadosmacro.merge(comprometimento, on = 'Date', how = 'left').merge(selic, on = 'Date', how = 'left').merge(credito_reais, on = 'Date', how = 'left')

# Criando planilhas para os dados
macrocredito.to_csv('macrocredito.csv')
macrocredito_reais.to_csv('macrocredito_reais.csv')

# Torna em formato long
macrocredito_long = pd.melt(macrocredito.reset_index(),
                     id_vars = 'Date',
                     value_vars = macrocredito.columns,
                     var_name = 'variable',
                     value_name = 'values')

# Torna em formato long
macrocredito_reais_long = pd.melt(macrocredito_reais.reset_index(),
                     id_vars = 'Date',
                     value_vars = macrocredito_reais.columns,
                     var_name = 'variable',
                     value_name = 'values')

# Cria tabelas long
macrocredito_long.to_csv('macrocredito_long.csv')
macrocredito_reais_long.to_csv('macrocredito_reais_long.csv')

# Configura o tema do gráfico
## Cores
colors = ['#282f6b', '#b22200', '#eace3f', '#224f20', '#b35c1e', '#419391', '#839c56','#3b89bc']

## Tamanho
theme = {'figure.figsize' : (15, 10)}

## Aplica o tema
sns.set_theme(rc = theme,
              palette = colors)

# Plota o crédito desinflacionário total
sns.lineplot(x = 'Date',
             y = 'values',
             hue = 'variable',
             data = macrocredito_reais_long[macrocredito_reais_long.variable.isin(['total', 'livre'])]).set(title = 'Concessões desinflacionárias mensais de crédito: TotalxLivre',
                                                xlabel = '',
                                                ylabel = 'R$ Bilhões')

# Adiciona a fonte no gráfico           
plt.annotate('Fonte: Dados do BCB/SGS e IPEA(IPCA12)',
            xy = (1.0, -0.07),
            xycoords='axes fraction',
            ha='right',
            va="center",
            fontsize=10)

plt.savefig('credito_reais.png')
plt.close()

# Plota o dados de taxas de juros
sns.lineplot(x = 'Date',
             y = 'values',
             hue = 'variable',
             data = macrocredito_long[macrocredito_long.variable.isin(['inadimplencia','comprometimento de renda', 'juro'])]).set(title = 'Inadimplencia X  Comprometimento X Juros',
                                                xlabel = '',
                                                ylabel = 'Em porcentagem(%)')

# Adiciona a fonte no gráfico           
plt.annotate('Fonte: Dados do BCB/SGS',
            xy = (1.0, -0.07),
            xycoords='axes fraction',
            ha='right',
            va="center",
            fontsize=10)

plt.savefig('inadimplencia_comprometimento.png')
plt.close()

# Plota o dados de taxas de juros
sns.lineplot(x = 'Date',
             y = 'values',
             hue = 'variable',
             data = macrocredito_long[macrocredito_long.variable.isin(['inadimplencia','selic', 'desemprego' ])]).set(title = 'Inadimplencia X Selic X Desemprego' ,
                                                xlabel = '',
                                                ylabel = 'Em porcentagem(%)')

# Adiciona a fonte no gráfico         
plt.annotate('Fonte: Dados do BCB/SGS',
            xy = (1.0, -0.07),
            xycoords='axes fraction',
            ha='right',
            va="center",
            fontsize=10)

plt.savefig('inadimplencia_desemprego.png')
plt.close()

# Plota o dados de taxas de juros
sns.lineplot(x = 'Date',
             y = 'values',
             hue = 'variable',
             data = macrocredito_long[macrocredito_long.variable.isin(['inadimplencia','juro', 'spread'])]).set(title = 'Inadimplencia X Juros X Spread',
                                                xlabel = '',
                                                ylabel = 'Em porcentagem(%)')

# Adiciona a fonte no gráfico           
plt.annotate('Fonte: Dados do BCB/SGS',
            xy = (1.0, -0.07),
            xycoords='axes fraction',
            ha='right',
            va="center",
            fontsize=10)

plt.savefig('inadimplencia_spread.png')

