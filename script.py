"""
http://127.0.0.1:5000/start  

"""
import pandas as pd
import alfred3 as al
import os

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# prediction model 
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
    df_out_preds['your advisor\'s estimate'] = [round(val, 2) for val in y_pred.tolist()]
    df_out_preds['true value'] = round(y_test, 2)

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

## Section 0: setup 

# *option A: choose*
exp += al.HideOnForwardSection(name="setup_section")
exp.setup_section += al.Page(name="setup_page")
exp.setup_section.setup_page += al.SingleChoiceButtons('Human', 'Algorithm', 'Hybrid', name = 'condition')

# *option B: random+equal sample size for all conditions*
# @exp.setup 
# def setup(exp): 
#     randomizer = al.ListRandomizer.balanced("Human", "Algorithm", "Hybrid", exp=exp) 
#     exp.condition = randomizer.get_condition()

## Section 01: introductions section 
exp += al.ForwardOnlySection(name="instructions_section")
exp.instructions_section += al.Page(name="introduction")
exp.instructions_section.introduction += al.Text("""We are researchers from Queen's University, Belfast. 
                                                 We are investigating judgment and decision making. 
                                                 In this study, you'll be asked to make estimates based on information that you receive. 
                                                 You will then be given advice. 
                                                 After receiving this advice, you may make a final estimate.
                                                 The study should take __ minutes to complete. 
                                                 Your participation is entirely voluntary. 
                                                 You can end the survey at any point, for any reason, without penalty.""")

# participant information 
exp.instructions_section += al.Page(name="pi")
exp.instructions_section.pi += al.Text(path="Participant Information.txt") 

# Screen 1: consent 
@exp.member(of_section="instructions_section")
class Consent(al.Page): 
    
    def on_first_show(self):
        self += al.Text("Please select each box if you consent to each statement.")
        self += al.Text("YOU CANNOT PROCEED TO THE SURVEY WITHOUT RESPONDING TO EACH STATEMENT.", align="center")
        self += al.Hline()
        self += al.VerticalSpace("10px")
        
        # default option is no? 
        self += al.MultipleChoice("Yes", "No", toplab="I have read and understood the information about the study.", name="m1")
        self += al.MultipleChoice("Yes", "No", toplab="""I understand that my participation is entirely voluntary 
                                  and that I am free to withdraw at any time throughout, without giving a reason.""", name="m2")
        self += al.MultipleChoice("Yes", "No", toplab="""I understand that my involvement in this research is strictly anonymous 
                                  and my participation is confidential.""", name="m3")
        self += al.MultipleChoice("Yes", "No", toplab="I understand that my anonymised data will be published in a public repository.", 
                                  name="m4")
        self += al.MultipleChoice("Yes", "No", toplab="I consent to participate in this study.", name="m5")
        self += al.MultipleChoice("Yes", "No", toplab="""I understand that the study is being conducted by researchers from 
                                  Queen's University Belfast and that my personal information will be held securely 
                                  and handled in accordance with the provisions of the Data Protection Act 2018.""", name="m6")
        self += al.Hline()
        self += al.Text("Please contact the Chief Investigator at the below details if you wish to ask any further questions about the study:")
        self += al.Text("Chief Investigator: Dr Thomas Schultze at t.schultze@qub.ac.uk.")
        # self += al.Button(text="Submit", func=Any, followup="forward") 
        
# Screen 2: Age, Gender, Education level & Prolific ID
@exp.member(of_section="instructions_section")
class AGEP(al.Page):
    
    def on_first_show(self): 
        self += al.SingleChoiceList("Select", "18-24", "25-34", "35-44", "45-54", "55-64", "65 and over", toplab="What is your age?", name="sl1")
        self += al.SingleChoiceList("Select", "Male", "Female", "Prefer not to say", toplab="What is your gender?", name="sl2")
        self += al.SingleChoiceList("Select", "Less than Secondary school", "GCSE's", "A Levels", "Undergraduate Degree", 
                                    "Postgraduate Certificate", "Master's Degree", "Professional Degree", "Doctoral Degree", 
                                    toplab="What is the highest level of education you have completed?", name="sl3")
        # self += al.Button(text="Submit", followup="forward")

