# http://127.0.0.1:5000/start  

import pandas as pd
import alfred3 as al

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from scipy.stats import pearsonr

def pred(file, target):

    # load file 
    df = pd.read_csv("databases/"+file)
    
    # optional drop columns 
    # uploaded_file = uploaded_file.drop()
    
    # encode categorical features
    df_encoded = pd.get_dummies(df) 

    # split and train
    X = df_encoded.drop(target, axis=1) # input features
    y = df_encoded[target] # target

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
    predictions['predictions'] = y_pred.tolist()
    # predictions['True Classes'] = y_test
    # predictions['Error'] =  predictions['True Classes'] - predictions['Predictions'] 

    df_out = df.merge(X_test, left_index=True, right_index=True, how='inner')
    df_out = df_out.drop(columns=['total_bill_y', 'size_y', 'sex_Female', 'sex_Male', 'smoker_No', 'smoker_Yes', 'day_Fri', 'day_Sat', 'day_Sun', 'day_Thur', 'time_Dinner', 'time_Lunch', 'tip'], axis=1)

    df_out = df_out.merge(predictions, left_index = True, right_index = True)
    
    # accuracy
    accuracy = rf.score(X_test, y_test)*100
    
    # calculate the Pearson correlation coefficient
    correlation_coefficient, _ = pearsonr(y_pred, y_test)
    
    return df_out.head(100), accuracy, correlation_coefficient
    
exp = al.Experiment()

# setup
@exp.setup
def setup(exp):
    exp.progress_bar = al.ProgressBar(show_text=True)

# TODO: start section 
# exp += al.ForwardOnlySection(name="consent")
# exp.consent += al.Page(name="pdf")

# TODO: consent section 
# exp += al.ForwardOnlySection(name="consent")
# exp.consent += al.Page(name="pdf")

# instructions section 
exp += al.ForwardOnlySection(name="main")
exp.main += al.Page(name="welcome_pg")
exp.main.welcome_pg += al.Text("Welcome!", align="center")
exp.main.welcome_pg += al.Text("""
We are researchers from Queen\'s University, Belfast. We are investigating judgment and decision making.
In this study, you\'ll be asked to make judgments and predictions. The study should take __ minutes to complete. 
Your participation is entirely voluntary. You can end the survey at any point, for any reason, without penalty. 
Your responses will be anonymised and the data will be held securely. 
This means there is no way for anybody to possibly link the data to you. 
This includes us as the researchers, which means that once you complete the study, 
we will not have the means to withdraw your data after this point.
""", align="center")

@exp.member(of_section="main")
class Page2(al.Page):

    def on_first_show(self):
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        preds, accuracy, correlation_coefficient = pred(uploaded_file, target_feature)

        html_element = al.Html(html=preds.to_html(), name="table", align="center")
        self += html_element
        self += al.Hline()
        self += al.Text(f"Accuracy: {accuracy:.2f}%")
        self += al.Text(f"Pearson correlation coefficient: {correlation_coefficient:.2f}")
        self += al.TextEntry(toplab="Please enter your prediction:", name="prediction", align="center")
        
# TODO: confidence levels   
     
# TODO: final section of the experiment - feedback, payment, and debriefing

if __name__ == "__main__":
    exp.run()
    
