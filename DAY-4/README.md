# Day 4: Energy Consumption Prediction using AutoGluon

Welcome to Day 4 of the **30 Days of AI Challenge**. Today's project focuses on predicting the energy consumption of buildings using **AutoGluon Tabular**, an AutoML library that automates feature engineering, model selection, hyperparameter tuning, and ensemble stacking.

## 📌 Project Overview

Predicting energy consumption is essential for smart grids, resource optimization, and building management. This project trains a machine learning pipeline on structural, environmental, and occupancy metrics to estimate total energy consumption.

AutoGluon is configured with the `best_quality` preset to perform multi-layer stacking and bagging across diverse algorithms, achieving highly accurate and robust regression predictions.

---

## ⚙️ Technologies Used

- **Python 3.11 / 3.12**
- **AutoGluon Tabular** (AutoML Engine)
- **Pandas** & **NumPy** (Data manipulation)
- **Jupyter Notebooks** (Interactive training and testing)
- **LightGBM** (Core model gradient booster)

---

## 📊 Dataset Description

The dataset consists of 1,000 training records and 100 test records containing structural and environmental parameters:

| Feature Name | Type | Description |
| :--- | :--- | :--- |
| **Building Type** | Categorical | Type of building (`Residential`, `Commercial`, `Industrial`) |
| **Square Footage** | Numerical | Total area of the building in square feet |
| **Number of Occupants** | Numerical | Count of active people inside the building |
| **Appliances Used** | Numerical | Count of active electrical appliances |
| **Average Temperature** | Numerical | Average ambient temperature in Celsius |
| **Day of Week** | Categorical | Categorized as `Weekday` or `Weekend` |
| **Energy Consumption** | Numerical | **Target Variable** (Continuous value representing usage) |

---

## 🤖 Model Training & Architecture

AutoGluon was fitted with the target parameter `Energy Consumption` using:
- **Preset**: `best_quality` (trains multiple models, optimizes weights, and builds an L3 stacked ensemble).
- **Time Limit**: 600 seconds (10 minutes) on a GPU accelerated environment.

### Model Leaderboard
The training run evaluated a total of 110 configurations, with the following top model results:

1. **WeightedEnsemble_L3** (RMSE: `31.38`) 🏆 *Best Model*
2. **WeightedEnsemble_L2** (RMSE: `31.86`)
3. **ExtraTreesMSE_BAG_L2** (RMSE: `34.08`)
4. **LightGBMXT_BAG_L1** (RMSE: `38.74`)

---

## 📁 Project Structure

```text
DAY-4/
├── datasets/
│   ├── train_energy_data.csv       # Training dataset (1,000 rows)
│   └── test_energy_data.csv        # Testing dataset (100 rows)
├── energy_consumption_prediction_model/
│   └── ag-20260709_054303/        # AutoGluon saved model & checkpoints
├── training_and_api_endpoint/
│   ├── api_endpoint.py            # Local python script for testing predictions
│   └── energy_consumption_prediction_TRAINING.ipynb  # Jupyter training notebook
├── README.md                      # Project documentation (this file)
└── requirements.txt               # Day 4 dependencies
```

---

## 🚀 How to Run & Predict

### 1. Install Dependencies
Make sure you have the required packages installed in your active virtual environment:
```bash
pip install autogluon.tabular lightgbm pandas
```

### 2. Run Predictions
Execute the prediction helper script `api_endpoint.py` located inside `training_and_api_endpoint/`:
```bash
python training_and_api_endpoint/api_endpoint.py
```

Example input data in script:
```python
{
    "Building Type": "Industrial",
    "Square Footage": 20000,
    "Number of Occupants": 50,
    "Appliances Used": 20,
    "Average Temperature": 30,
    "Day of Week": "Weekday"
}
```
**Output prediction**: `~4325.69` units of energy consumption.
