from __future__ import annotations

from datetime import date, timedelta


PAIN_POINTS = {
    "1.3.1": "貸前徵信資料蒐集分散且重複",
    "1.3.1_step2": "20 項 ESG 指標每半年須人工重新檢視",
    "1.3.2": "貸中議合準備曠日廢時、難以規模化",
    "1.3.3": "貸後追蹤高度重複且揭露時程壓力大",
    "1.3.4": "中小企業 ESG/碳排資料缺口",
}

HIGH_CLIMATE_RISK_INDUSTRIES = ["鋼鐵", "水泥", "電力", "石化", "石油", "煤炭", "航運", "航空", "造紙", "紡織化纖"]

ESG_INDICATORS = {
    "E": ["碳排盤查", "減碳目標", "能源管理", "水資源管理", "污染裁罰", "CBAM因應", "氣候風險揭露", "廢棄物管理"],
    "S": ["勞動法規", "職安事件", "供應鏈管理", "人權政策", "社區溝通", "消費者/客戶權益"],
    "G": ["董事會治理", "資訊揭露", "AML/CFT", "重大訴訟", "誠信經營", "外部評鑑/認證"],
}
NEGATIVE_NEWS_SOURCE = "Google News（示意）"


def is_sme_data_gap_client(client):
    return client.get("ticker") == "N/A" or client.get("name") == "某精密中小企業(示意)"


def _package(name, industry, exposure, emissions, target, gap, tone="balanced"):
    method = "面對面會議 + 淨零轉型診斷" if gap >= 0.55 else "問卷追蹤 + 定期轉型進度會議"
    if tone == "positive":
        method = "年度追蹤會議 + SLL成效交流"
    return {
        "current_summary": f"{name}為{industry}業示意客戶，融資暴險{exposure}億元，年排放量約{emissions:,}噸CO2e。系統彙整裁罰、負面新聞、目標揭露、CBAM與產業路徑資料，作為議合準備素材。",
        "gap_analysis": f"Talk-Walk Gap 為 {gap:.2f}。{'已有明確目標，實績與揭露大致一致。' if tone == 'positive' else '揭露承諾與實際轉型進度仍有落差，需進一步確認資本支出、範疇三盤查與短中期目標。'}",
        "engagement_method": method,
        "dialogue_questions": [
            f"1. 貴公司是否願意於12個月內{'更新' if target else '設定'}中期減碳目標並提出董事會核准時程？",
            "2. 範疇一/二/三盤查邊界與查證狀態為何？是否需要示意銀行企業淨零轉型診斷協助？",
            f"3. {industry}主要高碳製程的低碳替代技術、資本支出與投產時程為何？",
            "4. 若涉及歐盟客戶或供應鏈，CBAM/客戶減碳要求之因應策略為何？",
            "5. 是否考慮以永續績效指標連結貸款（SLL）連動減碳KPI以取得利率優惠？",
        ],
        "tracking_kpis": [
            {"milestone": "T+6M", "target": "提交減碳路徑、資料缺口補件與董事會追蹤紀錄"},
            {"milestone": "T+12M", "target": "完成範疇三盤查或中期目標外部審查"},
            {"milestone": "T+1Y", "target": f"實際排放對照{industry}產業路徑，確認轉型缺口是否縮小"},
        ],
        "sll_suggestion": "建議以範疇一+二年排放量減幅、再生能源使用率或單位產品碳強度作為 SLL KPI。達標可享利率優惠0.03%-0.05%。",
    }


