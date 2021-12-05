# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 12:18:54 2020

@author: oryan

The aim of this little mini-project is to be able to data scrape all of the UFO sightings from the MoD recently released
project blue-book stuff. As this is downloadable and easy to read, it'll be easier to test and run rather than using a 
data scraper (I'd rather not ddox the MoD).

If this works, I think I'll start trying to do the same with police brutality data or something similar. See if I can
actually start to make a difference.
 
"""
import folium
from folium.plugins import MarkerCluster
import tabula
import os
from os import listdir
from os import path
import pandas as pd
import requests
import time
import numpy as np

class Run():
    def __init__(self):
        pass
        
    def Underlying_Map_Init(self):
        Map = folium.Map(location=[53.9009,-1.5491],zoom_start=5.25)
        return Map

    def Data_Scraper(self,run):
        data_table_dir = 'C:\\Users\\oryan\\Documents\\The UFO Project\\Data\\'
        files = []
        for f in listdir(data_table_dir):
            if f.endswith('.pdf'):
                files.append(path.join(f))
                
        GPS_Coords = []
        Progress = 0
        for i in range(len(files)):
            Year = 1997 + i
            file = 'GPS_Coords_Year_'+str(Year)+'.npy'
            full_path = data_table_dir+files[i]
            table = tabula.read_pdf(full_path,pages='all',multiple_tables=False)
            data = table[0]
            Date = data['Unnamed: 0']
            Time = data['Date']
            Town = data['Unnamed: 2']
            County = data['Time']
            Occupation = data['County']
            Description = data['Town / Village']
            Country = 'United Kingdom'
            
            if os.path.exists(data_table_dir+file):
                GPS_params = np.load(data_table_dir+file)
                for j in range(GPS_params.shape[0]):
                    GPS_Coords.append(GPS_params[j])
            else:
                for i in range(len(Town)):
                    Town_Name = Town[i]
                    if str(Town_Name) == 'nan':
                        continue
                    GPS_param = run.query_address(Town_Name,Country)
                    GPS_Coords.append(GPS_param)
                    Progress += 1
                    check = int(100*(Progress/len(Town)))
                    if check % 10 == 0 :
                        print('Algorithm is ' + str(check) + '% through run.' )
                
                np.save(data_table_dir+file+'.npy',GPS_Coords)
                
        return GPS_Coords,Town,Description

    def query_address(self,Town_Name,Country):
        """
        Point of this function is to search online for the gps coordinates of each town through the file.
        """
        url = "https://nominatim.openstreetmap.org/search"
        query = Town_Name+', '+Country                
        parameters = {'q':'{}'.format(query),'format':'json'}
        
        response = requests.get(url,params=parameters)
        time.sleep(2)
        
        if response.status_code != 200:
            print('Error querying {}'.format(Town_Name))
            result = {}
        else:
            result = response.json()
            if result == []:
                if '/' in Town_Name:
                    Town_Name_slash = Town_Name.find('/')
                    Town_Name_temp = Town_Name[:Town_Name_slash]
                    query = Town_Name_temp+','+Country
                    parameters = {'q':'{}'.format(query),'format':'json'}
                    response = requests.get(url,params=parameters)
                    time.sleep(1)
                    result=response.json()
                    if result == []:
                        Town_Name_temp = Town_Name[Town_Name_slash:]
                        query = Town_Name_temp+','+Country
                        parameters = {'q':'{}'.format(query),'format':'json'}
                        response = requests.get(url,params=parameters)
                        time.sleep(1)
                        result=response.json()
                        if result == []:
                            print('Error: Town Name has not been found. Need to manually look up and input.')
                            lat = float(input('Enter latitude of '+ Town_Name+': '))
                            long = float(input('Enter longitude of '+ Town_Name+': '))
                            GPS_temp = [lat,long]
                            return GPS_temp                    
                else:
                      print('Error: Town Name has not been found. Need to manually look up and input.')
                      lat = float(input('Enter latitude of '+ Town_Name+': '))
                      long = float(input('Enter longitude of '+ Town_Name+': '))
                      GPS_temp = [lat,long]
                      return GPS_temp
               
        dictionary = result[0]
        lat = float(dictionary['lat'])
        long = float(dictionary['lon'])
        GPS_temp = [lat,long]
#            print(GPS_temp)
            
        return GPS_temp
            
            
            

def main():
  """
  This is the master part of the script which will call all the functions required to build the map.
  """
  directory = 'C:\\Users\\oryan\\Documents\\The UFO Project\\'
  run = Run()
  m = run.Underlying_Map_Init()
  marker_positions,Towns,Incident_Descriptions = run.Data_Scraper(run)
  description_counter = 0
  for i in range(len(marker_positions)):
      marker = marker_positions[i]
      if str(Towns[i]) == 'nan':
          description_counter += 1
      description = Incident_Descriptions[int(description_counter)]
      folium.Marker([marker[0],marker[1]],popup=description).add_to(m)
      description_counter += 1

      
  m.save(directory+'test_map.html')
  
  print('Algorithm Complete.')

if __name__ == "__main__": main()