# SEO Selenium Google AIO 內容爬蟲

## 1. 套件安裝

請先安裝以下 Python 套件：

```bash
pip3 install selenium beautifulsoup4 wordcloud matplotlib
```

> **注意：**
> - 你可能需要安裝 Chrome 瀏覽器與對應版本的 ChromeDriver。
> - 請將 ChromeDriver 加入系統 PATH，或放在本專案資料夾下。
> - 請下載中文字型（如 NotoSansMonoCJKtc-VF.otf）並放在本專案資料夾內。

---

## 2. 關鍵字檔案（keywords.csv）格式

- 請準備一個名為 `keywords.csv` 的檔案，放在本專案資料夾下。
- 檔案需有一個標題為「關鍵字」的欄位，所有關鍵字請依序填在此欄下方。
- 檔案可用 Excel、Google Sheets 或純文字編輯器建立。

**範例：**

| 關鍵字   |
|---------|
| 益生菌   |
| 雞精     |
| 維生素C  |
| ...     |

---

## 3. 如何執行主程式

1. 確認 `seo_selenium_scraper.py`、`keywords.csv`、`NotoSansMonoCJKtc-VF.otf` 均在同一資料夾下。
2. 在終端機（Terminal）切換到該資料夾。
3. 執行：

```bash
python3 seo_selenium_scraper.py
```

---

## 4. 執行流程說明

- 程式會自動讀取 `keywords.csv`，依序搜尋每個關鍵字。
- 每個關鍵字會自動：
  - 開啟 Google 搜尋頁面
  - 輸入關鍵字並搜尋
  - 嘗試點擊「顯示更多」與來源連結圖示
  - 擷取 AIO（AI Overview）內容與來源網站連結
  - 若無 AIO 內容，會標記為 `NO_AIO_FOUND`
- 所有結果會自動儲存與分析。

---

## 5. 產生的檔案說明

- `aio_results.csv`：
  - 主結果表格。每一列為一個關鍵字，包含：
    - 關鍵字
    - AIO內容（Google AI 摘要文字）
    - 來源連結（每個連結一行，便於 Excel/Sheets 檢視）

- `aio_results.json`：
  - 完整結構化結果，包含所有關鍵字、AIO內容、來源連結（適合進階分析）。

- `aio_domain_analysis.csv`：
  - 網域分析表。每一列為一個關鍵字與一個被引用的網域，包含：
    - 關鍵字
    - 網域
    - 次數（該網域在此關鍵字下被引用的次數）

- `aio_wordcloud.png`：
  - 以所有 AIO 內容生成的關鍵詞雲圖，顯示 Google AI 最常出現的詞彙，便於內容優化。

- `full_page.html`：
  - 每次搜尋時暫存的 Google 搜尋結果原始碼，方便除錯與手動檢查。

---

## 6. 常見問題與注意事項

- **字型問題**：
  - 若詞雲圖中文字顯示為方框或亂碼，請確認 `NotoSansMonoCJKtc-VF.otf` 已放在專案資料夾，且程式有正確指定 `font_path`。

- **ChromeDriver 問題**：
  - 請確保 ChromeDriver 版本與 Chrome 瀏覽器相符。
  - Mac 用戶如遇安全性警告，請至「系統偏好設定 > 安全性與隱私」允許執行。

- **Google 反爬蟲**：
  - 若關鍵字數量過多、執行過快，可能會被 Google 暫時封鎖。建議適度調整等待時間。

- **AIO 內容缺失**：
  - 若某關鍵字無 AIO 內容，程式會自動標記為 `NO_AIO_FOUND`，可用於後續分析。

- **Excel 連結顯示**：
  - 來源連結以換行分隔，於 Excel/Sheets 內會自動換行顯示。

---

## 7. 進階應用建議

- 可根據 `aio_results.csv` 進行內容優化、SEO 策略規劃。
- 參考 `aio_domain_analysis.csv` 找出產業權威網站，作為內容參考或外部連結目標。
- 利用 `aio_wordcloud.png` 指導內容團隊聚焦 Google AI 常見詞彙。

---

## Reference

https://webscraping.ai/faq/google-search-scraping/how-do-i-scrape-google-search-results-using-selenium

https://www.scraperapi.com/blog/how-to-scrape-google-ai-results/

https://www.youtube.com/watch?v=8NXbUipUt8U&t=14s

https://www.youtube.com/watch?v=V_LK_Ks1vDA

https://www.youtube.com/watch?v=Dt66BsSlIgM&t=368s
