# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 13:42:04 2024

@author: omaer
"""
import pandas as pd

# Step 1: Carica il file Excel e filtra per le ore di luce
df = pd.read_excel('Total_Producers.xlsx')

sunlight_hours = {
    1: (8, 16),  # Gennaio
    2: (8, 17),  # Febbraio
    3: (7, 18),  # Marzo
    4: (6, 19),  # Aprile
    5: (5, 20),  # Maggio
    6: (5, 21),  # Giugno
    7: (6, 21),  # Luglio
    8: (6, 20),  # Agosto
    9: (7, 19),  # Settembre
    10: (7, 18),  # Ottobre
    11: (8, 17),  # Novembre
    12: (8, 16)  # Dicembre
}

df['datetime'] = pd.to_datetime(df['datetime'])
df['month'] = df['datetime'].dt.month
df['hour'] = df['datetime'].dt.hour

def is_sunlight_hour(row):
    month = row['month']
    hour = row['hour']
    start_hour, end_hour = sunlight_hours[month]
    return start_hour <= hour < end_hour

sunlight_df = df[df.apply(is_sunlight_hour, axis=1)]
sunlight_df = sunlight_df.drop(columns=['month', 'hour'])

output_file_path = 'Sunlight_Hours_Producers.xlsx'
sunlight_df.to_excel(output_file_path, index=False)

# Step 2: Sostituisci intervalli di date con valori specifici
df = pd.read_excel(output_file_path)

columns_to_keep = ['datetime'] + list(range(1, 15))
df = df[columns_to_keep]
df['datetime'] = pd.to_datetime(df['datetime'])

start_replace = '2019-11-01 08:00:00'
end_replace = '2019-11-06 16:45:00'
start_source = '2019-11-07 08:00:00'
end_source = '2019-11-07 08:00:00'

target_range = (df['datetime'] >= start_replace) & (df['datetime'] <= end_replace)
source_range = (df['datetime'] >= start_source) & (df['datetime'] <= end_source)

source_data = df[source_range].copy()
source_data = pd.concat([source_data]*((target_range.sum() // len(source_data)) + 1), ignore_index=True).iloc[:target_range.sum()]

df.loc[target_range, columns_to_keep[1:]] = source_data[columns_to_keep[1:]].values

output_file_path = 'Sunlight_Hours_Producers.xlsx'
df.to_excel(output_file_path, index=False)

# Step 3: Processa i valori zero nelle colonne specificate
df = pd.read_excel(output_file_path)

columns_to_process = list(range(0, 15))

for column in columns_to_process:
    for index, value in df[column].items():
        if value == 0:
            found_value = False
            for offset in range(1, 15):
                if index + offset < len(df) and df.iloc[index + offset][column] != 0:
                    df.at[index, column] = df.iloc[index + offset][column]
                    found_value = True
                    break
            if not found_value:
                for offset in range(1, 15):
                    if index - offset >= 0 and df.iloc[index - offset][column] != 0:
                        df.at[index, column] = df.iloc[index - offset][column]
                        break

output_file_path = 'Processed_Sunlight_Hours_Producers.xlsx'
df.to_excel(output_file_path, index=False)

# Step 4: Completa l'intervallo di date a 15 minuti e aggiungi riga iniziale
df = pd.read_excel(output_file_path)

columns_to_keep = ['datetime'] + list(range(1, 15))
df = df[columns_to_keep]

df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)

full_index = pd.date_range(start='2019-01-01 00:15:00', end='2019-12-31 23:45:00', freq='15T')
df = df.reindex(full_index)
df.fillna(0, inplace=True)

df.reset_index(inplace=True)
df.rename(columns={'index': 'datetime'}, inplace=True)

first_row = pd.DataFrame({'datetime': [pd.Timestamp('2019-01-01 00:00:00')]})
for col in range(1, 15):
    first_row[col] = 0
df = pd.concat([first_row, df], ignore_index=True)

output_file_path = 'Completed_Processed.xlsx'
df.to_excel(output_file_path, index=False)

