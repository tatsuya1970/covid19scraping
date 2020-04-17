## What is this

インターネット上の広島のコロナウィルス情報をスクレイピングし、得たデータを変換して json や csv として出力する Python スクリプトです

## Environments

- Python: 3.8.0

## How to Build

```
$ pip3 install -r requirements.txt
$ python main.py
```

## Specification

- main.py を実行すると、広島県 HP のデータソースにアクセスし、json ファイルと csv ファイルを出力します
  - contacts と inspections_summary のみ、過去データを CSV ファイルから読み込みます
    （スクレイピングデータソースの情報がグルーピングされ、詳細が収集できないため）
  - CSV ファイルの情報とスクレイピングデータソースから取得できる情報が重複する場合、出力ファイルのデータが重複する可能性があります
- 出力されるファイルの構造は、[都公式リポジトリ](https://github.com/tokyo-metropolitan-gov/covid19)に準拠しています

#### スクレイピング実装済データとソースは以下のとおりです

- patients: https://www.pref.hiroshima.lg.jp/soshiki/57/bukan-coronavirus.html
- patients_summary:
  - https://www.pref.hiroshima.lg.jp/soshiki/57/bukan-coronavirus.html
  - https://www.pref.hiroshima.lg.jp/soshiki/50/korona-kensazisseki.html
  - 感染患者増加に伴いデータソースの記載方針等が変わっているため、上記 2 つのデータソースの結果を結合したものが出力されます
- inspections: https://www.pref.hiroshima.lg.jp/soshiki/50/korona-kensazisseki.html
- inspections_summary: https://www.pref.hiroshima.lg.jp/soshiki/50/korona-kensazisseki.html
  - データソースは、過去分データがグルーピングされて正しく収集できないため、過去分のみ csv ファイルから読み込み
- discharges_summary: https://www.pref.hiroshima.lg.jp/soshiki/57/bukan-coronavirus.html
- contacts: https://www.pref.hiroshima.lg.jp/soshiki/50/korona-soudan-kennsai.html
  - データソースは、過去分データがグルーピングされて正しく収集できないため、過去分のみ csv ファイルから読み込み

## Scheduling

GitHub Actions により 15 分に一度、main.py を実行して json や csv 類を gh-pages ブランチに書き出します
