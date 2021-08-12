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

rainfall = pd.read_csv("monthly-rainfall.csv")



#%%
rainfall["period_start"]= rainfall["period_start"].astype(str).apply(pathify) 
rainfall["east scotland"]= rainfall["east scotland"].astype(str).apply(pathify) 
rainfall["north scotland"]= rainfall["north scotland"].astype(str).apply(pathify) 
rainfall["west scotland"]= rainfall["west scotland"].astype(str).apply(pathify) 
rainfall["northern ireland"]= rainfall["northern ireland"].astype(str).apply(pathify) 
rainfall["east midlands"]= rainfall["east midlands"].astype(str).apply(pathify) 
rainfall["east of england"]= rainfall["east of england"].astype(str).apply(pathify) 
rainfall["london"]= rainfall["london"].astype(str).apply(pathify) 
rainfall["north east england"]= rainfall["north east england"].astype(str).apply(pathify) 
rainfall["north west england"]= rainfall["north west england"].astype(str).apply(pathify) 
rainfall["south east england"]= rainfall["south east england"].astype(str).apply(pathify) 
rainfall["south west england"]= rainfall["south west england"].astype(str).apply(pathify) 
rainfall["wales"]= rainfall["wales"].astype(str).apply(pathify) 
rainfall["west midlands"]= rainfall["west midlands"].astype(str).astype(str).apply(pathify) 
rainfall["daycount"]= rainfall["daycount"].astype(str).apply(pathify) 

#%%
rainfall.to_csv("monthly-rainfall.csv")