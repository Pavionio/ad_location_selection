import pandas as pd
#%%
df1 = pd.read_csv('submission2ag_SPA.csv') # wnn3
df2 = pd.read_csv('submission5ag_SPA.csv') # wnn32222
df3 = pd.read_csv('submission4ag_SPA.csv') # without_nn_5
#%%
df1.mean()
#%%
df1.value = ((df1.value + df2.value + df3.value) / 3)
#%%
df1.value += 1
df1.to_csv('submit_merged.csv', index=False)
