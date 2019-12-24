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
#collection.create_index([('location', pymongo.GEOSPHERE)])
collection.create_index([('location', pymongo.GEO2D)])

def is_num(val):
    if val == None:
        return False
    if not(isinstance(val, int) or isinstance(val, str) or isinstance(val, float)):
        return False
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


@app.route('/sendLocation', methods=['GET', 'POST'])
def send_location():
    result = {
        'isSave': 0,
        'errorstr': None,
        'locationData': None
    }
    query = {}

    # パラメータ抽出
    if request.method == 'POST':
        data = check_json(request.data)
        if data == None:
            result['isSave'] = 100
            result['errorstr'] = 'jsonが異常です。'
            return jsonify(result)

        location    = data['location']    if 'location'    in data else None
        title       = data['title']       if 'title'       in data else None
        description = data['description'] if 'description' in data else None
        limitdata   = data['limit']       if 'limit'       in data else app.config['MAX_DATA']
        maxdistance = data['maxdistance'] if 'maxdistance' in data else None
    else:
        lat         = request.args.get('lat', default=None, type=float)
        lng         = request.args.get('lng', default=None, type=float)
        title       = request.args.get('title', default=None, type=str)
        description = request.args.get('description', default=None, type=str)
        limitdata   = request.args.get('limit', default=app.config['MAX_DATA'], type=int)
        maxdistance = request.args.get('maxdistance', default=None,type=float)
        location    = None if (lat == None and lng == None) else [lat, lng]

    # パラメータを元にクエリを作成
    if location != None:
        check_location(location, result)
        location = [location[1], location[0]]
    else:
        result['isSave'] = 1
        result['errorstr'] = 'locationがありません。'
    if title != None:
        if isinstance(title, str):
            query['title'] = re.compile(title)
        else:
            result['isSave'] = 11
            result['errorstr'] = 'titleが文字列ではありません。'
    if description != None:
        if isinstance(description, str):
            query['description'] = re.compile(description)
        else:
            result['isSave'] = 12
            result['errorstr'] = 'descriptionが文字列ではありません。'
    if limitdata != None:
        if isinstance(limitdata, int):
            if not(1 <= limitdata and limitdata <= 1000):
                result['isSave'] = 13
                result['errorstr'] = 'limitが1〜' + str(app.config['MAX_DATA']) + 'ではありません。'
        else:
            result['isSave'] = 14
            result['errorstr'] = 'limitが整数ではありません。'
    if maxdistance != None and result['isSave'] == 0:
        if not is_num(maxdistance):
            result['isSave'] = 15
            result['errorstr'] = 'maxdistanceが数値ではありません。'
    if result['isSave'] == 0:
        if maxdistance == None:
            query['location'] = {'$near': location}
        else:
            query['location'] = {
                '$geoWithin': {'$centerSphere': [location, maxdistance / 6378.137]}
            }
        result['locationData'] = list(collection.find(query, {'_id': False}).limit(limitdata))

    return jsonify(result)

@app.route('/risk', methods=['GET', 'POST'])
def send_location():
    result = {
        'risk': 0,
    }
    query = {}

    # パラメータ抽出
    if request.method == 'POST':
        data = check_json(request.data)
        if data == None:
            result['errorstr'] = 'jsonが異常です。'
            return jsonify(result)

        location    = data['location']    if 'location'    in data else None
        description = data['description'] if 'description' in data else None
    else:
        lat         = request.args.get('lat', default=None, type=float)
        lng         = request.args.get('lng', default=None, type=float)
        location    = None if (lat == None and lng == None) else [lat, lng]

        # パラメータを元にクエリを作成
    if location != None:
        check_location(location, result)
        location = [location[1], location[0]]
    else:
        result['errorstr'] = 'locationがありません。'
        return jsonify(result)
    query['location'] = {
        '$near': {'$geometry': {'type':'Point', 'coordinates': location}}
    }
    locationData = list(collection.find(query, {'_id': False})
    result['risk'] = len(locationData)

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
        data['location'] = [data['location'][1], data['location'][0]]
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
