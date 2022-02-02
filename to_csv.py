# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 19:40:29 2019

@author: user
"""

import csv

with open('boston.txt') as bo:
    with open('blank.csv', 'w', newline='') as bl:
        
        writer = csv.writer(bl)
        row_count = 0
        
        i = 1
        full = ''
        full_list = []
        for line in bo:
            full += line.replace('\n', '')
            if i:
                i = 0
            else:
                full_list = full.split()
                writer.writerow(full_list)
                full = ''
                full_list.clear()
                i = 1
                row_count += 1