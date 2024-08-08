# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 17:52:06 2024

@author: omaer
"""

import pandas as pd
import tensorflow as tf
import tensorflow_federated as tff

# Carica i dati pre-elaborati
train_df = pd.read_csv('training_data.csv')
test_df = pd.read_csv('testing_data.csv')

# Converti i dati in tensori
def dataframe_to_tf_dataset(df, shuffle=True, batch_size=32):
    df = df.copy()
    labels = df.pop('total_production')  # Assume 'total_production' è la colonna target
    dataset = tf.data.Dataset.from_tensor_slices((df.values, labels.values))
    if shuffle:
        dataset = dataset.shuffle(buffer_size=len(df))
    dataset = dataset.batch(batch_size)
    return dataset

train_dataset = dataframe_to_tf_dataset(train_df)
test_dataset = dataframe_to_tf_dataset(test_df, shuffle=False)

# Definisci un modello LSTM Keras
def create_lstm_model(input_shape):
    model = tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(input_shape=input_shape),
        tf.keras.layers.Reshape(target_shape=(input_shape[0], 1)),
        tf.keras.layers.LSTM(128, return_sequences=True),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(64),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1)  # Output layer
    ])
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
    return model

# Funzione per creare il modello federato
def model_fn():
    input_shape = (train_df.shape[1] - 1,)  # Numero di caratteristiche meno la colonna target
    keras_model = create_lstm_model(input_shape)
    return tff.learning.from_keras_model(
        keras_model,
        input_spec=train_dataset.element_spec,
        loss=tf.keras.losses.MeanSquaredError(),
        metrics=[tf.keras.metrics.MeanAbsoluteError()]
    )

# Configura l'algoritmo di federazione
iterative_process = tff.learning.build_federated_averaging_process(model_fn)

# Inizializza lo stato
state = iterative_process.initialize()

# Esegui l'addestramento federato per 100 epoche
NUM_ROUNDS = 100
for round_num in range(1, NUM_ROUNDS + 1):
    state, metrics = iterative_process.next(state, [train_dataset])
    print(f'Round {round_num}, Metrics: {metrics}')

# Valutazione del modello federato
evaluation = tff.learning.build_federated_evaluation(model_fn)
test_metrics = evaluation(state.model, [test_dataset])
print(f'Test Metrics: {test_metrics}')

# Salva il modello addestrato
def save_model(state, filepath):
    input_shape = (train_df.shape[1] - 1,)
    keras_model = create_lstm_model(input_shape)
    keras_model.compile(optimizer='adam', loss='mean_squared_error')
    
    # Carica i pesi dal modello federato
    keras_model.set_weights(tff.learning.keras_weights_from_model(state.model))
    
    # Salva il modello
    keras_model.save(filepath)

save_model(state, 'federated_model.h5')

# Carica il modello addestrato
loaded_model = tf.keras.models.load_model('federated_model.h5')

# Fai previsioni sul set di test
def predict_with_model(model, df):
    dataset = tf.data.Dataset.from_tensor_slices((df.values)).batch(32)
    predictions = model.predict(dataset)
    return predictions

predictions = predict_with_model(loaded_model, test_df.drop(columns=['total_production']))
predicted_df = test_df.copy()
predicted_df['predicted_total_production'] = predictions

# Salva le previsioni in un file CSV
predicted_df.to_csv('predicted_testing_data.csv', index=False)

