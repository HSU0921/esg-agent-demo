# AI 輔助 ESG 徵信、PCAF 融資排放與企業議合系統
## AI-Assisted ESG Credit Review, PCAF Financed Emissions & Corporate Engagement System

DSF506A 人工智慧在金融界的應用 | 期末專案 Demo

### 團隊成員

| 學號 | 姓名 | 任職機構 |
|------|------|--------|
| M14B020803 | Chester Wu | Chang Hwa Bank, Treasury / TMU |
| M14B020807 | Stanley Cheng | Nan Shan Life Insurance, Sales Supervisor |
| M14B020809 | Sophia Hsu | Bank of Taiwan, Sustainability Development Section |

### 線上 Demo

https://esg-agent-demo-jvxgcazyvknxpblaybzcvf.streamlit.app

### 本機執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

### 執行測試

```bash
pip install pytest
pytest test_app.py -v
```

### 檔案說明

| 檔案 | 說明 |
|------|------|
| app.py | Streamlit 主程式，含 Multi-Agent 工作流 UI（貸前、貸中、貸後三階段） |
| data.py | 示意資料與工具函式（PCAF 計算、Talk-Walk Gap、議合優先排序、HITL 觸發、ESG 檢核表等） |
| test_app.py | 自動化測試案例，驗證所有工具函式之計算邏輯 |
| requirements.txt | Python 套件相依 |
| packages.txt | 系統套件（中文字型，供 Streamlit Cloud 使用） |

### 重要聲明

Demo 中所有企業資料均為教學與公式驗證用之示意資料，不代表本組對特定真實企業之正式 ESG 評等或投資建議。
