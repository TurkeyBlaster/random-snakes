# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 23:40:50 2020

@author: user
"""

from random import choice

def glitch_text(num):

    diacritics = range(768, 879)
    string = input()
    chars = list(string)

    for i in range(len(chars)):
        
        if chars[i].isalnum():
        
            first = [chr(choice(diacritics)) for _ in range(num)]
            last = [chr(choice(diacritics)) for _ in range(num)]
            
            chars[i] = ''.join(first + [chars[i]] + last)
    
    return chars

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--num", type=int, default=3, help="Number of diacritics")

    args = parser.parse_args()

    chars = glitch_text(args.num)

    with open('zalgo.txt', 'w+', encoding='utf-8') as f:
        f.write(''.join(chars))