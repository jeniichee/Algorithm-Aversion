import pandas as pd
import os

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

"""
Prediction function that takes in a file and a target feature.
Returns dataframe w/predicted values of target feature, based on other existing features.  
"""
def pred(file, target):

    # load file 
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases/", file))
    
    # encode categorical features
    df_encoded = pd.get_dummies(df) 

    # split and train
    X = df_encoded.drop(target, axis=1) # input features
    y = df_encoded[target] # target

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7)

    # the model
    rf = RandomForestRegressor(n_estimators=100, random_state=7)
    rf.fit(X_train, y_train) 

    # predict labels for test
    y_pred = rf.predict(X_test)

    # cues 
    df_out = df.merge(X_test, left_index=True, right_index=True, how='inner')
    df_out = df_out.drop(columns=['total_bill_y', 'size_y', 'sex_Female', 
                                  'sex_Male', 'smoker_No', 'smoker_Yes', 
                                  'day_Fri', 'day_Sat', 'day_Sun', 'day_Thur', 
                                  'time_Dinner', 'time_Lunch', 'tip'], axis=1) # drop encoded columns
    
    # cues w/true values and predictions 
    df_out_preds = df_out.copy()
    df_out_preds["Algorithm estimate"] = [round(val, 2) for val in y_pred.tolist()]
    df_out_preds["true value"] = round(y_test, 2)
    
    # TODO: hybrid estimates 
    # df_out_preds["hybrid's estimate"] = []
    
    # TODO: human estimates 
    # df_out_preds["human's estimate"] = []

    # rename columns 
    df_out.rename(columns = {"total_bill_x": "total bill", "size_x": "number of guests"}, inplace = True)
    df_out_preds.rename(columns = {"total_bill_x": "total bill", "size_x": "number of guests"}, inplace = True)
    
    return df_out.head(100), df_out_preds.head(100)
    
    
    
    