DEMO_PORTFOLIO = [
    {
        "name": "台塑化(示意)", "ticker": "6505", "industry": "石化",
        "exposure_e_twd": 120, "company_value_e_twd": 8000, "annual_emissions_tco2e": 25_000_000, "pcaf_dq": 3,
        "high_climate_risk": True, "has_target": False, "is_policy": False, "talk_walk_gap": 0.72, "cbam_exposed": True,
        "negative_news": [
            {"title": "台塑化(示意) 六輕類型廠區排放超標情境", "date": "2024-08-15", "source": NEGATIVE_NEWS_SOURCE},
            {"title": "台塑化(示意) 石化廠廢水處理設備異常情境", "date": "2024-03-22", "source": NEGATIVE_NEWS_SOURCE},
            {"title": "ESG 評鑑情境：石化業碳排居高，轉型壓力大", "date": "2023-11-08", "source": NEGATIVE_NEWS_SOURCE},
        ],
        "env_penalties": [
            {"time": "2024-08-12", "fact": "固定污染源排放超過排放標準", "law": "空氣污染防制法第20條", "fine": "1,200,000"},
            {"time": "2023-11-03", "fact": "未依許可證內容操作", "law": "水污染防治法第7條", "fine": "600,000"},
        ],
        "esg_20_scores": {"E": [1, 1, 0, 1, 0, 1, 1, 0], "S": [1, 1, 0, 1, 1, 0], "G": [1, 1, 1, 0, 1, 1]},
        "credit_bonus": {"公司治理": 2, "永續環境": 1, "社會公益": 2},
        "talk_features": {"淨零承諾強度": 0.85, "減碳目標數值": 0.70, "ESG關鍵字密度": 0.90, "永續報告書完整度": 0.80},
        "walk_features": {"外部ESG評等": 0.35, "過去3年碳排趨勢": 0.20, "爭議事件數": 0.15, "行業相對排名": 0.30},
        "shap_top5": [
            {"feature": "宣稱2030淨零但近3年排放僅減2%", "value": 0.31, "direction": "up"},
            {"feature": "近2年環保裁罰2件", "value": 0.18, "direction": "up"},
            {"feature": "CBAM暴險（歐盟客戶佔比高）", "value": 0.12, "direction": "up"},
            {"feature": "已發布永續報告書", "value": -0.08, "direction": "down"},
            {"feature": "有設定部分減碳承諾", "value": -0.05, "direction": "down"},
        ],
        "engagement_package": {
            "current_summary": "台塑化(示意) 為本 demo 建立之石化業高轉型風險情境，融資暴險 120 億元，年排放量約 2,500 萬噸 CO2e，屬高氣候轉型風險產業。近 2 年有 2 件環境裁罰情境與 3 則負面新聞情境。銷貨前五大客戶含歐盟客戶，屬 CBAM 風險暴險情境。目前尚未設定中期溫度目標或通過 SBTi 審核。",
            "gap_analysis": "石化業SBT建議年減碳率為3.5%，但該客戶近3年實際碳排年減幅僅約0.7%，與產業路徑存在顯著落差。Talk-Walk Gap 0.72 顯示揭露承諾與實際表現之間有高度落差。",
            "engagement_method": "面對面會議 + 淨零轉型診斷",
            "dialogue_questions": [
                "1. 貴公司是否願意於12個月內設定中期溫度目標/通過SBTi審核？",
                "2. 範疇一/二/三盤查現況？是否需要示意銀行「企業淨零轉型診斷」協助？",
                "3. 六輕廠區高碳製程之低碳轉型計畫與資本支出時程為何？",
                "4. 銷貨前五大歐盟客戶之CBAM因應策略為何？",
                "5. 是否考慮以永續績效指標連結貸款（SLL）連動減碳KPI以取得利率優惠？",
            ],
            "tracking_kpis": [
                {"milestone": "T+6M", "target": "提交減碳路徑與轉型計畫"},
                {"milestone": "T+12M", "target": "完成範疇三盤查 / 提交SBTi目標審核申請"},
                {"milestone": "T+1Y", "target": "實際碳排較基準年下降，對照石化業3.5%/年路徑"},
            ],
            "sll_suggestion": "建議以「範疇一+二年排放量較基準年減幅」為永續績效指標，達成每年減3.5%以上可享利率優惠0.05%。",
        },
    },
    {
        "name": "中鋼(示意)", "ticker": "2002", "industry": "鋼鐵",
        "exposure_e_twd": 95, "company_value_e_twd": 6200, "annual_emissions_tco2e": 19_500_000, "pcaf_dq": 3,
        "high_climate_risk": True, "has_target": True, "is_policy": False, "talk_walk_gap": 0.58, "cbam_exposed": True,
        "negative_news": [
            {"title": "鋼鐵業示意客戶 A 高爐減碳進度受關注情境", "date": "2024-06-18", "source": NEGATIVE_NEWS_SOURCE},
            {"title": "鋼鐵業 CBAM 申報壓力升高情境", "date": "2023-12-10", "source": NEGATIVE_NEWS_SOURCE},
        ],
        "env_penalties": [{"time": "2023-09-21", "fact": "粒狀污染物排放紀錄異常", "law": "空氣污染防制法第23條", "fine": "350,000"}],
        "esg_20_scores": {"E": [1, 1, 1, 1, 0, 1, 1, 1], "S": [1, 1, 1, 1, 1, 0], "G": [1, 1, 1, 1, 1, 1]},
        "credit_bonus": {"公司治理": 3, "永續環境": 2, "社會公益": 2},
        "talk_features": {"淨零承諾強度": 0.80, "減碳目標數值": 0.76, "ESG關鍵字密度": 0.72, "永續報告書完整度": 0.86},
        "walk_features": {"外部ESG評等": 0.54, "過去3年碳排趨勢": 0.33, "爭議事件數": 0.46, "行業相對排名": 0.49},
        "shap_top5": [
            {"feature": "高爐製程減碳資本支出尚未完全落地", "value": 0.20, "direction": "up"},
            {"feature": "CBAM暴險", "value": 0.14, "direction": "up"},
            {"feature": "近2年環保裁罰1件", "value": 0.08, "direction": "up"},
            {"feature": "已揭露2050淨零路徑", "value": -0.10, "direction": "down"},
            {"feature": "外部ESG評等中上", "value": -0.06, "direction": "down"},
        ],
        "engagement_package": _package("中鋼(示意)", "鋼鐵", 95, 19_500_000, True, 0.58),
    },
    {
        "name": "亞泥(示意)", "ticker": "1102", "industry": "水泥",
        "exposure_e_twd": 68, "company_value_e_twd": 3600, "annual_emissions_tco2e": 8_800_000, "pcaf_dq": 4,
        "high_climate_risk": True, "has_target": False, "is_policy": False, "talk_walk_gap": 0.65, "cbam_exposed": True,
        "negative_news": [
            {"title": "亞泥(示意) 礦區開發與生態復育爭議情境", "date": "2024-05-03", "source": NEGATIVE_NEWS_SOURCE},
            {"title": "水泥業熟料替代率不足，轉型壓力升高情境", "date": "2023-10-29", "source": NEGATIVE_NEWS_SOURCE},
        ],
        "env_penalties": [{"time": "2024-01-16", "fact": "事業廢棄物貯存標示不完整", "law": "廢棄物清理法第36條", "fine": "180,000"}],
        "esg_20_scores": {"E": [1, 0, 0, 1, 0, 0, 1, 1], "S": [1, 1, 0, 1, 1, 0], "G": [1, 1, 1, 0, 1, 0]},
        "credit_bonus": {"公司治理": 2, "永續環境": 1, "社會公益": 1},
        "talk_features": {"淨零承諾強度": 0.70, "減碳目標數值": 0.45, "ESG關鍵字密度": 0.78, "永續報告書完整度": 0.70},
        "walk_features": {"外部ESG評等": 0.42, "過去3年碳排趨勢": 0.25, "爭議事件數": 0.28, "行業相對排名": 0.36},
        "shap_top5": [
            {"feature": "未設定中期SBT目標", "value": 0.22, "direction": "up"},
            {"feature": "礦區爭議新聞2則", "value": 0.13, "direction": "up"},
            {"feature": "熟料替代率資訊不足", "value": 0.10, "direction": "up"},
            {"feature": "永續報告書揭露完整", "value": -0.07, "direction": "down"},
            {"feature": "水資源管理有揭露", "value": -0.04, "direction": "down"},
        ],
        "engagement_package": _package("亞泥(示意)", "水泥", 68, 8_800_000, False, 0.65),
    },
    {
        "name": "台泥(示意)", "ticker": "1101", "industry": "水泥",
        "exposure_e_twd": 72, "company_value_e_twd": 4200, "annual_emissions_tco2e": 7_200_000, "pcaf_dq": 2,
        "high_climate_risk": True, "has_target": True, "is_policy": False, "talk_walk_gap": 0.22, "cbam_exposed": False,
        "negative_news": [{"title": "水泥業示意客戶 B 低碳水泥與儲能布局受關注情境", "date": "2024-04-12", "source": NEGATIVE_NEWS_SOURCE}],
        "env_penalties": [],
        "esg_20_scores": {"E": [1, 1, 1, 1, 1, 0, 1, 1], "S": [1, 1, 1, 1, 1, 1], "G": [1, 1, 1, 1, 1, 1]},
        "credit_bonus": {"公司治理": 3, "永續環境": 3, "社會公益": 3},
        "talk_features": {"淨零承諾強度": 0.88, "減碳目標數值": 0.84, "ESG關鍵字密度": 0.76, "永續報告書完整度": 0.90},
        "walk_features": {"外部ESG評等": 0.82, "過去3年碳排趨勢": 0.78, "爭議事件數": 0.86, "行業相對排名": 0.80},
        "shap_top5": [
            {"feature": "實際減碳接近產業路徑", "value": -0.20, "direction": "down"},
            {"feature": "外部ESG評等佳", "value": -0.12, "direction": "down"},
            {"feature": "近2年無環保裁罰", "value": -0.08, "direction": "down"},
            {"feature": "仍屬高氣候轉型風險產業", "value": 0.07, "direction": "up"},
            {"feature": "熟料替代技術需持續追蹤", "value": 0.05, "direction": "up"},
        ],
        "engagement_package": _package("台泥(示意)", "水泥", 72, 7_200_000, True, 0.22, "positive"),
    },
    {
        "name": "中油(示意)", "ticker": "CPC", "industry": "石油",
        "exposure_e_twd": 150, "company_value_e_twd": 9000, "annual_emissions_tco2e": 18_000_000, "pcaf_dq": 4,
        "high_climate_risk": True, "has_target": True, "is_policy": True, "talk_walk_gap": 0.40, "cbam_exposed": False,
        "negative_news": [
            {"title": "石油業示意客戶 A 煉製業減碳路徑與能源安全情境", "date": "2024-07-01", "source": NEGATIVE_NEWS_SOURCE},
            {"title": "油氣基礎設施汰換進度受關注情境", "date": "2023-09-13", "source": NEGATIVE_NEWS_SOURCE},
        ],
        "env_penalties": [{"time": "2023-05-27", "fact": "油槽區異味通報改善逾期", "law": "空氣污染防制法第32條", "fine": "500,000"}],
        "esg_20_scores": {"E": [1, 1, 0, 1, 0, 0, 1, 0], "S": [1, 1, 1, 1, 1, 1], "G": [1, 1, 1, 1, 1, 1]},
        "credit_bonus": {"公司治理": 2, "永續環境": 2, "社會公益": 3},
        "talk_features": {"淨零承諾強度": 0.75, "減碳目標數值": 0.64, "ESG關鍵字密度": 0.69, "永續報告書完整度": 0.78},
        "walk_features": {"外部ESG評等": 0.55, "過去3年碳排趨勢": 0.44, "爭議事件數": 0.52, "行業相對排名": 0.58},
        "shap_top5": [
            {"feature": "政策性投資降權", "value": -0.18, "direction": "down"},
            {"feature": "油氣產業長期轉型風險", "value": 0.16, "direction": "up"},
            {"feature": "近2年裁罰1件", "value": 0.06, "direction": "up"},
            {"feature": "能源安全政策角色", "value": -0.07, "direction": "down"},
            {"feature": "已有減碳承諾", "value": -0.05, "direction": "down"},
        ],
        "engagement_package": _package("中油(示意)", "石油", 150, 18_000_000, True, 0.40),
    },
    {
        "name": "長榮海運(示意)", "ticker": "2603", "industry": "航運",
        "exposure_e_twd": 80, "company_value_e_twd": 5000, "annual_emissions_tco2e": 6_000_000, "pcaf_dq": 3,
        "high_climate_risk": True, "has_target": True, "is_policy": False, "talk_walk_gap": 0.30, "cbam_exposed": False,
        "negative_news": [{"title": "航運業示意客戶 A 船隊燃油效率與替代燃料布局情境", "date": "2024-02-20", "source": NEGATIVE_NEWS_SOURCE}],
        "env_penalties": [],
        "esg_20_scores": {"E": [1, 1, 1, 0, 1, 0, 1, 1], "S": [1, 1, 1, 1, 1, 1], "G": [1, 1, 1, 1, 1, 1]},
        "credit_bonus": {"公司治理": 3, "永續環境": 2, "社會公益": 2},
        "talk_features": {"淨零承諾強度": 0.78, "減碳目標數值": 0.74, "ESG關鍵字密度": 0.62, "永續報告書完整度": 0.82},
        "walk_features": {"外部ESG評等": 0.66, "過去3年碳排趨勢": 0.60, "爭議事件數": 0.72, "行業相對排名": 0.63},
        "shap_top5": [
            {"feature": "高效率船隊汰換計畫", "value": -0.11, "direction": "down"},
            {"feature": "替代燃料採購仍待擴大", "value": 0.09, "direction": "up"},
            {"feature": "IMO減碳規範壓力", "value": 0.08, "direction": "up"},
            {"feature": "負面新聞少", "value": -0.06, "direction": "down"},
            {"feature": "永續報告書完整", "value": -0.05, "direction": "down"},
        ],
        "engagement_package": _package("長榮海運(示意)", "航運", 80, 6_000_000, True, 0.30, "positive"),
    },
    {
        "name": "遠東新(示意)", "ticker": "1402", "industry": "紡織化纖",
        "exposure_e_twd": 55, "company_value_e_twd": 3000, "annual_emissions_tco2e": 2_800_000, "pcaf_dq": 4,
        "high_climate_risk": True, "has_target": False, "is_policy": False, "talk_walk_gap": 0.50, "cbam_exposed": True,
        "negative_news": [
            {"title": "紡織化纖示意客戶 A 海外供應鏈碳揭露要求升高情境", "date": "2024-06-02", "source": NEGATIVE_NEWS_SOURCE},
            {"title": "化纖業再生料比例與品牌客戶要求落差情境", "date": "2023-08-07", "source": NEGATIVE_NEWS_SOURCE},
        ],
        "env_penalties": [{"time": "2024-04-09", "fact": "廢水檢測申報資料補正", "law": "水污染防治法第18條", "fine": "120,000"}],
        "esg_20_scores": {"E": [1, 0, 1, 1, 0, 1, 1, 0], "S": [1, 1, 1, 1, 1, 0], "G": [1, 1, 1, 0, 1, 1]},
        "credit_bonus": {"公司治理": 2, "永續環境": 2, "社會公益": 2},
        "talk_features": {"淨零承諾強度": 0.66, "減碳目標數值": 0.52, "ESG關鍵字密度": 0.75, "永續報告書完整度": 0.72},
        "walk_features": {"外部ESG評等": 0.50, "過去3年碳排趨勢": 0.42, "爭議事件數": 0.47, "行業相對排名": 0.45},
        "shap_top5": [
            {"feature": "未通過SBTi審核", "value": 0.13, "direction": "up"},
            {"feature": "CBAM/品牌客戶暴險", "value": 0.10, "direction": "up"},
            {"feature": "廢水裁罰1件", "value": 0.06, "direction": "up"},
            {"feature": "供應鏈管理揭露完整", "value": -0.07, "direction": "down"},
            {"feature": "再生料專案已有投資", "value": -0.04, "direction": "down"},
        ],
        "engagement_package": _package("遠東新(示意)", "紡織化纖", 55, 2_800_000, False, 0.50),
    },
    {
        "name": "某精密中小企業(示意)", "ticker": "N/A", "industry": "製造業",
        "exposure_e_twd": 8, "company_value_e_twd": None, "annual_emissions_tco2e": None, "pcaf_dq": 5,
        "high_climate_risk": "可能", "has_target": None, "is_policy": False, "talk_walk_gap": None, "cbam_exposed": None,
        "negative_news": [], "env_penalties": [],
        "esg_20_scores": {"E": [None, None, None, None, None, None, None, None], "S": [None, None, None, None, None, None], "G": [None, None, None, None, None, None]},
        "credit_bonus": {"公司治理": 0, "永續環境": 0, "社會公益": 0},
        "talk_features": {}, "walk_features": {}, "shap_top5": [],
        "engagement_package": {
            "current_summary": "本客戶為中小企業，ESG/碳排資料不足。系統不臆測補值，需請客戶補件或以明確方法估算並標註 PCAF DQ=5。",
            "gap_analysis": "NEED_HUMAN_REVIEW：Talk-Walk Gap 無法計算。",
            "engagement_method": "退回補件 + 聯徵 ESG 自評問卷",
            "dialogue_questions": [
                "1. 請提供最近年度能源使用量、用電量與營收資料。",
                "2. 是否已填寫聯徵 ESG 自評問卷？",
                "3. 是否有主要客戶要求碳盤查或產品碳足跡？",
                "4. 是否需要示意銀行協助進行產業別+營收估算排放？",
                "5. 是否願意將補件時程納入授信條件追蹤？",
            ],
            "tracking_kpis": [
                {"milestone": "T+1M", "target": "完成聯徵 ESG 自評問卷"},
                {"milestone": "T+3M", "target": "提交用電/燃料/營收資料供排放估算"},
                {"milestone": "T+6M", "target": "確認是否啟動碳盤查或客戶要求盤查"},
            ],
            "sll_suggestion": "資料不足，暫不建議設定SLL利率連動；待補件後再評估。",
        },
    },
]


