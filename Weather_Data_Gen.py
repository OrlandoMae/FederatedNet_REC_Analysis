# -*- coding: utf-8 -*-
"""
Creato il 6 Agosto 2024 alle 12:32:08

@author: omaer
"""
import pandas as pd
import random
from datetime import timedelta

# Carica il file Excel
file_path = 'Weather_Data.xlsx'

# Leggi i dati
df_weather = pd.read_excel(file_path, sheet_name='Weather')

# Convertire la colonna 'datetime' in oggetti datetime per facilitare l'analisi temporale
df_weather['datetime'] = pd.to_datetime(df_weather['datetime'])

# Definire i limiti stagionali per temperatura e umidità
seasonal_limits = {
    "winter": {"temperature": (0, 15), "humidity": (70, 90)},
    "spring": {"temperature": (8, 25), "humidity": (50, 70)},
    "summer": {"temperature": (18, 30), "humidity": (30, 70)},
    "autumn": {"temperature": (8, 20), "humidity": (50, 70)}
}

# Definire le ore di luce per la radiazione solare
sunlight_hours = {
    1: (8, 16),  # gennaio
    2: (8, 17),  # febbraio
    3: (7, 18),  # marzo
    4: (6, 19),  # aprile
    5: (5, 20),  # maggio
    6: (5, 21),  # giugno
    7: (6, 21),  # luglio
    8: (6, 20),  # agosto
    9: (7, 19),  # settembre
    10: (7, 18),  # ottobre
    11: (8, 17),  # novembre
    12: (8, 16)  # dicembre
}

# Funzione per determinare la stagione basata sul mese
def get_season(month):
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"

# Funzione per calcolare la radiazione solare in base alla stagione e ora
def calculate_solar_radiation(hour, season, sunlight_start, sunlight_end):
    if sunlight_start <= hour <= sunlight_end:
        peak = (sunlight_end - sunlight_start) / 2 + sunlight_start
        solar_intensity = (1 - abs(hour - peak) / (peak - sunlight_start))  # Intensità massima a mezzogiorno
        base_radiation = 1050 if season in ['spring', 'summer'] else 750
        return max(2, base_radiation * solar_intensity)
    return 0

