# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 20:40:42 2021

@author: user
"""

from urllib import request
req =  request.Request(
    'https://www.lalal.ai/api/upload/',
    open(r'C:\Users\user\Downloads\ABBA_-_Dancing_Queen_Qoret.com.mp3', 'rb'),
    {'Content-Disposition': 'attachment; filename=ABBA_-_Dancing_Queen_Qoret.com.mp3',
     "Authorization": "license 14abcde0"
     }) # this will make the method "POST"
resp = request.urlopen(req)