def search_negative_news(client):
    return client.get("negative_news", [])


def lookup_env_penalties(client):
    return client.get("env_penalties", [])


def build_esg_checklist(client):
    emissions = client.get("annual_emissions_tco2e")
    has_missing_core = emissions is None or client.get("company_value_e_twd") is None
    if is_sme_data_gap_client(client):
        return [
            {"類別": "1. 近2年環境保護裁處資訊及改善情形", "狀態": "資料不足", "摘要": "查無重大裁罰，但資料覆蓋不足", "來源": "示意資料庫"},
            {"類別": "2. 近2年溫室氣體排放量資訊及營運影響", "狀態": "資料不足", "摘要": "範疇一/二排放量：未揭露", "來源": "客戶待補件"},
            {"類別": "3. 近2年勞動法規及改善情形", "狀態": "資料不足", "摘要": "中小企業待補件", "來源": "客戶待補件"},
            {"類別": "4. 近5年涉入訴訟案件資訊", "狀態": "資料不足", "摘要": "查無重大未決訴訟，但資料覆蓋不足", "來源": "示意資料庫"},
            {"類別": "5. AML/CFT名單掃描與可交易判斷", "狀態": "✓有資料", "摘要": "未命中制裁/資恐名單", "來源": "AML_SCREENING工具計算 / 法遵名單（示意）"},
            {"類別": "6. 近3年負面新聞", "狀態": "資料不足", "摘要": "查無重大新聞，但資料覆蓋不足", "來源": NEGATIVE_NEWS_SOURCE},
            {"類別": "7. 認證、獲獎、評鑑資訊", "狀態": "資料不足", "摘要": "永續報告書：無", "來源": "客戶待補件"},
        ]
    return [
        {"類別": "1. 近2年環境保護裁處資訊及改善情形", "狀態": "✓有資料" if client["env_penalties"] else "✓查無", "摘要": f"{len(client['env_penalties'])}件環保裁罰", "來源": "環保裁處資料庫（示意）"},
        {"類別": "2. 近2年溫室氣體排放量資訊及營運影響", "狀態": "⚠待覆核" if emissions is None else "✓有資料", "摘要": "缺排放量資料" if emissions is None else f"{emissions:,} tCO2e", "來源": "永續報告書 p.42 / PCAF資料表（示意）"},
        {"類別": "3. 近2年勞動法規及改善情形", "狀態": "⚠待覆核" if has_missing_core else "✓有資料", "摘要": "中小企業待補件" if has_missing_core else "查無重大違規；營建業5年工安事件不適用", "來源": "勞動部裁罰公開資料（示意）"},
        {"類別": "4. 近5年涉入訴訟案件資訊", "狀態": "✓有資料", "摘要": "查無重大未決訴訟" if not client["env_penalties"] else "需覆核裁罰相關行政救濟狀態", "來源": "司法院裁判書系統（示意）"},
        {"類別": "5. AML/CFT名單掃描與可交易判斷", "狀態": "✓有資料", "摘要": "未命中制裁/資恐名單", "來源": "AML_SCREENING工具計算 / 法遵名單（示意）"},
        {"類別": "6. 近3年負面新聞", "狀態": "✓有資料" if client["negative_news"] else "✓查無", "摘要": f"{len(client['negative_news'])}則負面/關注新聞", "來源": NEGATIVE_NEWS_SOURCE},
        {"類別": "7. 認證、獲獎、評鑑資訊", "狀態": "⚠待覆核" if has_missing_core else "✓有資料", "摘要": "待人工補認證/評鑑" if has_missing_core else "已匯入示意揭露資料與外部ESG評等", "來源": "永續報告書 p.58 / 外部 ESG 評等（示意）"},
    ]


