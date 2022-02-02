# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 01:05:36 2020

@author: user
"""

# Adopted from: https://github.com/atif93/google_image_downloader/blob/master/image_download_python3.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from urllib.request import urlopen, Request
import argparse
import re

parser = argparse.ArgumentParser()

# Add long and short arguments for image search
parser.add_argument(
    
    "--search-text",
    "-s",
    type = str,
    required = True,
    help = "The search query/subject"
)
# Add long and short arguments for number of images
parser.add_argument(
    
    "--num-images",
    "-n",
    type = int,
    default = 400,
    help = """Number images to be downloaded\n
            If fewer pictures are found than specified,\n
            all available pictures will be downloaded\n
            Default: 400"""
)
# Add long and short arguments for destination directory
parser.add_argument(
    
    "--image-dir",
    "-d",
    type = str,
    default = 'images',
    help = """Intermediate directory in which the images will be downloaded\n
            (a folder of image searches will be downloaded in this directory)\n
            If the directory doesn't exist, it will be created\n
            in the current working directory (unless it is a complete path)
            Default: '/images'"""
)
args = parser.parse_args()

os.environ["PATH"] += os.pathsep + os.getcwd()

image_dir = args.image_dir
search_text = args.search_text.replace(" ", "_")

# Destination directory
if image_dir[:2] == 'C:':
    dest_dir = os.path.join(image_dir, search_text) # When path is complete
else:
    dest_dir = os.path.join(os.getcwd(), image_dir, search_text) # When path is relative

num_images = args.num_images
num_scrolls = round(num_images / 400) + 1

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

url = f"https://www.google.co.in/search?q={search_text.replace('_', '+')}&source=lnms&tbm=isch"
driver = webdriver.Chrome("C://Users/user/Documents/chromedriver_win32/chromedriver.exe") # Path to ChromeDriver
driver.get(url)

headers = {
    
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}

img_count = 0
download_count = 0

class ScrollHeightChange:
    
    def __init__(self, current_height):
        
        self.current_height = current_height
    
    def __call__(self, driver):
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height > self.current_height:
            return new_height
        else:
            return False

for _ in range(num_scrolls):
    
    # Scroll as far down as possible
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        
        try:
            
            last_height = WebDriverWait(driver, 3).until(
            
                ScrollHeightChange(last_height)
            )
        
        except TimeoutException:
            
            break
        
    
    # Try to click 'show more results' button
    try:
        
        more_imgs_button = WebDriverWait(driver, 2).until(
            
            EC.visibility_of_element_located((By.XPATH, "//*[contains(concat( ' ', @class, ' ' ), concat( ' ', 'mye4qd', ' ' ))]"))
        )
        more_imgs_button.click()
    
    except TimeoutException:
        
        print("Max images reached")
        break
    
imgs = driver.find_elements_by_xpath("//*[contains(concat( ' ', @class, ' ' ), concat( ' ', 'Q4LuWd', ' ' ))]")
print(f"Number of images loaded: {len(imgs)}")

print(f"Attempting download at {dest_dir}")

for img in imgs:
    
    img_count += 1
    
    print(f"Downloading image #{img_count}", end=': ')
    
    try:
        
        img_url = img.get_attribute('src')
        
        # If src attribute didn't send,
        # We try to get it from the html
        if img_url is None:
            
            html = img.get_attribute('outerHTML')
            img_url = re.search('data-src=[^\s]+', html).group().replace('data-src=', '').replace('"', '')
        
        print(f"{img_url[:51]}...")
        
        req = Request(img_url, headers=headers)
        raw_im = urlopen(req).read()
        
        with open(os.path.join(dest_dir, f"{download_count}.png"), "wb") as im:
            im.write(raw_im)
            
        download_count += 1
        
    except Exception as e:
        
        print(f"\nUnable to download image: {e}")
        
    finally:
        
        print() # Empty line for separation between images
        
        if download_count >= num_images:

            break
        
print(f"Final downloaded amount: {download_count}/{len(imgs)}")

print("Closing driver")
try:
    
    driver.close()
    
except Exception as e:
    
    print(f"Could not close driver: {e}\nManual exit required")