from flask import Flask, render_template
import pymongo

# Setting Flask
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.Test')
app.config['JSON_AS_ASCII'] = False

# Setting Database
client = pymongo.MongoClient(app.config['HOST_MONGODB'], app.config['PORT_MONGODB'])
db = client[app.config['NAME_DB']]
collection = db[app.config['NAME_COLLECTION']]

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def render_index():
    return render_template('index.html', title='Prevent Ripping off Server')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
