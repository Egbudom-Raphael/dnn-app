import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tensorflow import keras
from typing import Dict
# import json
import pandas as pd

app=FastAPI()

origins=['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.post("/predict")
def predict(data: Dict):
    # Convert the input data to a pandas DataFrame
    df = pd.DataFrame.from_dict(data, orient='index').T

    # loading the saved model
    model = keras.models.load_model('1d_conv.hdf5', compile=False)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Make a prediction using the trained model
    y_pred = model.predict(df)
    print(y_pred)
    # Return the prediction as a dictionary
    return f'{y_pred[0][0]}'
