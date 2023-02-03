# script that extracts data and writes result to csv
# run daily 

import pandas as pd

# get data
url = "https://github.com/jlomako/quebec-emergency-rooms/raw/main/data/urgence_time.csv"
df = pd.read_csv(url, encoding="latin1")

# get timestamp
timestamp = df.iloc[0, -1]

# select columns with wait times
df = df.filter(items=['Region', 'Nom_installation',
                      'DMS_ambulatoire\t\t\t\t\t\t',
                      'DMS_sur_civiere',
                      ])

df = df.loc[df['Region'].str.contains(r"Montr")]

# rename columns
df.rename(columns={'Nom_installation': 'hospital_name',
                   'DMS_ambulatoire\t\t\t\t\t\t': 'wait_hours',
                   'DMS_sur_civiere': 'wait_hours_stretcher'}, inplace=True)

df = df.filter(items=['hospital_name', 'wait_hours', 'wait_hours_stretcher'])

# replace names
# df.iloc[0,0] = 'TOTAL MONTRÉAL'
# df.iloc[2,0] = 'HÔPITAL DU SACRÉ-COEUR DE MONTRÉAL'

# add timestamp to df
# obs! numbers refer to average wait time on previous day
df = df.assign(Date = timestamp)

# transform wait times to row
df_wait_hours = pd.pivot(df, index='Date', columns='hospital_name', values='wait_hours')
df_wait_hours_stretcher = pd.pivot(df, index='Date', columns='hospital_name', values='wait_hours_stretcher')

# create csv
# df_wait_hours.to_csv("tables/wait_hours.csv", header=True, na_rep='NA')
# df_wait_hours_stretcher.to_csv("tables/wait_hours_stretcher.csv", header=True, na_rep='NA')

# write to csv
df_wait_hours.to_csv("tables/wait_hours.csv", header=False, mode="a",  na_rep='NA')
df_wait_hours_stretcher.to_csv("tables/wait_hours_stretcher.csv", header=False, mode="a",  na_rep='NA')

