import pandas as pd
from pandas import DataFrame
import egrep

df = pd.read_excel('./test.xlsx')
df2 = pd.read_excel('./2.xlsx')
df3 = df.set_index(['名字'])[~df.set_index(['名字']).isin(df2.set_index(['名字'])).all(1)].reset_index()
"""
for i in range(0,df.shape[0]):
    print(df.values[i][0])
"""
print(df3.iloc[0,0])

#df.to_excel('2.xlsx')
