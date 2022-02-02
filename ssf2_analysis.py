# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 22:38:44 2019

@author: user
"""

from lxml import html as hl
import pandas as pd
import requests

def text(elt):
    return elt.text_content().replace(u'\xa0', u' ').strip('\n')

def no_dups(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]

rw = requests.get("https://mcleodgaming.fandom.com/wiki/Weight")
root_w = hl.fromstring(rw.content)

for table_w in root_w.xpath('//table'):

    # Get list of table headers
    header_w = [text(th) for th in table_w.xpath('//th')]
    header_w = no_dups(header_w)
    header_w.remove('Class') # Remove class header

    # Get the table info
    weights = [[text(td) for td in tr.xpath('td')]
            for tr in table_w.xpath('//tr')]
    weights = [row for row in weights]
    
    del weights[:2] # Irrelevant data
    # Remove weight class info
    weights = list(map(lambda x: x[:len(x):len(x)-1] if len(x) == 3 else x, weights))
    temp = weights[:]
    weights.clear()
    
    for w in temp:
        # If the current item has no weight,
        # Add the last item's weight as the current item's weight
        if len(w) == 1:
            w.append(temp[temp.index(w) - 1][-1])
            
        weights.append(w)

    weights = pd.DataFrame(weights, columns=header_w).dropna()

rf = requests.get("https://mcleodgaming.fandom.com/wiki/Falling_speed")
root_f = hl.fromstring(rf.content)

for table_f in root_f.xpath('//table'):

    header_f = [text(th) for th in table_f.xpath('//th')]
    header_f = no_dups(header_f)

    f_sp = [[text(td) for td in tr.xpath('td')]
            for tr in table_f.xpath('//tr')]
    f_sp = [row for row in f_sp]
    
    del f_sp[:2]
    
    f_speeds = []
    chars = weights['Character'].unique() # Get all character names
    for grp in f_sp: 
        nm = grp[0]
        # List all character names which appear in the string
        v_nms = [char for char in chars if char in nm]
        
        for v_nm in v_nms:
            
            f_speeds.append([v_nm, grp[1]])
                
    f_speeds = pd.DataFrame(f_speeds, columns=header_f).dropna()

ssf2_info = pd.merge(weights, f_speeds, on='Character', how='outer')
ssf2_info = ssf2_info.set_index('Character')
ssf2_info.columns = ['Weight', 'Fall Speed']
ssf2_info[['Weight', 'Fall Speed']] = ssf2_info[['Weight', 'Fall Speed']].apply(pd.to_numeric)

print(ssf2_info, end="\n\n")

deviation = abs(ssf2_info.dropna() - ssf2_info.dropna().mean())
sum_deviation = deviation.sum(axis=1).sort_values()

print(sum_deviation.head())