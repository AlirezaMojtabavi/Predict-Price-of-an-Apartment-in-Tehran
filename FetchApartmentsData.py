from random import randint
import requests
import re
from bs4 import BeautifulSoup
import mysql.connector

#Extracted some features with Web scraping and Regex from https://ihome.ir/ 
#for Buying and selling Apartments in Tehran.
#these features include areas, number of bedrooms, antiquity of apartments, neighborhoods and prices. 
#Then, these features stored in Database and finally using machine learning for predict price of another apartments.

garbageCodeList = list()     ## unacceptable codes for url
AdCodeList = list()          ## acceptable codes for url
listOfInput = list()         ## including area, antiquity, number of room(s)
listOfPrice = list()         ## including Price 
listOfNeighborhood = list()  ## including neighborhood of tehran

def GetCode(): ## return Non-repetitive code
    flag = False
    while flag == False :
        flipCoin = randint(0,9)

        if flipCoin%2 == 0 :
            randomCode = randint(1936373,2204714) ## experimentally
        else :
            randomCode = randint(5000096,5195496) ## experimentally
            
        if (randomCode in garbageCodeList) or (randomCode in AdCodeList) :
            flag = False
        else:
            flag = True
    
    return randomCode

url = 'https://ihome.ir/details-page/' ## will be complete (newURL) with Adcode
currect = True
count = 0
n = 500     ## choose your number of Apartment for train (whatever you increase n-> you have strange DataBase but the time duration is increased too)
while count < n :

    checkCode = False
    while (checkCode == False) : ## to check Adcode point to an apartment
        Adcode = GetCode()
        newURL = url + str(Adcode)
        r = requests.get(newURL)
        soup = BeautifulSoup(r.text,'html.parser')
    
        if (soup.find_all('div', attrs = {'class':'nuxt-error'})) : ## this Adcode doesn't point to any apartment
            garbageCodeList.append(Adcode)
            checkCode = False
        elif not(soup.find_all('div', attrs = {'class':'sell-label'})): ## this Adcode is not for sell
            garbageCodeList.append(Adcode)
            checkCode = False
        else :
            propertyDetailTitle = soup.find_all('h1', attrs = {'class':'h4 property-detail_title font-weight-bold'})[0].text
            if re.findall(r'کلنگی', propertyDetailTitle) == ['کلنگی'] :
                garbageCodeList.append(Adcode)
                checkCode = False
            elif re.findall(r'مغازه', propertyDetailTitle) == ['مغازه']:
                garbageCodeList.append(Adcode)
                checkCode = False
            else :                           ## this code just pointing to an Apartment
                checkCode = True
                currect = True
                AdCodeList.append(Adcode)

    print(Adcode)
    ## Neighborhood
    neighborhood = re.findall(r'@type\":\s+\"ListItem\",\s*\"position\":\s+4,\s*\"item\":\s*{\s*\"@id\":\s*.*\s*\"name\":\s*\"(.*)\"',r.text)
    try:
        neighborhood = neighborhood[0]
        listOfNeighborhood.append(neighborhood)
    except:
        continue

    listOfData = soup.find_all('div', attrs = {'class':'property-detail__icons'})
    for items in listOfData :     
        try:
            area = items.find_all('div', attrs = {'class':'property-detail__icons-item'})[2].text       ## Area of a Apartment
            area = re.sub(r'\s*متر مربع\s*','', area).strip()
    
            rooms = items.find_all('div', attrs = {'class':'property-detail__icons-item'})[1].text      ## number of rooms in each Apartment
            if rooms == ('ندارد') or (rooms == '—') :
                rooms = '0'
            elif  re.findall(r'عدد', rooms) == ['عدد'] :
                rooms = re.sub(r'\s*عدد\s*','', rooms).strip() 
            else :
                rooms = re.sub(r'\s*خواب\s*','', rooms).strip()
    
            antiquity = items.find_all('div', attrs = {'class':'property-detail__icons-item'})[0].text  ## Apartment has been used for how many year
            antiquity = re.sub(r'\s+','', antiquity)
            if (antiquity == 'نوساز') or (antiquity == '—') :
                antiquity = '0'
            else:
                antiquity = re.sub(r'\s*سال\s*','', antiquity).strip()
        
            listOfInput.append((int(area), rooms, antiquity))
        except:
            currect == False
            break
##--------------------------------Get price of an apartment -------------------------------------------
        if currect == False:
            continue

        price = soup.findAll('div', attrs = {'class':'sell-value'})[0].text.strip()
        
        if price == 'توافقی' :
            price = '-'

        elif [price] == re.findall(r'(\s*\d*\s*میلیارد\s*تومان\s*)',price):
            price = re.sub(r'(\s*میلیارد\s*تومان\s*)','', price) + '000000000'

        elif [price] == re.findall(r'(\s*\d+\s*میلیارد\s*و\s*\d+\s*میلیون\s*تومان\s*)', price):
            digits = re.findall(r'(\d+) میلیارد  و (\d+) میلیون  تومان', price)
            price = digits[0][0] + digits[0][1] + '000000'

        elif [price] == re.findall(r'(\s*\d+ میلیون  تومان\s*)', price) :
            price = re.sub(r'\s*میلیون  تومان\s*','', price) + '000000'

        elif [price] == re.findall(r'(\s*\d+\s*میلیون\s*و\s*\d+\s*هزار\s*تومان\s*)', price):
            digits = re.findall(r'(\d+) میلیون  و (\d+) هزار  تومان', price)
            price = digits[0][0] + digits[0][1] + '000'

        elif [price] == re.findall(r'(\s*\d+\s*میلیارد\s*و\s*\d+\s*میلیون\s*و\s*\d+\s*هزار\s*تومان\s*)', price):
            digits = re.findall(r'\s*(\d+)\s*میلیارد\s*و\s*(\d+)\s*میلیون\s*و\s*(\d+)\s*هزار\s*تومان\s*', price)
            price = digits[0][0] + digits[0][1] + digits[0][2] + '000'
            
        listOfPrice.append(price)
        count+=1
   
# print(listOfNeighborhood) 
# print(listOfInput)       
#print(listOfPrice)  

# print('lenNeighborhood =') 
print(len(listOfNeighborhood)) 
# print('listOfInput = ') 
print(len(listOfInput))       
# print('listOfPrice = ')
print(len(listOfPrice))

##------------------------------------Storing to Database----------------------------------------------------------


cnx = mysql.connector.connect(user = [type your user] , password = [type your password] ,
                                    host = [type your host]  , database = [type your database name] )
cursor = cnx.cursor()
for i in range (1,n+1):

    cursor.execute('INSERT INTO [type your table] VALUES (\'%i\',\'%s\', \'%i\', \'%s\',\'%s\', \'%s\')' 
                % (i, listOfNeighborhood[i-1], listOfInput[i-1][0], listOfInput[i-1][1], listOfInput[i-1][2],listOfPrice[i-1]))
cnx.commit()

cnx.close()

print('Fetching data is done!')