def calculate_pcaf_financed_emissions(client):
    required = ["exposure_e_twd", "company_value_e_twd", "annual_emissions_tco2e"]
    missing = [field for field in required if client.get(field) is None]
    if missing:
        return {
            "status": "NEED_HUMAN_REVIEW",
            "missing_fields": missing,
            "source_note": "來源：PCAF_CALCULATOR工具計算；缺資料不臆測",
        }
    attribution = client["exposure_e_twd"] / client["company_value_e_twd"]
    financed = attribution * client["annual_emissions_tco2e"]
    return {
        "status": "OK",
        "attribution_factor": round(attribution, 6),
        "financed_emissions_tco2e": round(financed),
        "pcaf_dq": client["pcaf_dq"],
        "source_note": "來源：PCAF_CALCULATOR工具計算；PCAF Part A: Financed Emissions（範疇一+二）",
    }


def calculate_talk_walk_gap(client):
    gap = client.get("talk_walk_gap")
    if gap is None:
        return {"status": "NEED_HUMAN_REVIEW", "label": "NEED_HUMAN_REVIEW", "source_note": "來源：TALK_WALK_GAP工具計算；缺資料不臆測"}
    if gap >= 0.6:
        label = "⚠ 高落差"
    elif gap >= 0.35:
        label = "🟡 中落差"
    else:
        label = "🟢 低落差"
    return {"status": "OK", "gap": gap, "label": label, "source_note": "來源：TALK_WALK_GAP工具計算"}


