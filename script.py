import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import alfred3 as al

exp = al.Experiment()
exp += al.Page(name="page1")

@exp.member
class ExamplePage(al.Page):
    title = ""
