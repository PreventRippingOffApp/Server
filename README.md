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
	"description: "kakikukeko"
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