def calculate_engagement_priority(client):
    if client.get("company_value_e_twd") is None or client.get("talk_walk_gap") is None:
        return {"status": "NEED_HUMAN_REVIEW", "priority_score": None, "rank_reason": "缺公司價值、排放或Talk-Walk資料", "policy_downweight": False}
    exposure_component = min(client["exposure_e_twd"] / 150, 1) * 35
    emissions_component = min(client["annual_emissions_tco2e"] / 25_000_000, 1) * 25
    gap_component = client["talk_walk_gap"] * 30
    controversy_component = min(len(client["negative_news"]) + len(client["env_penalties"]), 5) / 5 * 10
    score = exposure_component + emissions_component + gap_component + controversy_component
    policy_downweight = bool(client.get("is_policy"))
    if policy_downweight:
        score *= 0.55
    return {
        "status": "OK",
        "priority_score": round(score, 1),
        "policy_downweight": policy_downweight,
        "rank_reason": "政策性投資降權" if policy_downweight else "依暴險、排放、Talk-Walk Gap與爭議事件計算",
        "source_note": "來源：ENGAGEMENT_PRIORITY工具計算",
    }


def rank_portfolio():
    scored = []
    for client in DEMO_PORTFOLIO:
        result = calculate_engagement_priority(client)
        if result["status"] == "OK":
            scored.append({"name": client["name"], "industry": client["industry"], **result})
    return sorted(scored, key=lambda item: item["priority_score"], reverse=True)


