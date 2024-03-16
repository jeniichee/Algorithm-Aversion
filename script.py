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
    
    # cues w/true values and predictions 
    df_out_preds = df_out.copy()
    df_out_preds["Algorithm estimate"] = [round(val, 2) for val in y_pred.tolist()]
    df_out_preds["true value"] = round(y_test, 2)
    
    # # TODO: hybrid estimates 
    # df_out_preds["hybrid's estimate"] = []

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

# *option A: choose*
exp += al.HideOnForwardSection(name="setup_section")
exp.setup_section += al.Page(name="setup_page")
exp.setup_section.setup_page += al.SingleChoiceButtons('Algorithm', 'Human', 'Hybrid', name = 'condition')

# *option B: random+equal sample size for all conditions*
# @exp.setup 
# def setup(exp): 
#     randomizer = al.ListRandomizer.balanced("Human", "Algorithm", "Hybrid", exp=exp) 
#     exp.condition = randomizer.get_condition()

# introductions section 
exp += al.ForwardOnlySection(name="info_consent")
exp.info_consent += al.Page(name="introduction")
exp.info_consent.introduction += al.Text(path="introduction.txt")

# # participant information 
# exp.info_consent += al.Page(name="pi")
# exp.info_consent.pi += al.Text(path="Participant Information.txt") 

# # consent 
# @exp.member(of_section="info_consent")
# class Consent(al.Page): 
    
#     def on_first_show(self):
#         self += al.Text("Please select each box if you consent to each statement.")
#         self += al.Text("YOU CANNOT PROCEED TO THE SURVEY WITHOUT RESPONDING TO EACH STATEMENT.", align="center")
#         self += al.Hline()

#         self += al.MultipleChoice("Yes", "No", toplab="I have read and understood the information about the study.", name="m1")
#         self += al.MultipleChoice("Yes", "No", toplab="""I understand that my participation is entirely voluntary 
#                                   and that I am free to withdraw at any time throughout, without giving a reason.""", name="m2")
#         self += al.MultipleChoice("Yes", "No", toplab="""I understand that my involvement in this research is strictly anonymous 
#                                   and my participation is confidential.""", name="m3")
#         self += al.MultipleChoice("Yes", "No", toplab="I understand that my anonymised data will be published in a public repository.", 
#                                   name="m4")
#         self += al.MultipleChoice("Yes", "No", toplab="I consent to participate in this study.", name="m5")
#         self += al.MultipleChoice("Yes", "No", toplab="""I understand that the study is being conducted by researchers from 
#                                   Queen's University Belfast and that my personal information will be held securely 
#                                   and handled in accordance with the provisions of the Data Protection Act 2018.""", name="m6")
#         self += al.Hline()
#         self += al.Text("Please contact the Chief Investigator at the below details if you wish to ask any further questions about the study:")
#         self += al.Text("Chief Investigator: Dr Thomas Schultze at t.schultze@qub.ac.uk.")
#         # self += al.Button(text="Submit", func=Any, followup="forward") 
        
# # Age, Gender, Education level & Prolific ID
# @exp.member(of_section="info_consent")
# class AGEP(al.Page):
    
#     def on_first_show(self): 
#         self += al.SingleChoiceList("Select", "18-24", "25-34", "35-44", "45-54", "55-64", "65 and over", toplab="What is your age?", name="sl1")
#         self += al.SingleChoiceList("Select", "Male", "Female", "Prefer not to say", toplab="What is your gender?", name="sl2")
#         self += al.SingleChoiceList("Select", "Less than Secondary school", "GCSE's", "A Levels", "Undergraduate Degree", 
#                                     "Postgraduate Certificate", "Master's Degree", "Professional Degree", "Doctoral Degree", 
#                                     toplab="What is the highest level of education you have completed?", name="sl3")
#         # self += al.Button(text="Submit", followup="forward")

# Screen 3: Task information & Incentivization
exp += al.ForwardOnlySection(name="instructions_section")

