"""
http://127.0.0.1:5000/start  
"""

import alfred3 as al
from thesmuggler import smuggle

"""External source files and global parameters"""
model = smuggle("model.py")
content = smuggle("files/content.py")

"""Initialize experiment"""
exp = al.Experiment()
trials = 10 
cond = "" 

"""*option A: manually choose*"""
exp += al.Page(name="setup_page")
exp.setup_page += al.SingleChoiceButtons('Algorithm', 'Human', 'Hybrid', name = 'condition')

# """*option B: random+equal sample size for all conditions*"""
# @exp.setup 
# def setup(exp): 
#     randomizer = al.ListRandomizer.balanced("Human", "Algorithm", "Hybrid", exp=exp) 
#     exp.condition = randomizer.get_condition()

# if exp.condition == "Algorithm": 
# cond = "Algorithm"
# # if exp.condition == "Human":
# cond = "Other person"   
# if self.exp.condition == "Hybrid":
# cond = "Hybrid" 

"""Introduction, participtant information, and consent"""
exp += al.ForwardOnlySection(name="intro_info_consent")
exp.intro_info_consent += al.Page(name="Introduction")
exp.intro_info_consent.Introduction += al.Text(content.introduction)
exp.intro_info_consent += al.Page(title="Participant Information Sheet", name="participtant_info")
exp.intro_info_consent.participtant_info += al.Text(content.participtant_info)
   
@exp.member(of_section="intro_info_consent")    
class consent(al.Page):
    
    def on_first_show(self):
        
        self += al.Text("Please select each box if you consent to each statement.")
        self += al.Text("**YOU CANNOT PROCEED TO THE SURVEY WITHOUT RESPONDING TO EACH STATEMENT.**", align="center")
        self += al.Hline()

        self += al.MultipleChoice("Yes", "No", toplab="I have read and understood the information about the study.", max=1, name="m1", force_input=True, select_hint="Select one")
        self += al.MultipleChoice("Yes", "No", toplab="""I understand that my participation is entirely voluntary 
                                  and that I am free to withdraw at any time throughout, without giving a reason.""", max=1, name="m2", force_input=True, select_hint="Select one")
        self += al.MultipleChoice("Yes", "No", toplab="""I understand that my involvement in this research is strictly anonymous 
                                  and my participation is confidential.""", max=1, name="m3", force_input=True, select_hint="Select one")
        self += al.MultipleChoice("Yes", "No", toplab="I understand that my anonymised data will be published in a public repository.", max=1, name="m4", force_input=True, select_hint="Select one")
        self += al.MultipleChoice("Yes", "No", toplab="I consent to participate in this study.", max=1, name="m5", force_input=True, select_hint="Select one")
        self += al.MultipleChoice("Yes", "No", toplab="""I understand that the study is being conducted by researchers from 
                                  Queen's University Belfast and that my personal information will be held securely 
                                  and handled in accordance with the provisions of the Data Protection Act 2018.""", max=1, name="m6", force_input=True, select_hint="Select one")
        self += al.Hline()
        self += al.Text("*Please contact the Chief Investigator at the below details if you wish to ask any further questions about the study:*")
        self += al.Text("**Chief Investigator**: Dr Thomas Schultze at <u>t.schultze@qub.ac.uk.</u>", align="center")
        
# Age, Gender, Education level & Prolific ID
exp.intro_info_consent += al.Page(name="AGEP")
exp.intro_info_consent.AGEP += al.NumberEntry(toplab="What is your age?", force_input=True, min=0, max=100, name="participant_age", save_data="True", placeholder="Enter your age")
exp.intro_info_consent.AGEP += al.SingleChoiceList("Select", "Male", "Female", "Non-binary", "Prefer not to say", toplab="What is your gender?", name="sl2", force_input=True)
exp.intro_info_consent.AGEP += al.SingleChoiceList("Select", "Less than Secondary school", "GCSE's", "A Levels", "Undergraduate Degree", 
                                    "Postgraduate Certificate", "Master's Degree", "Professional Degree", "Doctoral Degree", 
                                    toplab="What is the highest level of education you have completed?", name="sl3", force_input=True)