def calculate_risk_level(client):
    if is_sme_data_gap_client(client):
        return "🟡 資料不足待覆核", "#F9A825"
    score = 0
    score += 2 if client.get("talk_walk_gap", 0) >= 0.6 else 1 if client.get("talk_walk_gap", 0) >= 0.35 else 0
    score += 1 if client.get("exposure_e_twd", 0) >= 80 else 0
    score += 1 if len(client.get("env_penalties", [])) >= 1 else 0
    score += 1 if client.get("cbam_exposed") else 0
    if score >= 4:
        return "🔴 高", "#E53935"
    if score >= 2:
        return "🟡 中", "#F9A825"
    return "🟢 低", "#1F6E43"


def needs_hitl(client):
    if is_sme_data_gap_client(client):
        return True, "中小企業資料不足 / 未揭露範疇一二排放 / 無永續報告書 / PCAF DQ 5/5"
    triggers = []
    if client.get("talk_walk_gap", 0) >= 0.6:
        triggers.append("高 Talk-Walk Gap")
    if client.get("env_penalties"):
        triggers.append("近2年環保裁罰")
    if client.get("high_climate_risk"):
        triggers.append("高氣候轉型風險產業")
    return bool(triggers), " / ".join(triggers) if triggers else "低風險案件，系統建議進入一般追蹤。"


def format_number(value, unit=""):
    if value is None:
        return "NEED_HUMAN_REVIEW"
    return f"{value:,.0f}{unit}"


def next_reassessment_date():
    return (date.today() + timedelta(days=90)).isoformat()
