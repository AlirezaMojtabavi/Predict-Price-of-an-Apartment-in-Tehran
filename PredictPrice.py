import numpy 
import mysql.connector
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn import tree

##--------------------------Catch Data from data base--------------------------------

cnx = mysql.connector.connect(user = [type your user] , password = [type your password] ,
                                    host = [type your host]  , database = [type your database name] )

cur = cnx.cursor()
cur.execute("SELECT Neighborhood, Area, rooms, Antiquity FROM specifications")
inputData = cur.fetchall()

cur.execute("SELECT Price FROM specifications")
outputData = cur.fetchall()

if cur:
    cur.close()
if cnx:
    cnx.close()

## TestData

newApartments = [['ولنجک', 120, '2','2'], 
                ['میرداماد', 110, '2','0'],
                ['هروی', 200, '4','2']]

for i in newApartments: ## Add newApartments to input of table
    inputData.append(i)

Neighborhood = list()
Area = list()
rooms = list()
Antiquity = list()

for i in inputData :
    Neighborhood.append(i[0])
    Area.append(i[1])
    rooms.append(i[2])
    Antiquity.append(i[3])

# Encode Neighborhood
values = numpy.array(Neighborhood)
# integer encode
labelEncoder = LabelEncoder()
integer_encoded = labelEncoder.fit_transform(values)
# binary encode
NeighborhoodOHE = OneHotEncoder(sparse=False)
integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
NeighborhoodOHE = NeighborhoodOHE.fit_transform(integer_encoded)
test= Area+rooms
x = numpy.column_stack((NeighborhoodOHE, Area,rooms, Antiquity))
y = outputData
print(x[1])
print(len(x))
print(len(x[1]))
temp = numpy.split(x, [(-1)*len(newApartments)])
x = temp[0]

newApartments_enc = temp[1]
# Start training and testing
clf = tree.DecisionTreeClassifier()
clf = clf.fit(x, y)

# Encode New Apartment
answer = clf.predict(newApartments_enc)
for i in range(len(answer)):
    print("The price of Apartment in %s with %i metters Area, is approaximately %s Tomans." % (newApartments[i][0],newApartments[i][1], answer[i]))
