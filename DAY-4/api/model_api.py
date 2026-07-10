from autogluon.tabular import TabularPredictor

model_path=r"C:\Users\ACER\OneDrive\Desktop\30DaysOfAI-CHALLENGE-IN-PUBLIC\DAY-4\ENERGY_CONSUMPTION_PREDICTION_USING_AUTOGLUON\energy_consumption_prediction_model\ag-20260709_054303"

predictor=TabularPredictor.load(model_path)

# app = FastAPI(title="Energy Consumption Prediction API")

# class InputData(BaseModel):
#     Building_Type: str
#     Square_Footage: int
#     Number_of_Occupants: int
#     Appliances_Used: int
#     Average_Temperature: float
#     Day_of_Week: str

# @app.post("/predict")
# def predict(data: InputData):
#     df = pd.DataFrame([data.dict()])
#     prediction = predictor.predict(df)
#     return {"predicted_energy_consumption": float(prediction[0])}