# 音声翻訳アプリ
このアプリは、音声を録音し、Whisper を使って文字起こしを行い、OpenAI互換APIで翻訳する Python GUI アプリです。CustomTkinter を使ったUIで、手軽に音声翻訳を体験できます。

## 主な機能
・音声の録音（5秒間）    
・Whisperによる自動文字起こし  
・ChatGPT互換APIによる翻訳（日本語・英語・ドイツ語対応）    
・翻訳結果の表示   

## インストール方法

### 1.リポジトリをクローン
``` git clone https://github.com/tuba02/Translation.git  cd Translation```   


### 2.仮想環境の作成（任意）
 ``` python -m venv venv     
 venv\Scripts\activate``` 
   

### 3.依存パッケージのインストール
 ``` pip install -r requirements.txt ``` 

## APIキーの設定
OpenRouter APIを使用するため、ルートディレクトリに.envファイルを作成し、以下のように記載してください  
 ``` OPENROUTER_API_KEY=your_openrouter_api_key ``` 

## アプリの実行
 ``` python app.py ``` 

## 必要なライブラリ
以下の内容をrequirements.txtに記載しています  
 ``` numpy  
sounddevice  
openai  
python-dotenv  
customtkinter  
torch  
whisper  
ffmpeg-python
 ```

## ライセンス
このプロジェクトは [MIT License](./LICENSE) のもとで公開されています。