@exp.member(of_section="instructions_section")
class Instructions(al.Page): 
    
    def on_first_show(self):
        self += al.Text("Welcome!", align="center")
        
        # get condition 
        condition = self.exp.values.get("condition")
        
        ## algorithm 
        # if self.exp.condition == "Algorithm": 
        if condition == 1: 
            self += al.Text(path="algorithm_condition.txt")
        ## human
        # if self.exp.condition == "Human":
        elif condition == 2: 
            self += al.Text(path="human_condition.txt")
        ## hybrid     
        # if self.exp.condition == "Hybrid":
        else: 
            self += al.Text(path="hybrid_condition.txt")
            self += al.Hline()
        
        self += al.Text("All the information shown in this study represents real data from a restaurant.")
        self += al.Text("Based on this data, you will be asked to estimate the amount that each table of diners paid as a tip for each bill.")
        self += al.Hline()
        self += al.Text("You will make estimates for 10 bills. You will base your estimates on the data you are given. For each bill, you will be given the following:")      
        self += al.Text("""
                        Total Amount of Bill	 £00.00
                        Gender                   Male/ Female
                        Smoker                   Yes/ No
                        Date of Meal	         DD/MM/YY
                        Time of Day	
                        Size of Party	         Number of diners at table
                        """)

# practice feedback 
@exp.member 
class Practice_Feedback(al.HideOnForwardSection):
    
    def on_exp_access(self):
        # get condition 
        condition = self.exp.values.get("condition")
        cond = "" 

        if condition == 1: 
            cond = "Algorithm"
        elif condition == 2:
            cond = "Restaurant manager"
        else: 
            cond = "Hybrid"
        
        # custom instruction phase 
        #TODO: .format("cond") only showing "Hybrid" :(
        self += al.Page(name = 'Practice_Phase')
        self.Practice_Phase += al.Text("Next, you will complete 10 practice estimates. This is just to give you experience before you complete your 10 actual estimates.")
        self.Practice_Phase += al.Text("You will see the data table with information about each bill. You will make an estimate of the tip paid for the bill.")
        self.Practice_Phase += al.Text("You will then see the {}'s estimate for the tip paid for each bill.".format(cond))
        self.Practice_Phase += al.Text("Finally, you will get feedback indicating how close both your estimate and the {}'s estimate were to the actual tip paid.".format(cond))
 
        for n in range(trials):
            self += Trials_Page1(name=f"trial_{n}",  vargs={"i": n})
            self += Trials_Page2(name=f"trial0_{n}",  vargs={"i": n})


# asks participants to enter initial estimate
class Trials_Page1(al.Page):

    def on_first_show(self):
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        no_preds, _ = pred(uploaded_file, target_feature)
        
        n = self.vargs.i
        
        self += al.Html(html=no_preds[n:n+1].to_html(), name=f"table_{n+1:02}") 
        self += al.Hline()
        self += al.TextEntry(toplab="How much do you think was paid as a tip for this bill? (Please enter a number between 0-10, to two decimal places e.g. 1.00)", name=f"prediction_{n+1:02}", align="center")
        
#  shows the cues, the advisor’s estimate, and the true value.
class Trials_Page2(al.Page):

    def on_first_show(self):
        
        # get condition 
        condition = self.exp.values.get("condition")
        cond = "" 

        if condition == 1: 
            cond = "Algorithm"
        elif condition == 2:
            cond = "Restaurant manager"
        else: 
            cond = "Hybrid"
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        no_preds, preds = pred(uploaded_file, target_feature)
        
        n = self.vargs.i
        estimate = self.exp.values.get(f"prediction_{n+1:02}")
        
        self += al.Html(html=no_preds[n:n+1].to_html())
        self += al.Hline()
        
        #TODO:Hybrid estimates column
        #TODO:Human estimates column
        self += al.Text("{} estimate: ".format(cond) + preds[n:n+1]["Algorithm estimate".format(cond)].to_string(index=False))
        self += al.Text("Your estimate: " + estimate)
        self += al.Text("Actual tip: " + preds[n:n+1]["true value"].to_string(index=False))

# # TODO: accuracy of estimates    
# @exp.member(of_section="Practice_Feedback")
# class Estimates_Accuracy(al.Page):   
#     # TODO: create df of Bill Number, Actual Tip, Accuracy of Your Estimate, 
#     # Accuracy of Algorithm Estimate
#     # TODO: bold/highlight closest estimate 
    
