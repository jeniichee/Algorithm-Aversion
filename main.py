import pandas as pd
import keyboard as kb
import os # accessing directory structure on macOS

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

class Main():
    
    # # file directory for macbook and windows ?
    # for dirname, _, filenames in os.walk('/kaggle/input'):
    #     for filename in filenames:
    #         print(os.path.join(dirname, filename))
        
    # load file 
    file = input("file name: ") 
    df = pd.read_csv(file)
    
    # target feature 
    target = input("predict: ")
    
    # encode categorical features
    df = pd.get_dummies(df) 

    # split and train
    X = df.drop(target, axis=1) # input features
    y = df[target] # target

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7)
    
    # # StandardScaler to normalize numeric data 
    # scaler = StandardScaler() 
    # scaler.fit(X_train)
    # X_train = scaler.transform(X_train) # transform training data
    # X_test = scaler.transform(X_test) # transform test data

    # the model
    rf = RandomForestRegressor(n_estimators=100, random_state=7)
    rf.fit(X_train, y_train) 

    # predict labels for test
    y_pred = rf.predict(X_test)
    
    # converting y_pred 
    predictions = pd.DataFrame()
    predictions['Predictions'] = y_pred.tolist()
    df_out = pd.merge(X_test, predictions, left_index = True, right_index = True)
        
    predictions['True Classes'] = y_test
    predictions['Error'] =  predictions['True Classes'] - predictions['Predictions'] 
    df_out = pd.merge(X_test, predictions, left_index = True, right_index = True)
    print(df_out.head(100))
    
    # accuracy
    print('Accuracy: {}'.format((rf.score(X_test, y_test))*100))

if __name__ == '__main__':
    Main()
    
# datasets fuilfil model req
# some strong/weak accuracy
# not too difficult task, can b identifiable 
# continuous data

# conceptual problem - how could we use an algorithm that takes/scrutinize human feedback if within precision (human overseer) 
# algo accuracy vs not show
# precision parameter --> expression of confidence commmunicated
# decision experience gap, systematic difference, sampling -> algorithm shows uncertainity/failure + unfailure 
# familiarize w/alfred + qualtrics 
