import alfred3 as al
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from scipy.stats import pearsonr

exp = al.Experiment()
exp += al.ForwardOnlySection(name="main") 

# model 
def pred(file, target):

    # load file 
    df = pd.read_csv("databases/"+file)
    
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
    
    # calculate the Pearson correlation coefficient
    correlation_coefficient, _ = pearsonr(y_pred, y_test)
    print(f"r: {correlation_coefficient}")

# setup 
@exp.setup
def setup(exp):
    exp.progress_bar = al.ProgressBar(show_text=True)


# welcome page
@exp.member(of_section="main")
class Page0(al.Page):
    title = "Welcome"

    def on_exp_access(self):
        self += al.Text("Welcome!", align="center")
        self += al.Text("*Instructions*", align="center")  # instructions

# database+task selection 
@exp.member(of_section="main")
class Page1(al.Page):
    title = "File"

    def on_exp_access(self):
        self += al.TextEntry(toplab="Please enter the file name:", name="file",  align="center")
        self += al.TextEntry(toplab="Please enter the target feature:", name="target",  align="center")

# task 
@exp.member(of_section="main")
class Page2(al.Page):
    title = "Task"

    def on_exp_access(self):
        file_path = 
        target = 
        pred(file_path, target)
        
        self += al.TextEntry(toplab="Please enter your prediction:", name="prediction",  align="center")
           

if __name__ == "__main__":
    exp.run()

## for web browsers except chrome: http://127.0.0.1:5000/start