# TODO: validate consent+age+fix empty page if valid inputs 
@exp.member(of_section="intro_info_consent")
class Validation(al.Page): 
    
    def on_first_show(self):
        if int(self.exp.values.get("participant_age")) <= 18:
            self.title = "Thank you for taking the time to complete our study!"
            self += al.Text(content.debrief, align="center")
        
    def on_first_hide(self):
        
        if int(self.exp.values.get("participant_age")) <= 18:
            self.exp.abort(
                reason="screening",
                icon="users",
                msg="Sorry, you must be over 18 to participate in the experiment.")

"""Task Information & Incentivization """
exp += al.ForwardOnlySection(name="instructions_section")
@exp.member(of_section="instructions_section")
class Instructions(al.Page): 
    
    title = "Welcome!"
    
    def on_first_show(self):
        
        # get condition 
        if self.exp.values.get("condition") == 1: 
            self += al.Text(content.algorithm_task_info)
            cond = "Algorithm"
        elif self.exp.values.get("condition") == 2: 
            self += al.Text(content.human_task_info)
            cond = "Other person"
        else: 
            self += al.Text(content.hybrid_task_info)
            cond = "Hybrid intelligence"
        
        self += al.Hline()
        self += al.VerticalSpace("5mm")
        self += al.Text(content.data_info) 
        self += al.VerticalSpace("5mm") 
        self += al.Style(code=" th, td {padding: 10px;} table, th, td {border: 1px solid black; border-collapse: collapse;} th {text: black; text-align: center;}")    
        self += al.Html(html="""
                        <table>
                        <tr>
                            <th>Tip</th>
                            <th>Gender of the bill payer</th>
                            <th>Smoker</th>
                            <th>Date of Meal</th>
                            <th>Time of Day</th>
                            <th>Size of Party</th>
                        </tr>
                        <tr>
                            <td>$00.00</td>
                            <td>Male/Female</td>
                            <td>Yes/No</td>
                            <td>DD/MM/YY</td>
                            <td>eg. Dinner</td>
                            <td>Number of diners at the table.</td>
                        </tr>
                        </table>
                        """, position="center")
        self += al.VerticalSpace("5mm")
        self += al.NumberEntry(toplab="How much do you think the total bill was?", name="mt", align="center", force_input=False)
        self += al.Hline()
        self += al.Text("You will then be told the actual total for each bill and will see how accurate your estimate and your advisor's estimates are for each practice task:")
        self += al.Text(f"""
                                            {cond}'s estimate: ___
                                            Your estimate: __
                                            Actual bill: ___
                        """)

# TODO in trial and main task: 
# - remove index in display 
# - confidence -> numbered sacle from 1 to 5 with anchors "not at all confident" and "very confident"? 
# - show estimates w/dollar 
                
"""Experience Phase Instructions"""
@exp.member
class Practice_Feedback(al.ForwardOnlySection):
    
    def on_exp_access(self):
        
        # get condition 
        if self.exp.values.get("condition") == 1: 
            cond = "algorithm"
        elif self.exp.values.get("condition") == 2: 
            cond = "other person"
        else: 
            cond = "hybrid intelligence"
        
        # instructions
        self += al.Page(name="Page")
            
        self.Page += al.Text(content.exp_instructions.format(cond))
 
        for n in range(trials):
            self += Trials_Page1(name=f"trial_{n}",  vargs={"i": n})
            self += Trials_Page2(name=f"trial0_{n}",  vargs={"i": n})

"""Experience Phase Estimates"""
# 1st estimate
class Trials_Page1(al.Page):

    def on_first_show(self):
        n = self.vargs.i
        
        self.title = f"Practice Trial #{n+1:02}" 
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "total_bill"
        no_preds, _ = model.pred(uploaded_file, target_feature)
        
        self += al.Style(code="th, td {padding: 10px;} table, th, td {border: 1px solid black; border-collapse: collapse;} th, td {text: black; text-align: center;} table{width: 100%;}") 
        self += al.Html(html=no_preds[n:n+1].to_html(), name=f"table_{n+1:02}", position="center") 
        self += al.Hline()
        self += al.NumberEntry(toplab="How much do you think the total bill was?", min=0, max=100, name=f"prediction_{n+1:02}", align="center")
        
