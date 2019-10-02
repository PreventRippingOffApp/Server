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