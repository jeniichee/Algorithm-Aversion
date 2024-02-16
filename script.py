import alfred3 as al
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from scipy.stats import pearsonr
from alfred3 import admin

exp = al.Experiment()

# model
def pred(f, target):
    
    # load file 
    df = pd.read_csv("databases/"+f)
    
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

# setup
@exp.setup
def setup(exp):
    exp.progress_bar = al.ProgressBar(show_text=True)

# start section 
# TODO: turn into admin mode 
exp += al.ForwardOnlySection(name="StartSection")
exp.StartSection += al.Page(name="start_pg")
exp.StartSection.start_pg += al.TextEntry(leftlab="Please enter the file name:", name="uploaded_file")
exp.StartSection.start_pg += al.TextEntry(leftlab="Please enter the target feature:", name="t2")

# TODO: consent section 
exp += al.ForwardOnlySection(name="consent")
exp.consent += al.Page(name="pdf")

# instructions section 
exp += al.ForwardOnlySection(name="main")
exp.main += al.Page(name="welcome_pg")
exp.main.welcome_pg += al.Text("Welcome!", align="center")
exp.main.welcome_pg += al.Text("*Instructions*", align="center")

@exp.member(of_section="main")
class Page2(al.Page):

    def on_first_show(self):
        uploaded_file = self.exp.values["uploaded_file"]
        target_feature = self.exp.values["t2"]
        preds, accuracy, correlation_coefficient = pred(uploaded_file, target_feature)
        
        # TODO: make the table fit the frame 
        # html_string = """
        
        # """
        
        # assert html_string == preds.to_html()
        html_element = al.Html(html=preds.to_html())
        self += html_element.height
    
        self += al.Text(f"Accuracy: {accuracy:.2f}%")
        self += al.Text(f"Pearson correlation coefficient: {correlation_coefficient:.2f}")
        self += al.TextEntry(toplab="Please enter your prediction:", name="prediction", align="center")
        
# TODO: final section of the experiment - feedback, payment, and debriefing
@exp.member
class SectionFinale(al.ForwardOnlySection):
    
    def on_exp_access(self): 

        self += al.Page(title = 'Feedback', name = 'feedback')
        self += al.TextEntry(toplab="Feedback?")

if __name__ == "__main__":
    exp.run()

# for web browsers except chrome: http://127.0.0.1:5000/start

## database Pearson r values
# insurance.csv = 0.9203913336104259
# bank = 0.941011708655843
# BMI = 0.9814944355434478
# concrete = 0.960403322918504
# exam = 0.8564969012993616
# happy = 0.9999791281834894
# insurance = 0.9203913336104259
# placement = 0.8432494857338155
# red wine = 0.7211983393453991
# star type = 0.9999321798727429
# tip = 0.7569161669495375
