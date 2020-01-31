from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import pymongo
import json
import re
import os
import ast
import geopandas as gpd
from geopandas.geoseries import *
from shapely.geometry import Point
from flask_cors import CORS




# Setting Flask
app = Flask(__name__, instance_relative_config=True, static_url_path='/uploads', static_folder='./uploads')
CORS(app)
app.config.from_object('config.Product')
app.config['JSON_AS_ASCII'] = False

# Setting Database
mongodb_setting = {
    'host': os.getenv('HOST_MONGODB', app.config['HOST_MONGODB']),
    'port': os.getenv('PORT_MONGODB', app.config['PORT_MONGODB']),
    'db': os.getenv('NAME_DB', app.config['NAME_DB']),
    'collection': os.getenv('NAME_COLLECTION', app.config['NAME_COLLECTION']),
    'audiocollection': os.getenv('NAME_AUDIO_COLLECTION', app.config['NAME_AUDIO_COLLECTION'])
}
client = pymongo.MongoClient(mongodb_setting['host'], mongodb_setting['port'])
db = client[mongodb_setting['db']]
collection = db[mongodb_setting['collection']]
#collection.create_index([('location', pymongo.GEOSPHERE)])
collection.create_index([('location', pymongo.GEO2D)])
audiocollection = db[mongodb_setting['audiocollection']]
audiocollection.create_index([('location', pymongo.GEO2D)])

# Setting revgeo
shpfile = gpd.read_file(app.config['SHP_PATH'])
geometry = shpfile['geometry']

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

def revgeo(lat, lng):
        point = Point(lng, lat)

        points = geometry.contains(point)
        row = points[points == True].index

        geos = shpfile.loc[row]

        if geos.empty == True:
            return "0", None
        else:
            return geos['JCODE'].to_string(index=False).strip()[0:2], geos['KEN'].to_string(index=False).strip()


@app.route('/sendAudioList', methods=['GET', 'POST'])
def send_audio_list():
    result = {
        'isSave': 0,
        'errorstr': None,
        'audioList': None
    }
    query = {}

    # パラメータ抽出
    if request.method == 'POST':
        data = check_json(request.data)
        if data == None:
            result['isSave'] = 100
            result['errorstr'] = 'jsonが異常です。'
            return jsonify(result)

        token     = data['token'] if 'token' in data else None
        limitdata = data['limit'] if 'limit' in data else app.config['MAX_DATA']
        skip      = data['skip']  if 'skip'  in data else 0
    else:
        token     = request.args.get('token', default=None,                   type=str)
        limitdata = request.args.get('limit', default=app.config['MAX_DATA'], type=int)
        skip      = request.args.get('skip',  default=0,                      type=int)

    # パラメータを元にクエリを作成
    if token != None:
        query['token'] = token
    if limitdata != None:
        if isinstance(limitdata, int):
            if not(1 <= limitdata and limitdata <= 1000):
                result['isSave'] = 13
                result['errorstr'] = 'limitが1〜' + str(app.config['MAX_DATA']) + 'ではありません。'
        else:
            result['isSave'] = 14
            result['errorstr'] = 'limitが整数ではありません。'
    if skip != None:
        if isinstance(skip, int):
            if skip < 0:
                result['isSave'] = 32
                result['errorstr'] = 'skipが0以上ではありません。'
        else:
            result['isSave'] = 31
            result['errorstr'] = 'skipが整数ではありません'


    if result['isSave'] == 0:
        result['audioList'] = list(audiocollection.find(query, {'_id': False}).skip(skip).limit(limitdata))

    return jsonify(result)


@app.route('/searchPrefecture', methods=['GET', 'POST'])
def search_Prefecture():
    result = {
        'isSave': 0,
        'errorstr': None,
        'prefectureID': "0",
        'prefecture': None
    }

    # パラメータ抽出
    if request.method == 'POST':
        data = check_json(request.data)
        if data == None:
            result['isSave'] = 100
            result['errorstr'] = 'jsonが異常です。'
            return jsonify(result)

        location    = data['location']    if 'location'    in data else None
    else:
        lat         = request.args.get('lat', default=None, type=float)
        lng         = request.args.get('lng', default=None, type=float)
        location    = None if (lat == None and lng == None) else [lat, lng]

    # パラメータを元にクエリを作成
    if location != None:
        check_location(location, result)
    else:
        result['isSave'] = 1
        result['errorstr'] = 'locationがありません。'

    if result['isSave'] == 0:
        result['prefectureID'], result['prefecture'] = revgeo(location[0], location[1])

    return jsonify(result)


@app.route('/saveAudio', methods=['POST'])
def save_audio():
    result = {
        'isSave': 0,
        'errorstr': None,
    }

    # token: 固有Token
    if 'audioFile' not in request.files:
        result['isSave']   = 21
        result['errorstr'] = 'audioFileがありません。'
    elif 'token' not in request.form:
        result['isSave']   = 22
        result['errorstr'] = 'tokenがありません。'
    else:
        # 認証関連の処理
        pass

    if 'location' in request.form:
        location = request.form.get('location', default=None, type=list)
    else:
        lat      = request.form.get('lat', default=None, type=float)
        lng      = request.form.get('lng', default=None, type=float)
        location = None if (lat == None and lng == None) else [lat, lng]

    if location is not None:
        check_location(location, result)
    else:
        result['isSave'] = 1
        result['errorstr'] = 'locationがありません。'

    if result['isSave'] == 0:
        audioFile = request.files['audioFile']
        updir     = app.config['UPLOAD_DIR'] + '/' + request.form['token']
        uptime    = datetime.now()
        filename  = uptime.strftime("%Y%m%d%H%M%S_") + secure_filename(audioFile.filename)
        if not os.path.isdir(updir):
            os.makedirs(updir)
        audioFile.save(os.path.join(updir, filename))

        prefectureID, prefecture = revgeo(location[0], location[1])
        query = {
            'location': location[::-1],
            'time': uptime.strftime("%Y/%m/%d %H:%M:%S"),
            'path': os.path.join(updir, filename),
            'prefecture': prefecture,
            'token': request.form['token']
        }
        audiocollection.insert_one(query)
    return jsonify(result)


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
            query['location'] = {
                '$geoWithin': {'$centerSphere': [location, 1 / 6378.137]}
            }
        else:
            query['location'] = {
                '$geoWithin': {'$centerSphere': [location, maxdistance / 6378.137]}
            }
        result['locationData'] = list(collection.find(query, {'_id': False}).limit(limitdata))

    return jsonify(result)

@app.route('/risk', methods=['GET', 'POST'])
def risk():
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
        '$geoWithin': {'$centerSphere': [location, 1 / 6378.137]}
    }
    locationData = list(collection.find(query, {'_id': False}))
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
