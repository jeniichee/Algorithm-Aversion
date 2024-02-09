import alfred3 as al

exp = al.Experiment()
exp += al.ForwardOnlySection(name="main") 

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
        self += al.FileUpload(name="file_upload", label="Choose CSV File")
        self += al.TextEntry(toplab="Please enter the target feature:", name="target",  align="center")

# task 
@exp.member(of_section="main")
class Page2(al.Page):
    title = "Task"

    def on_exp_access(self):
        file_path = self.exp.values["databases/"+"file_upload"]
        target = self.exp.values["target_entry"]
        model.pred(file_path, target)
        
        self += al.TextEntry(toplab="Please enter your prediction:", name="prediction",  align="center")
           

if __name__ == "__main__":
    exp.run()

## for web browsers except chrome: http://127.0.0.1:5000/start