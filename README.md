# Mics 的自動翻譯模組包

## 使用方法

* 下載檔案 https://github.com/mics8128/Factorio-MicsLocale/archive/master.zip
* 將檔案解壓縮放置於 `mods/MicsLocale_版本號` , 版本號部分請取代成 `x.x.x` 製作說明文件時的版本是 `0.0.3`
* 請至 https://cloud.google.com/translate/docs/getting-started 依照文件指示取得憑證
* 將憑證放置於 `mods/MicsLocale_版本號/auto_translate` 取名為 credentials.json
* 安裝 `python` 以及 `pip` 並執行 `pip install --upgrade google-api-python-client`
* 在 `auto_translate` 底下執行 `python main.py` 即可自動翻譯模組內的文件