#  Feedback
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
            cond = "Hybrid intelligence"
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "total_bill"
        no_preds, preds = model.pred(uploaded_file, target_feature)
        
        self += al.Style(code="th, td {padding: 10px;} table, th, td {border: 1px solid black; border-collapse: collapse;} th, td {text: black; text-align: center;} table{width: 100%;}") 
        self += al.Html(html=no_preds[n:n+1].to_html(), position="center")
        self += al.Hline()
        
        #TODO:Hybrid estimates column
        #TODO:Human estimates column
        self += al.Text("Your estimate: $" + (str((self.exp.values.get(f"prediction_{n+1:02}")))))
        self += al.Text("{}'s estimate: ".format(cond) + preds[n:n+1]["{}'s estimate".format(cond)].to_string(index=False))
        self += al.Text("Actual: " + preds[n:n+1]["true value"].to_string(index=False))

"""Part 2 task instructions"""
@exp.member
class Official_Feedback(al.HideOnForwardSection):
        
    def on_exp_access(self):
        
        self += al.Page(name="Part2")
        self.Part2 += al.Text(content.main_task_instructions)
        self.Part2 += al.TextArea(toplab="Please type the underlined portion of the text above into the box below to show that you have read the incentive/bonus information.", name="bonus_info")

        for item in range(10, 20):
            self += OPG1(name=f"trial_{item}",  vargs={"i": item})
            self += OPG2(name=f"trial0_{item}",  vargs={"i": item})

"""Part 2 Estimates"""
# 1st Estimate + confidence
class OPG1(al.Page):
    
    def on_first_show(self):
        item = self.vargs.i
        
        self.title = f"Main Task - Trial #{item-9:02} - First Estimate"
        
        # file/target input 
        uploaded_file = "tips.csv"
        target_feature = "total_bill"
        no_preds, _ = model.pred(uploaded_file, target_feature)
        
        self += al.Style(code="th, td {padding: 10px;} table, th, td {border: 1px solid black; border-collapse: collapse;} th, td {text: black; text-align: center;} table{width: 100%;}") 
        self += al.Html(html=no_preds[item:item+1].to_html(), name=f"table_{item+1:02}", position="center") 
        self += al.Hline()
        self += al.NumberEntry(toplab="How much do you think the total bill was?", min=0, max=100, name=f"prediction_{item+1:02}", align="center")
        self += al.VerticalSpace("10px")

        self += al.SingleChoiceButtons("None", "Little", "Some", "A Fair Amount", "A Lot", toplab="How confident are you in the accuracy of your first estimate?", name=f"b1_{item+1:02}")

# 2nd Estimate + advisor estimate + confidence 
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
        target_feature = "total_bill"
        no_preds, preds = model.pred(uploaded_file, target_feature)
        
        self += al.Style(code="th, td {padding: 10px;} table, th, td {border: 1px solid black; border-collapse: collapse;} th, td {text: black; text-align: center;} table{width: 100%;}") 
        self += al.Html(html=no_preds[item:item+1].to_html(), position="center")
        self += al.Hline()
        self += al.Text("Your First Estimate: $" + (str(self.exp.values.get(f"prediction_{item+1:02}"))))
        self += al.Text("{}'s estimate: ".format(cond) + preds[item:item+1]["{}'s estimate".format(cond)].to_string(index=False))
        self += al.NumberEntry(toplab="You should now make a second estimate in the box below.", min=0, max=10, name=f"pred_{item+1:02}", align="center")
        self += al.SingleChoiceButtons("None", "Little", "Some", "A Fair Amount", "A Lot", toplab="How confident are you in the accuracy of your second estimate?", name=f"b2_{item+1:02}")

# bonus
exp += al.Page(name="bonus") 
exp.bonus += al.Text("TBD", align="center") 

# debrief 
exp += al.Page(name="debrief", title="Thank you for taking the time to complete our study!")
exp.debrief += al.Text(content.debrief)
        
if __name__ == "__main__":
    exp.run()
    
