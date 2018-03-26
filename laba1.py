import urllib.request
import urllib.parse
import html.parser
from html.parser import HTMLParser
import bs4
from bs4 import BeautifulSoup
import csv
import os
from os import walk
import datetime
import pandas as pd
import numpy as np
import re



url = "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/vh_browseByCountry_province.php"
regions = []
DIR_PATH = 'files'

def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False 

def parseAndSave(url):
    response = urllib.request.urlopen(url)
    soup = BeautifulSoup(response.read(), 'html.parser')
    province = soup.find(id="Province")
    now = datetime.datetime.now()
    
    if not os.path.exists('files'):
       os.makedirs('files')    
       
    for ids in province.findAll("option"):
           
        if isint(ids.get('id')):
            regions.append(ids.get('value'))
            province_url = url + "?country=UKR&provinceID="+ids.get('id')+"&year1=2016&year2=2018&type=Mean"
            response = urllib.request.urlopen(province_url)
            handle = open('files/'+ids.get('id') +'_'+ '{:d}'.format(now.year) + '{:d}'.format(now.month) + '{:d}'.format(now.day) + '{:d}'.format(now.hour) + '{:d}'.format(now.minute) +'.csv', "w")
            encoding = response.headers.get_content_charset('utf-8')     
            handle.write(response.read().decode(encoding))
            handle.close()               
    
def readDataCsv(filepath):
    csv_array = []
    file = open(filepath, 'rt');
    reader = csv.reader(file)
    for row in reader:
       csv_array.append(row)
    file.close
    return csv_array


def getHeader(csv_array):
    header = ['year', 'week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'provinceID', 'province']    
    return header 

def getBodyData(csv_array):
    body = []
    
    for base_value in csv_array[1:]:
        row = []
        value = base_value.__getitem__(0).split()
        if(len(value) == 3):
            row.append(value.__getitem__(0))
            row.append(value.__getitem__(1))
            row.append(value.__getitem__(2))            
            row.append(base_value.__getitem__(1))
            row.append(base_value.__getitem__(2))
            row.append(base_value.__getitem__(3))
            row.append(base_value.__getitem__(4))
            # change province index
            value = csv_array.__getitem__(0).__getitem__(0).split()
            provinceId = value.__getitem__(5).strip()[:-1]
            row.append(changeIndex(provinceId))
            row.append(value.__getitem__(6).strip()) 
            
            body.append(row)         
                           
    return body     

def getDataByRegion(path):
    data = [] 

    csv_array = readDataCsv(path)
    data.append(getHeader(csv_array))
    
    for row in getBodyData(csv_array):
        data.append(row)

    return data

def getDataAllRegion(dir_path):
    data = []
    for (dirpath, dirnames, filenames) in walk(dir_path):
        for path in filenames:
            data.append(getDataByRegion(dirpath + '/' + path))
    
    return data
               
def changeIndex(provinceID):
    newIndex = [0, 22, 24, 23, 25, 3, 4, 8, 19, 20, 21, 9, 26, 10, 11, 12, 13, 14, 15, 16, 27, 17, 18, 6, 1, 2, 7, 5]
    return newIndex.__getitem__(int(provinceID))

def getDataByRegionAndProvinceId(provinceId):
    data = []
    for (dirpath, dirnames, filenames) in walk(DIR_PATH):
        for path in filenames:
            if(path.split('_').__getitem__(0) == provinceId):
                data = getDataByRegion(dirpath + '/' + path)
    return data

def getVHIbyRegionAndYear(year, provinceId):
    data = getDataByRegionAndProvinceId(provinceId)
    row = []
    
    for base_value in data[1:]:
        if(base_value.__getitem__(0) == year):
            row.append(base_value[6])

    return row
  
def getVHIbyRegion(provinceId):
    data = getDataByRegionAndProvinceId(provinceId)
    vhi = []
    years = set()
    
    for base_value in data[1:]:
        years.add(base_value.__getitem__(0))

    vhi.append(years);
    
    for year in years:
        row = []
        for base_value in data[1:]:
            if(base_value.__getitem__(0) == year):
                row.append(base_value[6])            
        vhi.append(row)

    return vhi    

#readDataCsv(path)
#df = pd.read_csv(path, index_col=False, header=1)
#print (readDataCsv(path)[:2])
#print(getDataByRegion(path))
#print(getDataAllRegion("files"))
data = getVHIbyRegion('16')
print(data)
#print(min(data))
#print(max(data))