#%%
import re
import pandas as pd 
from typing import Union, Sequence, Any, List
from unidecode import unidecode

#%%
def pathify(label):
    """
      Convert a label into something that can be used in a URI path segment.
    """
    return re.sub(r'-$', '',
                  re.sub(r'-+', '-',
                         re.sub(r'[^\w/]', '-', unidecode(label).lower())))

co2 = pd.read_csv("la-co2-subsector.csv")



#%%
co2["Notation"]= co2["Notation"].astype(str).apply(pathify) 


#%%
co2.to_csv("la-co2-subsector.csv")
# %%
