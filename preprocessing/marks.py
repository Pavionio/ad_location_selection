import pandas as pd
df = pd.read_json('train_data.json')
df = pd.concat([df,pd.json_normalize(df['targetAudience'])], axis=1)
df = df.explode('points').reset_index(drop=True)
df = df.drop(['id', "hash", "targetAudience"], axis=1)
df = pd.concat([df,pd.json_normalize(df['points'])], axis=1)
df.drop("points", inplace=True, axis=1)
df.to_csv("marks.csv", index=False)
