"""
http://127.0.0.1:5000/start  
"""

import pandas as pd
import alfred3 as al
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
    df_out.rename(columns = {"total_bill_x": "total amount of bill", "size_x": "number of guests"}, inplace = True)
    df_out_preds.rename(columns = {"total_bill_x": "total bill", "size_x": "number of guests"}, inplace = True)
    
    return df_out.head(100), df_out_preds.head(100)

"""Initialize experiment"""
exp = al.Experiment()
trials = 10 
cond = "" 

"""*option A: manually choose*"""
exp += al.HideOnForwardSection(name="setup_section")
exp.setup_section += al.Page(name="setup_page")
exp.setup_section.setup_page += al.SingleChoiceButtons('Algorithm', 'Human', 'Hybrid', name = 'condition')

# """*option B: random+equal sample size for all conditions*"""
# @exp.setup 
# def setup(exp): 
#     randomizer = al.ListRandomizer.balanced("Human", "Algorithm", "Hybrid", exp=exp) 
#     exp.condition = randomizer.get_condition()

# introductions section 
exp += al.ForwardOnlySection(name="info_consent")
exp.info_consent += al.Page(name="introduction")
exp.info_consent.introduction += al.Text(path="introduction.txt")

# TODO: if no, take to debrief and end experiment 
# consent page 
@exp.member(of_section="info_consent")
class consent(al.Page): 
    
    def on_first_show(self):
        self += al.Text("Please select each box if you consent to each statement.")
        self += al.Text("YOU CANNOT PROCEED TO THE SURVEY WITHOUT RESPONDING TO EACH STATEMENT.", align="center")
        self += al.Hline()

        self += al.MultipleChoice("Yes", "No", toplab="I have read and understood the information about the study.", min=1, max=1, name="m1")
        self += al.MultipleChoice("Yes", "No", toplab="""I understand that my participation is entirely voluntary 
                                  and that I am free to withdraw at any time throughout, without giving a reason.""", min=1, max=1, name="m2")
        self += al.MultipleChoice("Yes", "No", toplab="""I understand that my involvement in this research is strictly anonymous 
                                  and my participation is confidential.""", min=1, max=1, name="m3")
        self += al.MultipleChoice("Yes", "No", toplab="I understand that my anonymised data will be published in a public repository.", 
                                  min=1, max=1, name="m4")
        self += al.MultipleChoice("Yes", "No", toplab="I consent to participate in this study.", min=1, max=1, name="m5")
        self += al.MultipleChoice("Yes", "No", toplab="""I understand that the study is being conducted by researchers from 
                                  Queen's University Belfast and that my personal information will be held securely 
                                  and handled in accordance with the provisions of the Data Protection Act 2018.""", min=1, max=1, name="m6")
        self += al.Hline()
        self += al.Text("Please contact the Chief Investigator at the below details if you wish to ask any further questions about the study:")
        self += al.Text("Chief Investigator: Dr Thomas Schultze at t.schultze@qub.ac.uk.")
        
# Age, Gender, Education level & Prolific ID]
exp.info_consent += al.Page(name="AGEP")
exp.info_consent.AGEP += al.NumberEntry(toplab="What is your age?", force_input=True, min=0, max=100, name="participant_age", save_data="True")
exp.info_consent.AGEP += al.SingleChoiceList("Select", "Male", "Female", "Prefer not to say", toplab="What is your gender?", name="sl2")
exp.info_consent.AGEP += al.SingleChoiceList("Select", "Less than Secondary school", "GCSE's", "A Levels", "Undergraduate Degree", 
                                    "Postgraduate Certificate", "Master's Degree", "Professional Degree", "Doctoral Degree", 
                                    toplab="What is the highest level of education you have completed?", name="sl3")

# participant information/debrief page (end experiment if 18 and under)
@exp.member(of_section="info_consent")
class PTINFO(al.Page): 
    
    def on_first_show(self):
        if int(self.exp.values.get("participant_age")) <= 18:
            self += al.Text(path="debrief.txt", align="center")
        else: 
             self += al.Text(path="Participant Information.txt")
            
    def on_first_hide(self):
        if int(self.exp.values.get("participant_age")) <= 18:
            self.exp.abort(
                reason="screening",
                title="Thank You!",
                icon="users",
                msg="Sorry, you must be over 18 to participate in the experiment."
            ) 
            
exp += al.ForwardOnlySection(name="instructions_section")

