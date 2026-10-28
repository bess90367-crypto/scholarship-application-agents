# 獎學金申請 Agent 團隊

這是一個以 Codex 主管代理為入口的工作倉庫，將申請文件轉錄、Excel 模板整理、成績計算與品質檢核分工處理。公開內容僅含可重用規則、程式及合成範例；實際申請資料保留本機。

## 使用

在 Codex 開啟本倉庫，直接告訴主管要整理的資料、模板及輸出位置。根目錄 AGENTS.md 會提供路由；`.codex/agents/` 定義七個角色，`.agents/skills/scholarship-supervisor/` 提供可重用技能。這些設定需要支援自訂代理與技能的 Codex 環境，並不自行啟動常駐服務。沒有多代理工具時主管按角色循序工作。

Python 3.11 以上可執行核心計算（不需要第三方套件）：

```sh
python -m scholarship score examples/synthetic-transcript.json
python -m scholarship verify examples/synthetic-transcript.json
python -m unittest discover -s tests -v
```

合成範例預期加權平均為 48，因為零分仍占學分。`verify` 同時檢查排名與列出自填資料/成績單差異。輸入以 `schemas/transcript.schema.json` 為交換規格；CLI 有計算必要欄位的語意檢查，但不宣稱執行完整 JSON Schema 驗證。缺值、不確定證據、重複 ID 或未確認規則會以退出碼 2 阻擋。

文件工具需先安裝選用相依套件，並自行建立忽略的 `private/` 目錄放置真實文件：

```sh
python -m pip install -r requirements.txt
python -m scholarship prepare-pdf private/input.pdf private/extracted.txt
python -m scholarship inspect-template private/template.xlsx > private/template-profile.json
```

`prepare-pdf` 只抽取文字層並產生逐頁標記和 `.pages.json`。文字過少的頁面標為 OCR 候選；這是啟發式判斷，每頁仍需視覺驗證。掃描 PDF 需另用可用 OCR 或圖像轉錄工具，保留文字與頁碼後才能填表。沒有 OCR 引擎時不假稱已完成辨識。

`inspect-template` 輸出一般與陣列公式（含作用範圍）、保留型別的內容、樣式 ID、格式、列高、欄寬、合併、驗證、隱藏列欄及命名範圍。輸出可能含私人資料，不能提交。Excel 實際填寫由 workbook-specialist 依當次模板完成；本 CLI 不宣稱對任意模板自動填寫或重算公式。詳細模板觀察見 `rules/template-profile.md`。

## 分工與資料夾

| 角色 | 責任 |
| --- | --- |
| supervisor | 使用者入口、路由、合併結果及處理衝突 |
| document-extractor | PDF/影像文字與來源定位 |
| workbook-specialist | 模板理解、保留格式及衍生工作簿 |
| score-validator | 加權平均、採計規則與排名範圍 |
| quality-reviewer | 原頁核對、差異與缺漏檢查 |
| knowledge-maintainer | 需求去重、規則與知識維護 |
| repository-maintainer | GitHub、公開檔檢查及回歸測試 |

`rules/` 儲存去識別規則；`schemas/` 定義資料交換；`knowledge/` 記錄需求及學習流程；`scholarship/` 為確定性工具；`tests/` 與 `examples/` 只能用合成資料。擴充角色時增加 TOML 並更新主管路由；新增政策先列適用範圍與確認狀態，再增加測試。

## 維護及排程

每次實際可見的可泛化新要求，依 `knowledge/learning-process.md` 使用穩定 ID 去重、更新規則與合成測試，通過後才提交。主管不保證看得到其他任務、所有 ChatGPT 專案對話或其附件；需要可存取來源或明確匯入需求。

GitHub Actions 在推送、PR、手動啟動與每週一 UTC 01:00（臺北 09:00）執行回歸測試。排程可能因 GitHub 限制延遲或停用，並非常駐監控。它只檢查倉庫，不會讀取私人對話或自動修改資格政策。專案需求的長期檢查由另行建立的 Codex 排程執行；只有實際完成設定後才能宣稱已啟用。

公開前逐檔檢查 staged diff；`.gitignore` 只是第一層措施。不得提交真實申請表、成績、逐字稿、模板檔、憑證或個人識別資訊。規則與數學計算不等於最終獎學金資格判定。
