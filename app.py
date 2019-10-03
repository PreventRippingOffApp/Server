from flask import Flask, render_template, request, jsonify
import pymongo
import json
import re

# Setting Flask
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.Product')
app.config['JSON_AS_ASCII'] = False

# Setting Database
client = pymongo.MongoClient(app.config['HOST_MONGODB'], app.config['PORT_MONGODB'])
db = client[app.config['NAME_DB']]
collection = db[app.config['NAME_COLLECTION']]
collection.create_index([('location', pymongo.GEO2D)])

def is_num(val):
    try:
        float(val)
    except ValueError:
        return False
    else:
        return True

def check_json(jsondata):
    data = jsondata.decode('utf-8')
    try:
        data = json.loads(data)
    except Exception:
        return None
    return data

def check_location(location, result):
    if not isinstance(location, list):
        result['isSave'] = 2
        result['errorstr'] = 'locationが配列形式ではありません。'
    elif len(location) != 2:
        result['isSave'] = 3
        result['errorstr'] = 'locationの要素数が2ではありません。'
    elif not(is_num(location[0]) and is_num(location[1])):
        result['isSave'] = 4
        result['errorstr'] = 'locationが数値ではありません。'
    elif location[0] < -90 or 90 < location[0]:
        result['isSave'] = 5
        result['errorstr'] = '緯度の値が異常です。'
    elif location[1] < -180 or 180 < location[1]:
        result['isSave'] = 6
        result['errorstr'] = '経度の値が異常です。'
    return



@app.route('/sendLocation', methods=['POST'])
def send_location():
    result = {
        'isSave': 0,
        'errorstr': None,
        'locationData': None
    }
    query = {}
    limitdata = app.config['MAX_DATA']

    # jsonチェック
    data = check_json(request.data)
    if data == None:
        result['isSave'] = 100
        result['errorstr'] = 'jsonが異常です。'
        return jsonify(result)
    
    if 'location' in data:
        check_location(data['location'], result)
        query['location'] = { '$near': data['location']}
    if 'title' in data:
        if isinstance(data['title'], str):
            query['title'] = re.compile(data['title'])
        else:
            result['isSave'] = 11
            result['errorstr'] = 'titleが文字列ではありません。'

    if 'description' in data:
        if isinstance(data['description'], str):
            query['description'] = re.compile(data['description'])
        else:
            result['isSave'] = 12
            result['errorstr'] = 'descriptionが文字列ではありません。'
    if 'limit' in data:
        if isinstance(data['limit'], int): 
            limitdata = data['limit']
        else:
            result['isSave'] = 13
            result['errorstr'] = 'limitが1〜' + str(limit) + 'ではありません。'
    
    if result['isSave'] == 0:
        print(query)
        result['locationData'] = list(collection.find(query, {'_id': False}).limit(limitdata))
        print(result['locationData'])
    
    return jsonify(result)




@app.route('/saveLocation', methods=['POST'])
def save_location():
    result = {
        'isSave': 0,
        'errorstr': None
    }

    # jsonチェック
    data = check_json(request.data)
    if data == None:
        result['isSave'] = 100
        result['errorstr'] = 'jsonが異常です。'
        return jsonify(result)

    if 'location' in data:
        check_location(data['location'], result)
    else:
        result['isSave'] = 1
        result['errorstr'] = 'locationがありません。'

    if result['isSave'] == 0:
        insertData = {
            'location': data['location'],
            'title': None,
            'description': None
        }

        if 'title' in data:
            insertData['title'] = data['title']
        if 'description' in data:
            insertData['description'] = data['description']
        collection.insert_one(insertData)

    return jsonify(result)
        

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def render_index():
    return render_template('index.html', title='Prevent Ripping off Server')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