# task information & incentivization 
@exp.member(of_section="instructions_section")
class Instructions(al.Page): 
    
    def on_first_show(self):
        
        # self += al.Style(".Title{color: black; font-family: Garamond;}")
        self.title = "Welcome!"
        
        ## algorithm 
        # if self.exp.condition == "Algorithm": 
        if self.exp.values.get("condition") == 1: 
            self += al.Text(path="algorithm_condition.txt")
            cond = "Algorithm"
        ## human
        # if self.exp.condition == "Human":
        elif self.exp.values.get("condition") == 2: 
            self += al.Text(path="human_condition.txt")
            cond = "Other person"
        ## hybrid     
        # if self.exp.condition == "Hybrid":
        else: 
            self += al.Text(path="hybrid_condition.txt")
            cond = "Hybrid"
        
        self += al.Hline()
        self += al.VerticalSpace("5mm")
   
        self += al.Text(path="data info.txt") 
        self += al.VerticalSpace("5mm") 
        self += al.Style(code=" th, td {padding: 10px;} table, th, td {border: 1px solid black; border-collapse: collapse;} th {text: black; text-align: center;}")    
        self += al.Html(html="""
                        <table>
                        <tr>
                            <th>Total Amount of Bill</th>
                            <th>Gender</th>
                            <th>Smoker</th>
                            <th>Date of Meal</th>
                            <th>Time of Day</th>
                            <th>Size of Party</th>
                        </tr>
                        <tr>
                            <td>£00.00</td>
                            <td>Male/Female</td>
                            <td>Yes/No</td>
                            <td>DD/MM/YY</td>
                            <td>eg. Dinner</td>
                            <td>Number of diners at the table.</td>
                        </tr>
                        </table>
                        """, position="center")
        self += al.VerticalSpace("5mm")
        self += al.NumberEntry(toplab="How much do you think was paid as a tip for this bill? (Please enter a number between 0-10, to two decimal places e.g. 1.00)", name="mt", align="center")
        self += al.Hline()
        self += al.Text("You will then be told the amount of the actual tip given and will see how accurate your estimate and your advisor's estimates are for each practice task:")
        self += al.Text("""
                                            {}'s estimate: ___
                                            Your estimate: __
                                            Actual tip: ___
                        """.format(cond))

# practice feedback 
exp += al.ForwardOnlySection(name="practice_section")

@exp.member(of_section="practice_section")
class Practice_Feedback(al.Page):
    
    def on_exp_access(self):
        
        # get condition 
        if self.exp.values.get("condition") == 1: 
            cond = "algorithm"
        elif self.exp.values.get("condition") == 2:
            cond = "other person"
        else: 
            cond = "hybrid"
        
        # custom instruction  
        #TODO: .format("cond") only showing "Hybrid" :(
        self += al.Text("Next, you will complete 10 practice estimates. This is just to give you experience before you complete your 10 actual estimates.")
        self += al.Text("You will see the data table with information about each bill. You will make an estimate of the tip paid for the bill.")
        self += al.Text("You will then see the estimate from the {} for the tip paid for each bill.".format(cond))
        self += al.Text("Finally, you will get feedback indicating how close both your estimate and the {}'s estimate were to the actual tip paid.".format(cond))
 
        for n in range(trials):
            self += Trials_Page1(name=f"trial_{n}",  vargs={"i": n})
            self += Trials_Page2(name=f"trial0_{n}",  vargs={"i": n})

# asks participants to enter initial estimate
class Trials_Page1(al.Page):

    def on_first_show(self):
        n = self.vargs.i
        
        self.title = f"Practice Trial #{n+1:02}" # TODO: change font/style
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        no_preds, _ = pred(uploaded_file, target_feature)
        
        self += al.Style(code="th, td {padding: 10px;} table, th, td {border: 1px solid black; border-collapse: collapse;} th, td {text: black; text-align: center;} table{width: 100%;}") 
        self += al.Html(html=no_preds[n:n+1].to_html(), name=f"table_{n+1:02}", position="center") 
        self += al.Hline()
        self += al.NumberEntry(toplab="How much do you think was paid as a tip for this bill? (Please enter a number between 0-10, to two decimal places e.g. 1.00)", min=0, max=10, name=f"prediction_{n+1:02}", align="center")
        
#  shows the cues, the advisor’s estimate, and the true value.
class Trials_Page2(al.Page):

    def on_first_show(self):
        n = self.vargs.i
        
        self.title = f"Practice Trial #{n+1:02}"
        self.subtitle = "Feedback"
        
        if self.exp.values.get("condition") == 1: 
            cond = "Algorithm"
        elif self.exp.values.get("condition") == 2:
            cond = "Other person"
        else: 
            cond = "Hybrid"
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        no_preds, preds = pred(uploaded_file, target_feature)
        
        self += al.Style(code="th, td {padding: 10px;} table, th, td {border: 1px solid black; border-collapse: collapse;} th, td {text: black; text-align: center;} table{width: 100%;}") 
        self += al.Html(html=no_preds[n:n+1].to_html(), position="center")
        self += al.Hline()
        
        #TODO:Hybrid estimates column
        #TODO:Human estimates column
        self += al.Text("{}'s estimate: ".format(cond) + preds[n:n+1]["Algorithm estimate".format(cond)].to_string(index=False))
        self += al.Text("Your estimate: " + str(self.exp.values.get(f"prediction_{n+1:02}")))
        self += al.Text("Actual tip: " + preds[n:n+1]["true value"].to_string(index=False))

