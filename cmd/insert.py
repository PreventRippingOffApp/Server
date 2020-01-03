import fiona
import requests
import json

file_name = './P30-13.shp'
collection = fiona.open(file_name)

for record in collection:
    title = record['properties']['P30_005']
    description = record['properties']['P30_006']
    location = record['geometry']['coordinates']
    print(title, description, location[0], location[1])
    res = requests.post(
        'http://localhost:5000/saveLocation',
        json.dumps({'title': title, 'description': description, 'location': [location[1], location[0]]}),
        headers={'Content-Type': 'application/json'}
    )
    print(res.json())
