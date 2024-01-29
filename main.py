import pandas as pd
import keyboard as keyboard

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

class main():
    
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
    rf = RandomForestRegressor(n_estimators = 100, random_state=7)
    rf.fit(X_train, y_train) 

    # predict labels for test
    y_pred = rf.predict(X_test)
    results = pd.DataFrame(y_pred) 
    
    # results['Predicted'] = y_pred
    
    print(results.head(100))
    
    # displays accuracy if space bar pressed 
    while True:
        keyboard.read_key()
        if keyboard.is_pressed("space"):
            # accuracy
            print('Accuracy: {}'.format(rf.score(X_test, y_test)))
        elif keyboard.is_pressed("esc"):
            exit()

if __name__ == '__main__':
    main()
    
# datasets fuilfil model req
# some strong/weak accuracy
# not too difficult task, can b identifiable 
# continuous data

# conceptual problem - how could we use an algorithm that takes/scrutinize human feedback if within precision (human overseer) 
# algo accuracy vs not show
# precision parameter --> expression of confidence commmunicated
# decision experience gap, systematic difference, sampling -> algorithm shows uncertainity/failure + unfailure 
# familiarize w/alfred + qualtrics 