#     def on_first_show(self):
#         self += al.Text("Accuracy") 

# bonus info 
@exp.member
class Bonus(al.HideOnForwardSection):
    
    def on_exp_access(self):
        
        self += al.Page(name="bonus")
        
        self.bonus += al.Text("Next, you will make your 10 official estimates.", align="center")
        self.bonus += al.Hline()
        self.bonus += al.Text("*Incentive/bonus info here*", align="center")
        
        #TODO: underline text
        self.bonus += al.TextEntry(toplab="Please type the underlined portion of the text above into the box below to show that you have read the incentive/ bonus information.", name="bonus_info")

# instructions for actual trial 
@exp.member
class Official_Feedback(al.HideOnForwardSection):
        
    def on_exp_access(self):
        
        self += al.Page(name = 'official_phase')
        
        condition = self.exp.values.get("condition")
        cond = "" 

        if condition == 1: 
            cond = "Algorithm"
        elif condition == 2:
            cond = "Human"
        else: 
            cond = "Hybrid"
        
        ## algorithm 
        # if self.exp.condition == "Algorithm": 
        if condition == 1: 
            self.official_phase += al.Text("As before, you will see the data table with information about each bill.", align="center")
            self.official_phase += al.Text("You will make an estimate of the tip paid for the bill.", align="center")
            self.official_phase += al.Text("You will then see the {}'s estimate for the tip paid for each bill.".format(cond), align="center")
            self.official_phase += al.Text("You will then have the chance to make a second estimate.", align="center")
            
        ## human
        # if self.exp.condition == "Human":
        elif condition == 2: 
            self.official_phase += al.Text(" ")
 
        for item in range(10, 20):
            self += OPG1(name=f"trial_{item}",  vargs={"i": item})
            self += OPG2(name=f"trial0_{item}",  vargs={"i": item})

# 10 different cases for real trials
class OPG1(al.Page):
    
    def on_first_show(self):
        item = self.vargs.i
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        no_preds, _ = pred(uploaded_file, target_feature)

        self += al.Html(html=no_preds[item:item+1].to_html(), name=f"table_{item+1:02}") 
        self += al.Hline()
        self += al.TextEntry(toplab="How much do you think was paid as a tip for this bill? (Please enter a number between 0-10, to two decimal places e.g. 1.00)", name=f"prediction_{item+1:02}", align="center")
        self += al.VerticalSpace("10px")
        
        #TODO: buttons buttoning a little too hard 
        self += al.SubmittingButtons("None", "Little", "Some", "A Fair Amount", "A Lot", toplab="How much confidence do you have in your estimate?", name=f"b1_{item+1:02}")

# Algorithm Estimate
class OPG2(al.Page):
    
    def on_first_show(self):
        
        # get condition 
        condition = self.exp.values.get("condition")
        cond = "" 

        if condition == 1: 
            cond = "Algorithm"
        elif condition == 2:
            cond = "Human"
        else: 
            cond = "Hybrid"
            
        item = self.vargs.i
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        no_preds, preds = pred(uploaded_file, target_feature)
        
        estimate = self.exp.values.get(f"prediction_{item+1:02}")
        
        self += al.Html(html=no_preds[item:item+1].to_html())
        self += al.Hline()
        self += al.Text("{} estimate: ".format(cond) + preds[item:item+1]["{} estimate".format(cond)].to_string(index=False))
        self += al.VerticalSpace("10px")
        
        #TODO: buttons buttoning a little too hard 
        self += al.SubmittingButtons("None", "Little", "Some", "A Fair Amount", "A Lot", toplab="How much confidence do you have in the {}'s estimates?".format(cond), name=f"b2_{item+1:02}")
        
        self += al.Hline()
        self += al.Text("Your First Estimate: " + estimate)
        self += al.TextEntry(toplab="You may alter your original estimate and make a second estimate in the box below. (Please enter a number between 0-10, to two decimal places e.g. 1.00)", name=f"pred_{item+1:02}", align="center")
        
        #TODO: figure out why name not naming for the second estimate, NoneType????
        self += al.Text("Your Second Estimate: " + self.exp.values.get(f"prediction_{item+1:02}"))
        
if __name__ == "__main__":
    exp.run()
    
