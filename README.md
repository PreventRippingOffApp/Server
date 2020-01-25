# Server

サーバ側の実装

## 必要なPythonパッケージ

- Flask
- PyMongo

### インストール

```
pip install -r requirements.txt
```

## 機能

- アプリケーション側から送られてきた情報を保存する。

### 位置情報の保存

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

### 位置情報の送信

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


### ファイルアップロード

アプリケーションから送られてきたリクエストを元に、音声ファイルをアップロードする。指定された情報を `/saveAudio` に送信することで、情報を送信する。サーバでは、送られてきた情報を処理し、以下の内容が含まれた情報を返す。

- isSave: 情報が保存されたかを表す。0であれば保存され、0以外であれば保存されていない。
- errorstr: isSaveが0でない場合に、エラーとなった原因を記載する。

#### POST

アプリケーション側で可能な指定は以下の通り。

- param
    - (必須)token:       ユーザの固有トークン。
    - (必須)backupKey:   バックアップキー。
    - (必須)location:    緯度・経度を配列化したもの。形式としては `[緯度, 経度]` である。locationを設定した場合、レスポンスがlocationに近い位置情報を送る。なお、locationの代わりに、latとlngをパラメータとして使用することも可能である。
- file
    - (必須)audioFile:   アップロードする音声ファイル。

### 位置情報→都道府県の検索

アプリケーションから送られてきたリクエストを元に、都道府県を返す。各方法で指定された情報を `/searchPrefecutre` にデータを送信することで、サーバは送られてきた情報を処理し、以下の内容が含まれた情報を返す。

- isSave: 情報が保存されたかを表す。0であれば保存され、0以外であれば保存されていない。
- errorstr: isSaveが0でない場合に、エラーとなった原因を記載する。
- prefectureID: 県ID。位置情報に該当する都道府県がない場合、"0"となる。
- prefecture: 県の名前。位置情報に該当する都道府県がない場合Noneとなる。

#### POST

アプリケーション側で可能な指定は以下の通り。

- (必須)location:    緯度・経度を配列化したもの。形式としては `[緯度, 経度]` である。locationを設定した場合、レスポンスがlocationに近い位置情報を送る。

#### GET

アプリケーション側で指定可能な指定は以下の通り。

- (必須)lat:         緯度
- (必須)lng:         経度

latとlngは、POSTのlocationに該当する。どちらか一方の値のみを渡すとエラーとなる。

### 音声リストの送信

アプリケーションから送られてきたリクエストを元に、音声リストを返す。各方法で指定された情報を `/sendAudioList` にデータを送信することで、サーバは送られてきた情報を処理し、以下の内容が含まれた情報を返す。

- isSave: 情報が保存されたかを表す。0であれば保存され、0以外であれば保存されていない。
- errorstr: isSaveが0でない場合に、エラーとなった原因を記載する。
- audioList: 音声リストの配列。各配列の要素には、以下が含まれている。
	- location: 緯度・経度を配列化したもの。形式としては `[緯度, 経度]` である。
	- prefecture: locationに対応する県の名前。
	- time: 音声ファイルをアップロードした時間。
	- path: 音声ファイルがアップロードされているパス。

#### POST

アプリケーション側で可能な指定は以下の通り。

- (任意)token: ユーザの固有トークン。
- (任意)limit: レスポンスを送る際の、情報の件数を指定できる。デフォルトは100であり、0〜1000まで指定可能。
- (任意)skip:  レスポンスを送る際に読み飛ばす音声ファイルの件数を指定できる。デフォルトは0である。

#### GET

アプリケーション側で指定可能な指定は以下の通り。

- (任意)token: ユーザの固有トークン。
- (任意)limit: レスポンスを送る際の、情報の件数を指定できる。デフォルトは100であり、0〜1000まで指定可能。
- (任意)skip:  レスポンスを送る際に読み飛ばす音声ファイルの件数を指定できる。デフォルトは0である。
