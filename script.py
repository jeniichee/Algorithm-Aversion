import alfred3 as al
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from scipy.stats import pearsonr

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
    df_out = pd.merge(X_test, predictions, left_index = True, right_index = True) # final df
    
    # accuracy
    accuracy = (rf.score(X_test, y_test)) * 100
    
    # calculate the Pearson correlation coefficient
    correlation_coefficient, _ = pearsonr(y_pred, y_test)
    
    return df_out.head(100), accuracy, correlation_coefficient
    
exp = al.Experiment()
exp += al.ForwardOnlySection(name="main")

# setup
@exp.setup
def setup(exp):
    exp.progress_bar = al.ProgressBar(show_text=True)
    
exp.main += al.Page(name="page0")
exp.main.page0 += al.Text("Welcome!", align="center")
exp.main.page0 += al.Text("*Instructions*", align="center")


## turn into admin page/behind the scenes 
exp.main += al.Page(name="page1")
exp.main.page1 += al.TextEntry(toplab="Please enter the file name:", name="t1")
exp.main.page1 += al.TextEntry(toplab="Please enter the target feature:", name="t2")

@exp.member(of_section="main")
class Page2(al.Page):

    def on_first_show(self):
        input_on_page1 = self.exp.values["t1"]
        input_on_page2 = self.exp.values["t2"]
        preds, accuracy, correlation_coefficient = pred(input_on_page1, input_on_page2)
        
        df = preds.to_string(index=False)
        
        self += al.Text(df)
        self += al.Text(f"Accuracy: {accuracy:.2f}%")
        self += al.Text(f"Pearson correlation coefficient: {correlation_coefficient:.4f}")
         
        self += al.TextEntry(toplab="Please enter your prediction:", name="prediction", align="center")

if __name__ == "__main__":
    exp.run()

## for web browsers except chrome: http://127.0.0.1:5000/start
## trying to figure out admin mode 
## retrieving data from sessions 