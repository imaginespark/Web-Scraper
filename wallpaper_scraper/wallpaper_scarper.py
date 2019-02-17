# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 13:14:01 2019
To scrap minimalist wallpaper from Simple Desktops
@author: Jerry
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import time
import progressbar

# global constants
BASE_URL = "http://simpledesktops.com"


def image_links_from_page(url_page):
    """
    To return images links of certain page and the address of next page
    """
    
    img_links = []
    soup = BeautifulSoup(url_page, "html5lib")
    div_src = soup.find_all("div", {"class": "desktop"})
    
    for each_div in div_src:
        soup2 = BeautifulSoup(str(each_div), "html5lib")
        img_links.append(soup2.find("img")["src"])

    img_links = extract_img_url(img_links)

    next_link = soup.find("a", {"class": "more"})
    if next_link:
        return img_links, next_link["href"]
    else:
        return img_links, None

def extract_img_url(img_links):
    """
    To return links from current page
    """
    
    tmp = []
    for each_link in img_links:
        if "jpg" in each_link:
            tmp.append(each_link[0:each_link.find("jpg") + 3])
        elif "png" in each_link:
            tmp.append(each_link[0: each_link.find("png") + 3])
    return tmp

def mkdir(path): 
    """
    To create a folder to save all images
    """
    folder = os.path.exists(path)
    
    if not folder:
        os.makedirs(path)
    else:
        print("This folder has been existed.")
		
def get_all_image_links():
    """
    To return all image links from the whole Simple Desktops
    """

    img_dl_links = []
    next_link = "/browse/1/"
    while next_link:
        fh = requests.get("%s%s" % (BASE_URL, next_link), allow_redirects=False)
        
        result = image_links_from_page(fh.text)
        fh.close()
        img_dl_links.append(result[0])
        next_link = result[1]
#        print(next_link)

    tmp = []
    for x in img_dl_links:
        for y in x:
            tmp.append(y)
    img_dl_links = tmp
    return img_dl_links

def download_images(img_dl_links, file_path):
    """
    To download the images and write to the target folder
    """
    x = 1
    total = len(img_dl_links)
    
    pbar = progressbar.ProgressBar().start()
    for img_url in img_dl_links:
        urlretrieve(img_url, file_path + img_url.split('/')[-1])
        
        pbar.update(int((x / (total - 1)) * 100))
        x += 1
        time.sleep(0.01)
    pbar.finish()

if __name__ == "__main__":

    file_path = "./simple-desktops"
    mkdir(file_path)
    img_dl_links = get_all_image_links() 
    
    
    file_path += '/'
    download_images(img_dl_links, file_path)
    
    
    

             