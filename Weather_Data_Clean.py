# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 13:04:27 2024

@author: omaer
"""
import pandas as pd

# Carica il file Excel esistente
input_file = '../../Dataset.xlsx'  # Sostituisci con il nome del tuo file originale
output_file = 'Weather_Data.xlsx'  # Nome del file che verrà creato

# Leggi il foglio di lavoro 'Weather'
df_weather = pd.read_excel(input_file, sheet_name='Weather')

# Rimuovi le righe dove tutte le colonne hanno valori 0 o NaN
df_weather_cleaned = df_weather.loc[~((df_weather.isnull()) | (df_weather == 0)).all(axis=1)].copy()

# Converti la colonna 'datetime' in formato datetime gestendo errori e valori non validi
df_weather_cleaned['datetime'] = pd.to_datetime(df_weather_cleaned['datetime'], errors='coerce')

# Calcola l'intervallo di tempo tra il primo e l'ultimo timestamp
start_time = df_weather_cleaned['datetime'].min()
end_time = df_weather_cleaned['datetime'].max()

# Genera un intervallo di datetime ogni 15 minuti tra start_time ed end_time
full_datetime_range = pd.date_range(start=start_time, end=end_time, freq='15T')

# Imposta l'indice del DataFrame per facilitare il merge con l'intervallo completo
df_weather_cleaned.set_index('datetime', inplace=True)

# Creiamo un nuovo DataFrame con l'intervallo di datetime corretto
corrected_df = pd.DataFrame(index=full_datetime_range)

# Uniamo i dati originali con il nuovo intervallo di datetime
corrected_df = corrected_df.join(df_weather_cleaned)

# Riempie i valori mancanti utilizzando l'interpolazione
corrected_df.interpolate(method='linear', inplace=True)

# Arrotonda tutti i valori numerici al numero intero più vicino
corrected_df = corrected_df.round()

# Reimposta l'indice in modo che 'datetime' sia di nuovo una colonna
corrected_df.reset_index(inplace=True)
corrected_df.rename(columns={'index': 'datetime'}, inplace=True)

# Salva il foglio corretto in un nuovo file Excel
with pd.ExcelWriter(output_file) as writer:
    corrected_df.to_excel(writer, sheet_name='Weather', index=False)

print(f"I dati corretti sono stati salvati in {output_file}.")

