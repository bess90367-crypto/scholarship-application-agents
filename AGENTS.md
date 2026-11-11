# 獎學金申請主管入口

本倉庫採「主管 Agent 單一入口」。任何獎學金申請資料整理、核對、範本填寫、成績計算、名單彙整或相關追問，預設都先由 supervisor 接收，再由主管自行調用適切子 Agent；使用者不需要辨認或指定子 Agent。

資料流：Google Drive 當次學期來源 → 完整來源清點 → PDF/影像逐頁可追溯文字 → 結構化資料 → 規則核對 → 私人範本資料夾的正式範本副本 → 品質檢核 → 逐一交付所有範本格式成品。先讀 `rules/core.md`、`rules/drive-workflow.md`、`rules/template-folder.md`、`rules/large-pdf.md`、`rules/template-profile.md` 與 `rules/batch-coverage.md`。

主管路由：一般文件抽取交 `document-extractor`；超大檔與讀取失敗交 `large-file-handler`；工作簿交 `workbook-specialist`；成績及排名交 `score-validator`；交付前交 `quality-reviewer`；可泛化需求交 `knowledge-maintainer`；版本及測試交 `repository-maintainer`。子 Agent 只回報證據、結果與阻礙，由主管裁決衝突。

「請整理 115-1 的獎學金申請資料」及同型自然語句視為完整任務。主管必須抽出唯一民國學期，從已設定的私人 Drive 來源根目錄自動找到該學期資料夾，不要求使用者選 Agent、重貼既有連結、逐檔上傳或重述流程。

每次任務開始都必須重新列出已設定的私人「範本資料夾」。該資料夾當下存在的正式範本是唯一版型來源；不得以 GitHub 摘要、歷史輸出或自行重建的近似版型取代。每一個正式範本都必須產出一個對應整理結果，保留原副檔名及原格式。除填入當次資料、必要的申請人模板頁/工作表複製與名稱替換外，不得改變既有格式、公式邏輯、字型、樣式、欄列尺寸、合併、驗證、命名範圍、列印設定、頁首頁尾、段落、表格樣式或文件結構。不得自行新增摘要頁、來源覆蓋頁、說明頁或其他非範本內容；模板放不下的疑義只在對話中回報。

大型 PDF 不得因檔案大小或連接器限制而直接跳過。必須依 `rules/large-pdf.md` 逐級嘗試索引文字、原始檔下載、同內容分檔/可讀副本、Work/瀏覽器下載後本機切分。任何來源尚未完整讀取時，不得宣稱「完整整理完成」，也不得用舊資料、範例資料或推測補齊。

公開倉庫只放程式、去識別規則與合成測試。真實姓名、學號、成績、原始文件及私人 Drive URL/ID 留在私人專案設定或執行環境，不寫入 public repository。

每次收到新的可泛化要求，先讀 `knowledge/requirements.json`，用穩定 ID 去重並增加合成 regression tests。未確認的資格、採計範圍或換算政策不得自行升格為正式規則。

## 交付連結 QA（不可省略）

所有 XLSX/DOCX 正式成品在回覆使用者前，必須在**本次執行的實際容器**中確認精確路徑存在、檔案大小大於零，並呼叫 `scholarship.delivery_guard.validate_deliverable` 重新開啟驗證；同時執行既有範本格式與資料 QA。只有上述檢查通過且檔案確實位於可下載的 sandbox 路徑時，才能提供 `sandbox:/mnt/data/...` 連結。不可根據檔名、歷史對話、GitHub 檔案或雲端檔案名稱自行猜測 sandbox 路徑。若本次環境找不到先前產物，必須明確告知連結無法恢復，不得重複貼出失效連結；重新取得原始來源與範本後才可重建並交付。
