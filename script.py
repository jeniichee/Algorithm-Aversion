"""
http://127.0.0.1:5000/start  

"""
import pandas as pd
import alfred3 as al
import os

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# prediction function 
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
    
    # cues w/true values and predictions (TODO: show w/parameters or create different dataframe)
    df_out_preds = df_out.copy()
    df_out_preds['your advisor\'s estimate'] = [round(val) for val in y_pred.tolist()]
    df_out_preds['true value'] = round(y_test)

    # rename columns 
    df_out.rename(columns = {"total_bill_x": "total bill", "size_x": "number of guests"}, inplace = True)
    df_out_preds.rename(columns = {"total_bill_x": "total bill", "size_x": "number of guests"}, inplace = True)
    
    # # accuracy
    # accuracy = rf.score(X_test, y_test)*100
    
    # # calculate the Pearson correlation coefficient
    # correlation_coefficient, _ = pearsonr(y_pred, y_test)
    
    return df_out.head(100), df_out_preds.head(100)

# create experiment 
exp = al.Experiment()
trials = 10 

# Section 0: setup 
exp += al.HideOnForwardSection(name="setup_section")
exp.setup_section += al.Page(name="setup_page")
exp.setup_section.setup_page += al.SingleChoiceButtons('Human', 'Algorithm', 'Toad', name = 'condition')

# Section 01: instructions section 
exp += al.ForwardOnlySection(name="instructions_section")

# TODO: different instructions and labels for the advisors depending on the condition...labels?
@exp.member(of_section="instructions_section")
class Instructions(al.Page): 
    
    def on_first_show(self): 
        
        self += al.Text("Welcome!", align="center")
        condition = self.exp.values.get("condition")
        
        if condition == 1:
            self += al.Text (""" 
            We are researchers from Queen\'s University, Belfast. 
            We are investigating judgment and decision making.
            In this study, you\'ll be asked to make judgments and predictions. 
            The study should take __ minutes to complete. 
            Your participation is entirely voluntary. 
            You can end the survey at any point, for any reason, without penalty. 
            Your responses will be anonymised and the data will be held securely. 
            This means there is no way for anybody to possibly link the data to you. 
            This includes us as the researchers, which means that once you complete the study, 
            we will not have the means to withdraw your data after this point.
            
            Why is this important? 
            Since the data we collect from you may be of interest to other researchers, 
            we will publish it on a publicly accessible online data repository 
            such as the Open Science Framework (https://www.osf.io), where it will remain indefinitely. 
            That means, upon publication of the data set, 
            anyone will have access to your anonymised (i.e., non-identifiable) data.   
            """, align="center")
        elif condition == 2:
            self += al.Text("""
            beep boop beep bap boop beep boop beep bap boop beep boop 
            beep bap boop beep boop beep bap boop beep boop beep bap boop
            """, align="center")
        else:
            self += al.Text("""
            ribbit ribbit croak ribbit ribbit ribbit croak ribbit ribbit ribbit 
            croak ribbit ribbit ribbit croak ribbitribbit ribbit croak ribbit 
            ribbit ribbit croak ribbit
            """, align="center")

# TODO: import consent page 
exp.instructions_section += al.Page(title="consent", name="consent_pg")
exp.instructions_section.consent_pg += al.Text("Please select each box if you consent to each statement.")
exp.instructions_section.consent_pg += al.Text("YOU CANNOT PROCEED TO THE SURVEY WITHOUT RESPONDING TO EACH STATEMENT")
exp.instructions_section.consent_pg += al.Hline()
exp.instructions_section.consent_pg += al.VerticalSpace("10px")
exp.instructions_section.consent_pg += al.MultipleChoice("Yes", "No", toplab="I have read and understood the information about the study.", name="m1")

# Section 02: feedback 
# TODO: ask if he means trials like this? 
exp += al.HideOnForwardSection(name="feedback_section")

# for i in range(1, trials+1):
#     exp.feedback_section += al.Page(name=f"trial{i}_page1")
#     exp.feedback_section += al.Page(name=f"trial{i}_page2") 
    
# Page 1: shows cues for this trial only w/out algorithm prediction yet 
# + asks participants to enter initial estimate
@exp.member(of_section="feedback_section")
class Trials_Page1(al.Page):

    def on_first_show(self):
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        no_preds, _ = pred(uploaded_file, target_feature)

        self += al.Html(html=no_preds.to_html(), name="table") # TODO: show only one row 
        self += al.Hline()
        self += al.TextEntry(toplab="Please enter your prediction:", name="prediction", align="center")
        
#  Page 2: shows the cues, the advisor’s estimate, and the true value.
@exp.member(of_section="feedback_section")
class Trials_Page2(al.Page):

    def on_first_show(self):
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        _, preds = pred(uploaded_file, target_feature)
        
        estimate = self.exp.values.get("prediction")

        self += al.Html(html=preds.to_html(), name="preds_table")
        self += al.Hline()
        self += al.Text("Your guess: " + estimate)
        
        
# Section 03: 
# TODO: confidence levels
   

# Section 04: 
# TODO: final section of the experiment - feedback, payment, and debriefing


if __name__ == "__main__":
    exp.run()
    