# part 2+bonus info 
@exp.member
class Part2(al.Page):
    
    def on_exp_access(self):

        if self.exp.values.get("condition") == 1: 
            cond = "algorithm"
        elif self.exp.values.get("condition") == 2:
            cond = "other person"
        else: 
            cond = "hybrid"
            
        self += al.Text("In part two of the study, you will make your 10 official estimates.", align="center") 
        self += al.Text("In this part of the study, there are bonuses available for more accurate estimates.", align="center") 
        self += al.Text("As before, you will see the data table with information about each bill.", align="center") 
        self += al.Text("You will make an estimate of the tip paid for the bill.", align="center") 
        self += al.Text("You will then see the {}'s estimate for the tip paid for each bill.".format(cond), align="center")
        self += al.Text("You will then have the chance to make a second estimate.", align="center") 
        self += al.Text("You will not receive any feedback in this part of the study.", align="center") 
        
        self += al.Hline()
        self += al.Text("<u>*Incentive/bonus info here*</u>", align="center") 
        self += al.TextArea(toplab="Please type the underlined portion of the text above into the box below to show that you have read the incentive/bonus information.", name="bonus_info")

# 10 different cases for real trials
@exp.member
class Official_Feedback(al.HideOnForwardSection):
        
    def on_exp_access(self):

        for item in range(10, 20):
            self += OPG1(name=f"trial_{item}",  vargs={"i": item})
            self += OPG2(name=f"trial0_{item}",  vargs={"i": item})

class OPG1(al.Page):
    
    def on_first_show(self):
        item = self.vargs.i
        
        self.title = f"Main Task - Trial #{item-9:02} - First Estimate"
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        no_preds, _ = pred(uploaded_file, target_feature)
        
        self += al.Style(code="th, td {padding: 10px;} table, th, td {border: 1px solid black; border-collapse: collapse;} th, td {text: black; text-align: center;} table{width: 100%;}") 
        self += al.Html(html=no_preds[item:item+1].to_html(), name=f"table_{item+1:02}", position="center") 
        self += al.Hline()
        self += al.NumberEntry(toplab="How much do you think was paid as a tip for this bill? (Please enter a number between 0-10, to two decimal places e.g. 1.00)", min=0, max=10, name=f"prediction_{item+1:02}", align="center")
        self += al.VerticalSpace("10px")
        
        #TODO: confidence initial or final estimate? 
        self += al.SingleChoiceButtons("None", "Little", "Some", "A Fair Amount", "A Lot", toplab="How much confidence do you have in your estimate?", name=f"b1_{item+1:02}")

# Algorithm Estimate
class OPG2(al.Page):
    
    def on_first_show(self):
        item = self.vargs.i
        
        self.title = f"Main Task - Trial #{item-9:02} - Second Estimate"
        
        # get condition 
        if self.exp.values.get("condition") == 1: 
            cond = "Algorithm"
        elif self.exp.values.get("condition") == 2:
            cond = "Other person"
        else: 
            cond = "Hybrid"
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "tip"
        no_preds, preds = pred(uploaded_file, target_feature)
        
        self += al.Style(code="th, td {padding: 10px;} table, th, td {border: 1px solid black; border-collapse: collapse;} th, td {text: black; text-align: center;} table{width: 100%;}") 
        self += al.Html(html=no_preds[item:item+1].to_html(), position="center")
        self += al.Hline()
        self += al.Text("{}'s estimate: ".format(cond) + preds[item:item+1]["{} estimate".format(cond)].to_string(index=False))
        self += al.Text("Your First Estimate: " + str(self.exp.values.get(f"prediction_{item+1:02}")))
        self += al.NumberEntry(toplab="You should now make a second estimate in the box below. This can be the same as your first estimate or amended. (Please enter a number between 0-10, to two decimal places e.g. 1.00)", min=0, max=10, name=f"pred_{item+1:02}", align="center")
  
# bonus
exp += al.Page(name="bonus") 
exp.bonus += al.Text("TBD", align="center") 

# debrief 
exp += al.Page(name="debrief")
exp.debrief += al.Text(path="debrief.txt")
        
if __name__ == "__main__":
    exp.run()
    