# Screen 3: Task information & Incentivization
exp += al.Section(name="task_info")
exp.task_info += al.Page(name="info") 
exp.task_info.info += al.Text("In this task, you will be asked to estimate the amount of the tip given for each bill in a restaurant. You will be given information about each bill to help you make each estimate. In addition, you will also be provided with an estimate which has been made by an algorithm.")
exp.task_info.info += al.VerticalSpace("10px")
exp.task_info.info += al.Text("You will have the opportunity to earn additional rewards by making accurate estimates. Please read all the information provided carefully.")
exp.task_info += al.Page(name="info0")
exp.task_info.info0 += al.Text("You will be given information about each specific bill, for example, the number of people who were in the party and the time of day that they ate at. You will use this information to help you estimate how much each table paid as a tip.")
exp.task_info.info += al.VerticalSpace("10px")
exp.task_info.info0 += al.Text("This algorithm is designed to forecast the amount that each set of diners may pay as a tip for their bill. The algorithm is based on hundreds of bills, using the same categories of data that you receive. This is a sophisticated model, put together by thoughtful analysis")
exp.task_info += al.Page(name="inf01")
exp.task_info.inf01 += al.Text("All the information shown in this study represents real data from a restaurant.")
exp.task_info.inf01 += al.Text("Based on this data, you will be asked to estimate the amount that each table of diners paid as a tip for each bill.")
exp.task_info.inf01 += al.Hline()
exp.task_info.inf01 += al.Text("You will make estimates for 10 bills. You will base your estimates on the data you are given. For each bill, you will be given the following:")
exp.task_info.inf01 += al.Text("""
                               Total Amount of Bill	 £00.00
                               Gender                Male/ Female
                               Smoker                Yes/ No
                               Date of Meal	         DD/MM/YY
                               Time of Day	
                               Size of Party	 Number of diners at table
                               """)
        
# # Screen 
# @exp.member(of_section="instructions_section")
# class Instructions(al.Page): 
    
#     def on_first_show(self): 
        
#         self += al.Text("Welcome!", align="center")
#         condition = self.exp.values.get("condition") 
        
#         if condition == 1:
#             self += al.Text (""" 
                             
#             """, align="center")
#         elif condition == 2:
#             self += al.Text("""

#             """, align="center")
#         else:
#             self += al.Text("""
  
#             """, align="center")

# Section 02: feedback 
# TODO: ask if he means trials like this? 

@exp.member 
class Feedback_Section(al.HideOnForwardSection):
    
    def on_exp_access(self):
        
        self += al.Page(title = "Experience Phase", name = 'experience_phase')
        self.experience_phase += al.Text("Next, you will complete 10 practice estimates. This is just to give you experience before you complete your 10 actual estimates. You will see the data table with information about each bill. You will make an estimate of the tip paid for the bill. You will then see the algorithm's estimate for the tip paid for each bill. Finally, you will get feedback indicating how close both your estimate and the algorithm's estimate were to the actual tip paid.")

        for i in range(trials):
            self += Trials_Page1(name=f"trial_{i}",  vargs={"i": i})
            self += Trials_Page2(name=f"trial0_{i}",  vargs={"i": i})

# Page 1: shows cues for this trial only w/out algorithm prediction yet 
# + asks participants to enter initial estimate
class Trials_Page1(al.Page):

    def on_first_show(self):
        i = self.vargs.i
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        no_preds, _ = pred(uploaded_file, target_feature)

        self += al.Html(html=no_preds[:i].to_html(), name=f"table_{i+1:02}") # TODO: show only one row 
        self += al.Hline()
        self += al.TextEntry(toplab="How much do you think was paid as a tip for this bill? (Please enter a number between 0-10, to two decimal places e.g. 1.00)", name=f"prediction_{i+1:02}", align="center")
        
#  Page 2: shows the cues, the advisor’s estimate, and the true value.
class Trials_Page2(al.Page):

    def on_first_show(self):
        i = self.vargs.i
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        _, preds = pred(uploaded_file, target_feature)
        
        estimate = self.exp.values.get("prediction")

        self += al.Html(html=preds[:1].to_html(), name=f"preds_{i+1:02}")
        self += al.Hline()
        self += al.Text("Your estimate: " + estimate)
        
        
# Section 03: 
# TODO: confidence levels
   

# Section 04: 
# TODO: final section of the experiment - feedback, payment, and debriefing


if __name__ == "__main__":
    exp.run()
    
