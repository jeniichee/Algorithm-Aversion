import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import alfred3 as al

# TASKS 
# randomly pick condition/go down a list/choosen by one of us? 
# timer/timeout/minimal time participant can stay on page 
# session expriation? 
# show progress bar? 

exp = al.Experiment()

exp += al.ForwardOnlySection(name="main")

# Set up each page 
@exp.setup
def setup(exp):
    exp.progress_bar = al.ProgressBar(show_text=True)

# Main section 
@exp.member
class Main(al.ForwardOnlySection): pass 

# Main page 
@exp.member(of_section="main")
class Main_Page(al.Page):
    title = "Welcome"
    
    def on_exp_access(self):
        self += al.TextEntry(toplab="Please estimate the length of the following river:", name="text1")

if __name__ == "__main__":
    exp.run()

## Main Page
# welcome screen
# instructions 
## 
