# Server

サーバ側の実装

## 動作環境(who3411)

- macOS High Sierra(ver 10.13.6)
- python 3.7.4
- pip 19.0.3
- MongoDB 4.2.0

### MongoDB (Homebrew)

[Install MongoDB Community Edition on macOS](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/)を参考にした、Homebrewが入っている場合のMongoDBのインストール、および起動・停止方法

#### インストール

```
$ brew tap mongodb/brew
$ brew install mongodb-community
```

#### 起動・停止

```
$ brew services start mongodb-community #起動
$ brew services stop mongodb-community  #停止
```

## 必要なPythonパッケージ

- Flask
- PyMongo

### インストール

```
pip install -r requirements.txt
```

## 機能

- アプリケーション側から送られてきた情報を保存する。

### 情報の保存

アプリケーションから送られてきた情報を保存する。保存可能な情報は以下の通り。

- (必須)location:    緯度・経度を配列化したもの。形式としては `[緯度, 経度]` である。
- (任意)title:       位置情報のタイトル。
- (任意)description: 位置情報に関する説明。

上記情報を `/saveLocation` にjson形式で送信することで、情報を保存する。サーバでは、送られてきた情報を処理し、以下の内容が含まれた情報を返す。

- isSave: 情報が保存されたかを表す。0であれば保存され、0以外であれば保存されていない。
- errorstr: isSaveが0でない場合に、エラーとなった原因を記載する。

#### リクエスト/レスポンス例

##### 例1

リクエスト

```
{
    "location" : [8, 8]
}
```

レスポンス

```
{
    "errorstr": null,
    "isSave": 0
}
```

##### 例2

リクエスト

```
{
    "location" : [1, 1],
    "title": "aiueo",
    "description": "kakikukeko"
}
```

レスポンス

```
{
    "errorstr": null,
    "isSave": 0
}
```

##### 例3

リクエスト

```
{
    "location" : ["a", 1],
}
```

レスポンス

```
{
    "errorstr": "locationが数値ではありません。",
    "isSave": 4
}
```

### 情報の送信

アプリケーションから送られてきたリクエストを元に、これまで保存してきた情報を返す。各方法で指定された情報を `/sendLocation` にjson形式で送信することで、情報を送信する。サーバでは、送られてきた情報を処理し、以下の内容が含まれた情報を返す。

- isSave: 情報が保存されたかを表す。0であれば保存され、0以外であれば保存されていない。
- errorstr: isSaveが0でない場合に、エラーとなった原因を記載する。
- locationData: アプリケーションの指定を元に抽出した位置情報の配列

#### POST

アプリケーション側で可能な指定は以下の通り。

- (必須)location:    緯度・経度を配列化したもの。形式としては `[緯度, 経度]` である。locationを設定した場合、レスポンスがlocationに近い位置情報を送る。
- (任意)title:       位置情報のタイトル。titleを設定した場合、部分一致形式で該当するtitleを検索する。
- (任意)description: 位置情報に関する説明。descriptionを設定した場合、部分一致形式で該当するdescriptionを検索する。
- (任意)limit:       レスポンスを送る際の、情報の件数を指定できる。デフォルトは100であり、0〜1000まで指定可能。
- (任意)maxdistance: 登録されているlocationとリクエストされたlocationの最大の距離(単位:km)。指定した場合、maxdistanceより遠くにあるlocationは送信されない。

#### GET

アプリケーション側で指定可能な指定は以下の通り。

- (必須)lat:         緯度
- (必須)lng:         経度
- (任意)title:       位置情報のタイトル。titleを設定した場合、部分一致形式で該当するtitleを検索する。
- (任意)description: 位置情報に関する説明。descriptionを設定した場合、部分一致形式で該当するdescriptionを検索する。
- (任意)limit:       レスポンスを送る際の、情報の件数を指定できる。デフォルトは100であり、0〜1000まで指定可能。
- (任意)maxdistance: 登録されているlocationとリクエストされたlocationの最大の距離(単位:km)。指定した場合、maxdistanceより遠くにあるlocationは送信されない。

latとlngは、POSTのlocationに該当する。どちらか一方の値のみを渡すとエラーとなる。

#### リクエスト/レスポンス例

以下の情報がサーバに登録されているとする。

```
{"location" : [ 3, 8 ], "title" : "aiueo", "description" : "kakikukeko" }
{"location" : [ 1, 1 ], "title" : "abcdefg", "description" : "hijklmn" }
{"location" : [ 5, 5 ], "title" : null, "description" : null }
```

##### 例1

リクエスト

```
# POST
{}

# GET
curl "http://localhost:5000/sendLocation"
```

レスポンス

```
{
	"errorstr":"locationがありません。",
	"isSave":1,
	"locationData":null
}
```

##### 例2

リクエスト

```
# POST
{
    "location" : [1, 1],
}

# GET
curl "http://localhost:5000/sendLocation?lat=1&lng=1"
```

レスポンス

```
{
    "errorstr": null,
    "isSave": 0,
    "locationData":[
        {"description":null,"location":[5,5],"title":null},
        {"description":"kakikukeko","location":[3,8],"title":"aiueo"},
        {"description":"hijklmn","location":[1,1],"title":"abcdefg"}
}
```

##### 例3

リクエスト

```
# POST
{
    "location" : ["a", 1],
}

# GET
curl "http://localhost:5000/sendLocation?lat=a&lng=1"
```

レスポンス

```
{
    "errorstr": "locationが数値ではありません。",
    "isSave": 4
    "locationData": null
}
```

##### 例4

リクエスト

```
# POST
{
    "location": [1, 1],
    "title": "def"
}

# GET
curl "http://localhost:5000/sendLocation?lat=1&lng=1&title=def"
```

レスポンス

```
{
    "errorstr":null,
    "isSave":0,
    "locationData":[
        {"description":"hijklmn","location":[1,1],"title":"abcdefg"}
    ]
}
```

##### 例5

リクエスト

```
# POST
{
    "location": [5,5],
    "maxdistance": 400.6
}

# GET
curl "http://localhost:5000/sendLocation?lat=5&lng=5&maxdistance=400.6"
```

レスポンス

```
{
    "errorstr":null,
    "isSave":0,
    "locationData":[
        {"description":null,"location":[5,5],"title":null},
        {"description":"kakikukeko","location":[3,8],"title":"aiueo"}
    ]
}
```