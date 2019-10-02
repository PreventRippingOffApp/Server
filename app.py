from flask import Flask, render_template, request, jsonify
import pymongo
import json

# Setting Flask
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.Test')
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

@app.route('/saveLocation', methods=['POST'])
def save_location():
    result = {
        'isSave': 0,
        'errorstr': None
    }

    # jsonチェック
    data = request.data.decode('utf-8')
    try:
        data = json.loads(data)
    except Exception:
        result['isSave'] = 100
        result['errorstr'] = 'jsonが異常です。'
        return jsonify(result)

    if not 'location' in data:
        result['isSave'] = 1
        result['errorstr'] = 'locationがありません。'
    elif not isinstance(data['location'], list):
        result['isSave'] = 2
        result['errorstr'] = 'locationが配列形式ではありません。'
    elif len(data['location']) != 2:
        result['isSave'] = 3
        result['errorstr'] = 'locationの要素数が2ではありません。'
    elif not(is_num(data['location'][0]) and is_num(data['location'][1])):
        result['isSave'] = 4
        result['errorstr'] = 'locationが数値ではありません。'
    elif data['location'][0] < -90 or 90 < data['location'][0]:
        result['isSave'] = 5
        result['errorstr'] = '緯度の値が異常です。'
    elif data['location'][1] < -180 or 180 < data['location'][1]:
        result['isSave'] = 6
        result['errorstr'] = '経度の値が異常です。'
    
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
