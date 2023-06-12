# %%

import NLTK
import pandas as pd
import pandas_profiling
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import ipywidgets as widgets

# %%

data = pd.read_csv('data/spam.csv', encoding='latin-1')

print(data[:5])

pr = data.profile_report()
data.profile_report()

# %%
pr



# %%
