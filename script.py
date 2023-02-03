# script that reads csv and writes data to tables

import pandas as pd
import numpy as np

# get data
url = "https://github.com/jlomako/quebec-emergency-rooms/raw/main/data/urgence_time.csv"
df = pd.read_csv(url, encoding="latin1")

# get timestamp from last column
timestamp = df.iloc[0, -1]

# select columns (without wait times)
df = df.filter(items=['Region', 'Nom_installation',
                      'Nombre_de_civieres_fonctionnelles \t\t\t\t\t\t' ,
                      'Nombre_de_civieres_occupees',
                      'Nombre_total_de_patients_presents_a_lurgence',
                      'Nombre_total_de_patients_en_attente_de_PEC'
                      ])

# filter rows
df = df.loc[df['Region'].str.contains(r"Montr")]

df.rename(columns={'Nom_installation': 'hospital_name',
                   'Nombre_de_civieres_fonctionnelles \t\t\t\t\t\t': 'beds_total',
                   'Nombre_de_civieres_occupees': 'beds_occ',
                   'Nombre_total_de_patients_presents_a_lurgence': 'patients_total',
                   'Nombre_total_de_patients_en_attente_de_PEC': 'patients_waiting'}, inplace=True)

# replace missings with NaNs
df['beds_total'] = pd.to_numeric(df['beds_total'], errors='coerce')
df['beds_occ'] = pd.to_numeric(df['beds_occ'], errors='coerce')
df['patients_total'] = pd.to_numeric(df['patients_total'], errors='coerce')
df['patients_waiting'] = pd.to_numeric(df['patients_waiting'], errors='coerce')

# calculate occupancy rate if not NaN
f = lambda x: round(100*(x['beds_occ']/x['beds_total'])) if x.notnull().all() else np.NaN
# and add new column occupancy_rate
df['occupancy_rate'] = df.apply(f, axis=1)

# get columns
df = df.filter(items=['hospital_name', 'occupancy_rate', 'patients_total', 'patients_waiting'])

# not really neccessary..
# replace 'Total Regional' with 'Total Montreal'
df.iloc[0,0] = 'TOTAL MONTRÉAL'
# replace name with weird character
df.iloc[2,0] = 'HÔPITAL DU SACRÉ-COEUR DE MONTRÉAL'

# add timestamp to df
df = df.assign(Date = timestamp)

# to integer, to get rid of .0
df['occupancy_rate'] = pd.to_numeric(df['occupancy_rate'], downcast='integer', errors='coerce').astype('Int64')
df['patients_total'] = pd.to_numeric(df['patients_total'], downcast='integer', errors='coerce').astype('Int64')
df['patients_waiting'] = pd.to_numeric(df['patients_waiting'], downcast='integer', errors='coerce').astype('Int64')

# transform variables to rows
df_occupancy = pd.pivot(df, index='Date', columns='hospital_name', values='occupancy_rate')
df_patients_total = pd.pivot(df, index='Date', columns='hospital_name', values='patients_total')
df_patients_waiting = pd.pivot(df, index='Date', columns='hospital_name', values='patients_waiting')

# create csv
# df_occupancy.to_csv("tables/occupancy.csv", header=True, na_rep='NA')
# df_patients_total.to_csv("tables/patients_total.csv", header=True, na_rep='NA')
# df_patients_waiting.to_csv("tables/patients_waiting.csv", header=True, na_rep='NA')

# append
df_occupancy.to_csv("tables/occupancy.csv", header=False, mode="a",  na_rep='NA')
df_patients_total.to_csv("tables/patients_total.csv", header=False, mode="a",  na_rep='NA')
df_patients_waiting.to_csv("tables/patients_waiting.csv", header=False, mode="a",  na_rep='NA')