# Funzione per generare i dati mancanti
def generate_missing_data(df, start_date, end_date):
    current_date = start_date
    new_data = []
    
    # Inizializzare con l'ultimo set di valori esistenti
    last_temperature = df.iloc[-1]['TemperatureC']
    last_dewpoint = df.iloc[-1]['DewpointC']
    last_pressure = df.iloc[-1]['PressurehPa']
    last_humidity = df.iloc[-1]['Humidity']
    last_wind_speed = df.iloc[-1]['WindSpeedKMH']
    last_wind_gust = df.iloc[-1]['WindSpeedGustKMH']
    
    while current_date <= end_date:
        season = get_season(current_date.month)
        temp_limits = seasonal_limits[season]["temperature"]
        humidity_limits = seasonal_limits[season]["humidity"]
        
        # Calcolare variazioni limitate per ogni parametro
        temp_variation = random.uniform(-0.75, 0.75)  # Limitazione per 15 minuti
        dewpoint_variation = random.uniform(-0.75, 0.75)  # Limitazione per 15 minuti
        pressure_variation = random.uniform(-1, 1)
        wind_speed_variation = random.uniform(-5, 5)
        wind_gust_variation = random.uniform(-2, 2)
        humidity_variation = random.uniform(-1, 1)
        
        # Ciclo diurno della temperatura
        hour = current_date.hour
        month = current_date.month

        # Differenza di temperatura tra giorno e notte
        day_night_difference = random.uniform(4, 8)  # Differenza tra 4 e 8 gradi

        # Calcolare l'aggiustamento di temperatura per ciclo diurno
        if hour == 12 or hour == 13:
            temperature = temp_limits[1]  # Massima temperatura tra le 12:00 e le 13:00
        elif hour < 12:
            temp_adjustment = hour / 12.0
            temperature = temp_limits[0] + (temp_limits[1] - temp_limits[0]) * temp_adjustment
        else:
            temp_adjustment = (24 - hour) / 12.0
            temperature = temp_limits[0] + (temp_limits[1] - temp_limits[0]) * temp_adjustment - day_night_difference
        
        # Limita la variazione della temperatura a massimo 0.75 gradi per intervallo di 15 minuti
        temperature = max(last_temperature - 0.75, min(last_temperature + 0.75, temperature))
        temperature = max(temp_limits[0], min(temperature + temp_variation, temp_limits[1]))

        # Calcolare il punto di rugiada
        dewpoint = last_dewpoint + dewpoint_variation
        dewpoint = max(temp_limits[0], min(dewpoint, temperature))  # Il punto di rugiada non può superare la temperatura

        # Ciclo diurno dell'umidità
        humidity = last_humidity + humidity_variation * (1 - temp_adjustment)
        humidity = max(humidity_limits[0], min(humidity, humidity_limits[1]))

        # La pressione è influenzata inversamente dalla velocità del vento
        pressure = last_pressure + pressure_variation - (wind_speed_variation / 5.0)
        pressure = max(980, min(pressure, 1050))  # Limiti realistici di pressione

        # Calcolo della velocità del vento e delle raffiche
        wind_speed = max(0, last_wind_speed + wind_speed_variation)
        wind_gust = max(wind_speed, last_wind_gust + wind_gust_variation)  # Le raffiche sono sempre maggiori della velocità base

        # Calcolare la radiazione solare
        sunlight_start, sunlight_end = sunlight_hours[month]
        solar_radiation = calculate_solar_radiation(hour, season, sunlight_start, sunlight_end)

        # Simulare la pioggia in base all'umidità e ai limiti stagionali
        rain_chance = humidity / 100.0
        rain = 0
        if random.random() < rain_chance:
            rain = random.uniform(0, 5)  # Simulazione di pioggia fino a 5 mm all'ora

        # Aggiungi una nuova riga di dati, arrotondando i valori agli interi
        new_data.append({
            "datetime": current_date,
            "TemperatureC": round(temperature),
            "DewpointC": round(dewpoint),
            "PressurehPa": round(pressure),
            "WindSpeedKMH": round(wind_speed),
            "WindSpeedGustKMH": round(wind_gust),
            "Humidity": round(humidity),
            "HourlyPrecipMM": round(rain),
            "dailyrainMM": round(rain),  # Semplificazione, può essere aggiustata per accumulo giornaliero
            "SolarRadiationWatts_m2": round(solar_radiation),
            "SeasonCode": {"winter": 1, "spring": 2, "summer": 3, "autumn": 4}[season],
            "Month": month,
            "Season": season
        })
        
        # Aggiorna i valori noti più recenti
        last_temperature = temperature
        last_dewpoint = dewpoint
        last_pressure = pressure
        last_humidity = humidity
        last_wind_speed = wind_speed
        last_wind_gust = wind_gust

        # Incrementa il datetime di 15 minuti
        current_date += timedelta(minutes=15)
    
    return pd.DataFrame(new_data)

# Generare i dati mancanti da giugno a dicembre
start_missing_date = df_weather['datetime'].max() + timedelta(minutes=15)
end_missing_date = pd.Timestamp('2019-12-31 23:45:00')

# Generare i dati per il periodo mancante
df_missing_data = generate_missing_data(df_weather, start_missing_date, end_missing_date)

# Aggiungere mese e stagione ai dati esistenti
df_weather['Month'] = df_weather['datetime'].dt.month
df_weather['Season'] = df_weather['Month'].apply(get_season)

# Unire i dati esistenti con quelli generati
df_complete = pd.concat([df_weather, df_missing_data], ignore_index=True)

# Ordinare i dati per la colonna datetime per assicurare la continuità temporale
df_complete.sort_values(by='datetime', inplace=True)

# Visualizzare le prime righe del dataset completo
print(df_complete.head())

# Opzionale: Salvare il dataframe completo su un nuovo file Excel
df_complete.to_excel('Weather_Data_Gen.xlsx', index=False)
