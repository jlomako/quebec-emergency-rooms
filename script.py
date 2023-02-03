# script that reads csv and writes data to tables

import pandas as pd
import numpy as np

# get data
url = "https://github.com/jlomako/quebec-emergency-rooms/raw/main/data/urgence_time.csv"
df = pd.read_csv(url, encoding="latin1")

timestamp = df.iloc[0, -1]

# select columns
df = df.filter(items=['Region', 'Nom_installation',
                      'Nombre_de_civieres_fonctionnelles \t\t\t\t\t\t' ,
                      'Nombre_de_civieres_occupees',
                      'Nombre_total_de_patients_presents_a_lurgence',
                      'Nombre_total_de_patients_en_attente_de_PEC',
                      'DMS_ambulatoire\t\t\t\t\t\t'
                      ])

# filter rows
df = df.loc[df['Region'].str.contains(r"Montr")]

# rename columns
df.rename(columns={'Nom_installation': 'hospital_name',
                   'Nombre_de_civieres_fonctionnelles \t\t\t\t\t\t': 'beds_total',
                   'Nombre_de_civieres_occupees': 'beds_occ',
                   'Nombre_total_de_patients_presents_a_lurgence': 'patients_total',
                   'Nombre_total_de_patients_en_attente_de_PEC': 'patients_waiting',
                   'DMS_ambulatoire\t\t\t\t\t\t': 'wait_hours'}, inplace=True)

# calculate occupancy rate if not NaN
f = lambda x: round(100*(pd.to_numeric(x['beds_occ'])/pd.to_numeric(x['beds_total']))) if x.notnull().all() else np.NaN
# f = lambda x: round(100*(x['beds_occ']/x['beds_total'])) if x.notnull().all() else np.NaN

# and add new column occupancy_rate
df['occupancy_rate'] = df.apply(f, axis=1)

df = df.filter(items=['hospital_name', 'occupancy_rate', 'patients_total', 'patients_waiting', 'wait_hours'])

# replace 'Total Regional' with 'Total Montreal'
df.iloc[0,0] = 'TOTAL MONTRÉAL'

# replace name with weird character
df.iloc[2,0] = 'HÔPITAL DU SACRÉ-COEUR DE MONTRÉAL'

# add timestamp to df
df = df.assign(Date = timestamp)

# transform variables to rows
df_occupancy = pd.pivot(df, index='Date', columns='hospital_name', values='occupancy_rate')
df_patients_total = pd.pivot(df, index='Date', columns='hospital_name', values='patients_total')
df_patients_waiting = pd.pivot(df, index='Date', columns='hospital_name', values='patients_waiting')
df_wait_hours = pd.pivot(df, index='Date', columns='hospital_name', values='wait_hours')

# write to file
df_occupancy.to_csv("tables/occupancy.csv", header=False, mode="a",  na_rep='NA')
df_patients_total.to_csv("tables/patients_total.csv", header=False, mode="a",  na_rep='NA')
df_patients_waiting.to_csv("tables/patients_waiting.csv", header=False, mode="a",  na_rep='NA')
df_wait_hours.to_csv("tables/wait_hours.csv", header=False, mode="a",  na_rep='NA')
 
