from __future__ import annotations

import os
import time
import textwrap
from datetime import datetime

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import streamlit as st

from data import (
    DEMO_PORTFOLIO,
    ESG_INDICATORS,
    PAIN_POINTS,
    build_esg_checklist,
    calculate_engagement_priority,
    calculate_pcaf_financed_emissions,
    calculate_risk_level,
    calculate_talk_walk_gap,
    format_number,
    is_sme_data_gap_client,
    lookup_env_penalties,
    needs_hitl,
    next_reassessment_date,
    rank_portfolio,
    search_negative_news,
)


PRIMARY = "#008C72"
NAVY = "#0B1F4D"
MINT = "#1FAE8A"
RISK_RED = "#E53935"
SAFE_BLUE = "#1E88E5"
LIGHT_GREEN = "#F4FAF7"
SOFT_BORDER = "#DCEBE5"
CHART_GREEN = "#2E7D5B"
CHART_GREEN_2 = "#2F855A"
CHART_LIGHT_GREEN = "#DFF3EA"
CHART_DARK = "#1F2937"
CHART_GRAY = "#6B7280"
CHART_RISK_RED = "#D94A45"
CHART_RISK_BLUE = "#3B82C4"
CHART_WARNING = "#F2C94C"
CHART_TEAL = "#256F73"
CHART_GRID = "#E5E7EB"
DASHBOARD_DISCLAIMER = "免責聲明：所有企業資料均為示意性假資料，僅供 DSF506A 期末專案概念驗證。"
TALK_WALK_DISCLAIMER = "本模組輸出為輔助訊號（risk signal），非 greenwashing 認定。最終由徵審人員判斷。"
CREDIT_SUMMARY_DISCLAIMER = "本摘要由 AI Agent 自動彙整，所有數值由工具計算並附來源。最終授信決策由徵審人員判斷。"

DATA_VERSION = "demo_data_v1.0"
HITL_STATUS_LABELS = {
    "pending": "待覆核",
    "approved": "已核准議合",
    "returned": "退回補件",
}
HITL_AUDIT_STATUS = {
    "pending": "Pending review",
    "approved": "Human approved",
    "returned": "Need supplement",
}
SUPPLEMENT_ITEMS = [
    "範疇三盤查邊界與查證狀態",
    "董事會核准之中期減碳目標與時程",
    "CBAM / 主要客戶減碳要求因應資料",
    "高碳製程資本支出與投產時程",
]
SME_SUPPLEMENT_ITEMS = [
    "ESG 自評問卷",
    "最近一年用電量或能源帳單",
    "主要製程與產能資料",
    "溫室氣體盤查規劃",
    "聯徵 ESG 資訊或外部佐證文件",
]
STEP4_ENGAGEMENT_TOOLS = "PCAF_CALCULATOR() / ENGAGEMENT_PRIORITY() / package_builder()"
STEP6_MONITORING_TOOLS = "MONITORING_SCHEDULER() / KPI_TRACKER() / SBT_PATHWAY_TRACKER() / TRANSITION_GAP_CHART()"
SBT_PATHWAY_MISSING_MESSAGE = (
    "資料不足，尚無法建立可信賴 SBT 減碳路線圖。"
    "請先補件：基準年排放量、範疇一二盤查、董事會核准中期目標。"
)

plt.rcParams["font.sans-serif"] = [
    "PingFang TC",
    "Microsoft JhengHei",
    "Noto Sans CJK TC",
    "Arial Unicode MS",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False


def page_setup():
    st.set_page_config(page_title="ESG AI Credit Intelligence", page_icon="🌱", layout="wide")
    st.markdown(
        f"""
        <style>
        :root {{
            --navy: {NAVY};
            --green: {PRIMARY};
            --mint: {MINT};
            --soft-bg: {LIGHT_GREEN};
            --border: {SOFT_BORDER};
            --muted: #667085;
            --shadow: 0 18px 45px rgba(11, 31, 77, 0.08);
            --card-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        #MainMenu, header, footer {{
            visibility: hidden;
        }}
        .stApp {{
            background: #F8F9FA;
            color: var(--navy);
        }}
        .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 3rem;
            max-width: 1480px;
        }}
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FCFA 63%, #EAF7F2 100%);
            border-right: 1px solid #E5EEF0;
            box-shadow: 8px 0 28px rgba(11, 31, 77, 0.05);
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
            padding-top: 1.4rem;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: var(--navy);
            letter-spacing: 0;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: rgba(255,255,255,0.94);
            border-radius: 10px;
            box-shadow: var(--card-shadow);
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            border-radius: 10px;
        }}
        .app-shell {{
            width: 100%;
        }}
        .dashboard-title {{
            margin: 0 0 16px;
        }}
        .dashboard-title h1 {{
            margin: 0 0 6px;
            font-size: 2rem;
            font-weight: 900;
        }}
        .dashboard-title p {{
            margin: 0;
            color: #667085;
            line-height: 1.6;
        }}
        .dashboard-section-title {{
            margin: 20px 0 10px;
            color: var(--navy);
            font-size: 1.05rem;
            font-weight: 880;
        }}
        .kpi-inner {{
            min-height: 118px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .kpi-label {{
            color: #667085;
            font-size: 0.82rem;
            font-weight: 850;
            letter-spacing: .02em;
            text-transform: uppercase;
        }}
        .kpi-value {{
            margin-top: 8px;
            font-size: 1.7rem;
            line-height: 1.05;
            font-weight: 920;
        }}
        .kpi-note {{
            margin-top: 10px;
            color: #667085;
            font-size: 0.84rem;
            line-height: 1.45;
        }}
        .compact-company h3 {{
            margin: 8px 0 10px;
            font-size: 1.15rem;
            font-weight: 900;
        }}
        .compact-row {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            padding: 8px 0;
            border-bottom: 1px solid #EEF2F4;
            color: #344054;
            font-size: 0.9rem;
        }}
        .compact-row:last-child {{
            border-bottom: 0;
        }}
        .compact-row b {{
            color: #667085;
            font-weight: 760;
        }}
        .compact-row span {{
            text-align: right;
            font-weight: 820;
            color: var(--navy);
        }}
        .summary-list {{
            margin-top: 6px;
        }}
        .summary-list .summary-point {{
            padding: 10px 0;
            border-bottom: 1px solid #EEF2F4;
            line-height: 1.45;
        }}
        .summary-list .summary-point:last-child {{
            border-bottom: 0;
        }}
        .summary-point b {{
            display: block;
            color: #667085;
            font-size: 0.78rem;
            margin-bottom: 3px;
        }}
        .summary-point span {{
            color: var(--navy);
            font-weight: 820;
        }}
        .workflow-gate {{
            padding: 16px 18px;
            border-radius: 10px;
            background: #F0FAF7;
            border: 1px solid #CBEDE3;
            color: #255C4B;
            line-height: 1.55;
        }}
        .sidebar-logo {{
            padding: 14px 12px 18px;
            margin-bottom: 12px;
            border-bottom: 1px solid #E3EEF0;
        }}
        .sidebar-logo .brand-row {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .logo-mark {{
            width: 42px;
            height: 42px;
            border-radius: 14px;
            display: grid;
            place-items: center;
            color: white;
            font-weight: 900;
            background: linear-gradient(145deg, var(--green), var(--mint));
            box-shadow: 0 10px 24px rgba(0, 140, 114, 0.22);
        }}
        .sidebar-logo .brand-title {{
            font-size: 1.12rem;
            font-weight: 850;
            color: var(--navy);
            line-height: 1.05;
        }}
        .sidebar-logo .brand-subtitle {{
            font-size: 0.76rem;
            color: #637083;
            text-transform: uppercase;
            letter-spacing: .06em;
            margin-top: 3px;
        }}
        .sidebar-section {{
            margin: 12px 0;
            padding: 13px 13px;
            border-radius: 14px;
            color: var(--navy);
            background: rgba(255,255,255,0.74);
            border: 1px solid #E0ECE9;
            line-height: 1.55;
            font-size: 0.92rem;
        }}
        .sidebar-section b {{
            display: block;
            color: var(--green);
            margin-bottom: 4px;
        }}
        .sidebar-tagline {{
            margin: 24px 4px 6px;
            padding: 18px 12px;
            border-radius: 18px;
            color: var(--navy);
            text-align: center;
            background: linear-gradient(180deg, rgba(0,140,114,0.09), rgba(255,255,255,0.82));
            font-weight: 800;
        }}
        .sidebar-tagline span {{
            display: block;
            color: #526174;
            font-weight: 600;
            margin-top: 6px;
            line-height: 1.35;
        }}
        .hero {{
            position: relative;
            overflow: hidden;
            border-radius: 22px;
            padding: 30px 34px;
            margin-bottom: 22px;
            background:
                linear-gradient(90deg, rgba(255,255,255,0.97) 0%, rgba(255,255,255,0.93) 58%, rgba(229,247,241,0.82) 100%),
                linear-gradient(135deg, rgba(0,140,114,0.12), rgba(30,95,210,0.08));
            border: 1px solid #E3EEF0;
            box-shadow: var(--shadow);
        }}
        .hero:after {{
            content: "";
            position: absolute;
            right: -70px;
            top: -78px;
            width: 410px;
            height: 260px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(31,174,138,0.22), rgba(31,174,138,0.06) 48%, transparent 70%);
        }}
        .hero-topline {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 18px;
            position: relative;
            z-index: 1;
        }}
        .hero h1 {{
            margin: 8px 0 5px;
            font-size: clamp(2rem, 4vw, 3rem);
            line-height: 1.08;
            font-weight: 900;
        }}
        .hero .subtitle {{
            margin: 0 0 14px;
            font-size: 1.08rem;
            color: #153A6B;
            font-weight: 760;
        }}
        .hero p {{
            max-width: 880px;
            margin: 0;
            color: #5B6678;
            line-height: 1.75;
            font-size: 0.98rem;
        }}
        .metric-card, .flow-card, .risk-card, .section-card, .agent-card {{
            background: rgba(255,255,255,0.96);
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: var(--shadow);
        }}
        .metric-card {{
            min-height: 116px;
            padding: 18px 18px;
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .metric-icon {{
            width: 54px;
            height: 54px;
            border-radius: 18px;
            display: grid;
            place-items: center;
            color: var(--green);
            background: linear-gradient(145deg, #E8F8F2, #F6FBFF);
            font-size: 1.45rem;
            font-weight: 900;
        }}
        .metric-label {{
            color: var(--navy);
            font-size: 0.94rem;
            font-weight: 820;
            margin-bottom: 4px;
        }}
        .metric-value {{
            color: var(--green);
            font-size: 2rem;
            font-weight: 900;
            line-height: 1;
        }}
        .metric-note {{
            color: #667085;
            font-size: 0.82rem;
            margin-top: 6px;
        }}
        .client-card {{
            padding: 18px 20px;
            min-height: 142px;
        }}
        .card-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
        }}
        .client-name {{
            font-size: 1.26rem;
            color: var(--navy);
            font-weight: 900;
            margin: 8px 0 12px;
        }}
        .pill {{
            display: inline-flex;
            align-items: center;
            padding: 5px 11px;
            border-radius: 999px;
            color: var(--green);
            font-weight: 800;
            background: #EAF8F4;
            border: 1px solid #CBEDE3;
            margin: 3px 5px 3px 0;
            font-size: 0.84rem;
        }}
        .pill.blue {{
            color: #1857C8;
            background: #EEF5FF;
            border-color: #CFE0FF;
        }}
        .pill.purple {{
            color: #5B42C7;
            background: #F3F0FF;
            border-color: #DED8FF;
        }}
        .pill.red {{
            color: #C72929;
            background: #FFF1F1;
            border-color: #FFD4D4;
        }}
        .flow-card {{
            padding: 16px 12px;
            min-height: 140px;
            text-align: center;
            position: relative;
        }}
        .flow-card.done {{
            border: 1.5px solid var(--green);
            box-shadow: 0 18px 42px rgba(0,140,114,0.12);
        }}
        .flow-number {{
            width: 28px;
            height: 28px;
            margin: -4px auto 10px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            background: linear-gradient(145deg, var(--green), var(--mint));
            color: white;
            font-weight: 900;
            font-size: 0.82rem;
        }}
        .flow-title {{
            font-weight: 850;
            color: var(--navy);
            margin-bottom: 5px;
        }}
        .flow-note {{
            color: #667085;
            font-size: 0.82rem;
            line-height: 1.45;
        }}
        .flow-arrow {{
            display: grid;
            place-items: center;
            height: 140px;
            color: var(--navy);
            font-size: 1.55rem;
            font-weight: 900;
        }}
        .risk-card {{
            padding: 16px 17px;
            min-height: 126px;
            border-left: 5px solid var(--green);
        }}
        .risk-card.red {{ border-left-color: #E53935; background: linear-gradient(135deg, #FFF7F6, #FFFFFF); }}
        .risk-card.yellow {{ border-left-color: #F59E0B; background: linear-gradient(135deg, #FFFBEB, #FFFFFF); }}
        .risk-card.green {{ border-left-color: var(--green); background: linear-gradient(135deg, #F0FBF7, #FFFFFF); }}
        .risk-card.blue {{ border-left-color: #2563EB; background: linear-gradient(135deg, #F2F7FF, #FFFFFF); }}
        .risk-label {{
            color: #5B6678;
            font-size: 0.88rem;
            font-weight: 820;
        }}
        .risk-value {{
            margin: 8px 0 6px;
            color: var(--navy);
            font-weight: 920;
            font-size: 1.8rem;
            line-height: 1;
        }}
        .risk-detail {{
            color: #667085;
            font-size: 0.84rem;
        }}
        .gap-gauge-card, .pcaf-visual-card {{
            background: #FFFFFF;
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: var(--shadow);
            padding: 18px 18px;
            margin-bottom: 14px;
        }}
        .gap-gauge-card .label, .pcaf-visual-card .label {{
            color: #6B7280;
            font-size: 0.82rem;
            font-weight: 850;
            letter-spacing: .03em;
            text-transform: uppercase;
        }}
        .gap-gauge-card .score {{
            color: #1F2937;
            font-size: 2.1rem;
            font-weight: 920;
            margin: 5px 0 0;
            line-height: 1;
        }}
        .gap-gauge-card .state {{
            display: inline-flex;
            margin: 10px 0 12px;
            padding: 5px 10px;
            border-radius: 999px;
            color: #FFFFFF;
            font-size: 0.86rem;
            font-weight: 850;
        }}
        .progress-track {{
            width: 100%;
            height: 12px;
            border-radius: 999px;
            background: #EEF2F7;
            overflow: hidden;
            border: 1px solid #E5E7EB;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 999px;
        }}
        .gap-gauge-card .note, .pcaf-visual-card .note {{
            margin-top: 10px;
            color: #6B7280;
            font-size: 0.88rem;
            line-height: 1.55;
        }}
        .pcaf-visual-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 12px;
            margin: 12px 0;
        }}
        .pcaf-mini-card {{
            border-radius: 14px;
            border: 1px solid #E5E7EB;
            background: #F9FBFA;
            padding: 12px;
        }}
        .pcaf-mini-card b {{
            display: block;
            color: #1F2937;
            font-size: 1.05rem;
            margin-top: 4px;
        }}
        .section-card {{
            padding: 18px 18px 14px;
            margin-bottom: 18px;
        }}
        .section-heading {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin: 2px 0 12px;
        }}
        .section-heading h3 {{
            margin: 0;
            font-size: 1.05rem;
            font-weight: 880;
        }}
        .agent-card {{
            padding: 20px;
            margin: 10px 0 18px;
            border-top: 4px solid var(--green);
        }}
        .agent-card h3 {{
            margin: 0 0 12px;
            font-size: 1.22rem;
            color: var(--green);
        }}
        .agent-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
        }}
        .agent-field {{
            border-radius: 14px;
            background: #F7FBFA;
            border: 1px solid #E2EFEB;
            padding: 11px 12px;
            color: #526174;
            font-size: 0.88rem;
            line-height: 1.45;
        }}
        .agent-field b {{
            display: block;
            color: var(--navy);
            margin-bottom: 3px;
        }}
        .pain-box {{
            background: #ECF8F2;
            border-color: #BFE8D8;
            color: #255C4B;
        }}
        .status-chip {{
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 5px 10px;
            color: var(--green);
            background: #E7F8F3;
            border: 1px solid #C7EDE2;
            font-size: 0.8rem;
            font-weight: 850;
        }}
        .ai-summary {{
            padding: 18px;
            min-height: 100%;
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FCFB 100%);
        }}
        .ai-summary-item {{
            display: flex;
            gap: 11px;
            align-items: flex-start;
            margin: 14px 0;
            color: #26364F;
            line-height: 1.5;
            font-weight: 680;
        }}
        .ai-summary-icon {{
            width: 30px;
            height: 30px;
            border-radius: 10px;
            display: grid;
            place-items: center;
            flex: 0 0 30px;
            color: var(--green);
            background: #EAF8F4;
        }}
        .html-button {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 18px;
            border-radius: 13px;
            padding: 12px 14px;
            color: var(--navy);
            background: #EEF6FF;
            border: 1px solid #D7E8FF;
            font-weight: 850;
        }}
        .demo-card {{
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 16px 18px;
            background: rgba(255,255,255,0.96);
            box-shadow: var(--shadow);
        }}
        .source-note {{ color: #667085; font-size: 0.86rem; }}
        .step-title {{ color: {PRIMARY}; margin-top: 1.4rem; }}
        .red-box {{
            border-left: 5px solid {RISK_RED};
            background: #FFF3F2;
            border-radius: 16px;
            padding: 15px 16px;
            box-shadow: var(--shadow);
        }}
        .blue-box {{
            border-left: 5px solid {SAFE_BLUE};
            background: #F2F7FF;
            border-radius: 16px;
            padding: 15px 16px;
            box-shadow: var(--shadow);
        }}
        .orange-box {{
            border-left: 5px solid #FB8C00;
            background: #FFF7EC;
            border-radius: 16px;
            padding: 15px 16px;
            box-shadow: var(--shadow);
        }}
        .summary-card {{
            border-left: 5px solid {PRIMARY};
            background: #F0FAF4;
            border-radius: 16px;
            padding: 14px 16px;
            margin-top: 1rem;
            box-shadow: var(--shadow);
        }}
        .disclaimer-bar {{
            margin-top: 22px;
            padding: 14px 16px;
            border-radius: 16px;
            color: #344054;
            background: #F3F7FF;
            border: 1px solid #D9E7FF;
            font-size: 0.9rem;
            line-height: 1.55;
        }}
        div[data-testid="stMetric"] {{
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 12px 14px;
            box-shadow: 0 12px 28px rgba(11, 31, 77, 0.06);
        }}
        div[data-testid="stDataFrame"] {{
            border-radius: 16px;
            overflow: hidden;
        }}
        .stButton > button {{
            border-radius: 13px;
            font-weight: 850;
            border: 1px solid rgba(0,140,114,0.28);
            box-shadow: 0 10px 22px rgba(0,140,114,0.12);
        }}
        @media (max-width: 1100px) {{
            .hero-topline, .agent-grid {{
                display: block;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def default_client_index():
    return next((idx for idx, item in enumerate(DEMO_PORTFOLIO) if item["ticker"] == "1102"), 0)


def sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-logo">
                <div class="brand-row">
                    <div class="logo-mark">ESG</div>
                    <div>
                        <div class="brand-title">ESG AI Credit Intelligence</div>
                        <div class="brand-subtitle">POC Demo</div>
                    </div>
                </div>
            </div>
            <div class="sidebar-section">
                <b>專案定位</b>
                AI-assisted ESG 徵信、PCAF 融資排放與企業議合概念驗證。
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 對應銀行責任授信生命週期")
        lifecycle_placeholder = st.empty()
        render_lifecycle_sidebar(lifecycle_placeholder)

        with st.expander("課程技術對應", expanded=False):
            st.dataframe(
                pd.DataFrame(
                    [
                        ["Week 01", "AI in Finance", "責任授信痛點定義、金融資料三類型"],
                        ["Week 03/04", "ML / Feature Engineering", "Talk-Walk Gap 特徵設計、F1/PR-AUC評估"],
                        ["Week 06", "Transformer / Embedding", "永續報告書文字向量化、RAG檢索"],
                        ["Week 07", "Prompt Engineering", "議合包prompt四要素設計"],
                        ["Week 09", "Hallucination Control", "Never guess always compute、NEED_HUMAN_REVIEW"],
                        ["Week 10", "AI Agent / Tool Calling", "Data Agent、Engagement Agent、Orchestrator"],
                        ["全程", "Governance / HITL", "人工覆核、稽核軌跡、來源追溯"],
                    ],
                    columns=["週次", "主題", "本系統對應"],
                ),
                hide_index=True,
                width="stretch",
            )
        st.markdown(
            """
            <div class="sidebar-tagline">
                數據驅動・永續共融
                <span>Data-driven,<br>Sustainable Finance</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    return lifecycle_placeholder


def responsibility_lending_lifecycle(current_step):
    completed_stage = min(max(int(current_step or 0), 0), 6)
    if completed_stage == 1:
        completed_stage = 2

    lifecycle_labels = [
        "1. 徵提資料",
        "2. 徵信調查與實地訪查",
        "3. ESG 風險評分",
        "4. 完成徵信報告",
        "5. 徵信覆核 △",
        "6. 移交徵審核定 △",
    ]
    return [(label, index <= completed_stage) for index, label in enumerate(lifecycle_labels, start=1)]


def lifecycle_status_rows(current_step):
    rows = []
    for label, is_complete in responsibility_lending_lifecycle(current_step):
        if "徵信覆核" in label:
            rows.append(label)
            rows.append("HITL 人工覆核中")
        elif "移交徵審核定" in label:
            rows.append(label)
        else:
            rows.append(f"{label} {'✅' if is_complete else ''}".strip())
    return rows


def render_lifecycle_sidebar(container):
    lines = lifecycle_status_rows(st.session_state.get("current_step", 0))
    container.markdown("  \n".join(lines))


def hitl_summary_label(status):
    return HITL_STATUS_LABELS.get(status or "pending", "待覆核")


def workflow_state(workflow_started, hitl_status):
    if not workflow_started:
        return "READY_TO_START"
    if hitl_status == "approved":
        return "approved"
    if hitl_status == "returned":
        return "returned"
    if hitl_status == "pending":
        return "HITL_PENDING"
    return "running"


def monitoring_view_for_status(status, client=None):
    if status == "approved":
        return {"mode": "full"}
    if status == "returned":
        items = SME_SUPPLEMENT_ITEMS if client and is_sme_data_gap_client(client) else SUPPLEMENT_ITEMS
        return {
            "mode": "supplement",
            "message": "HITL 已退回補件；系統暫不移交貸後追蹤。",
            "items": items,
        }
    return {
        "mode": "blocked",
        "message": "尚未啟動｜待 HITL 核准後移交貸後追蹤",
        "tools_label": f"預計呼叫工具：{STEP6_MONITORING_TOOLS}",
    }


def plain_risk_label(risk_label):
    return risk_label.replace("🔴", "").replace("🟡", "").replace("🟢", "").replace("⚠", "").strip()


def display_client_name(name):
    return name


def hero_section():
    st.markdown(
        """
        <div class="app-shell">
            <section class="hero">
                <div class="hero-topline">
                    <div>
                        <div class="status-chip">概念驗證 Demo</div>
                        <h1>AI 輔助 ESG 徵信、PCAF 融資排放與企業議合系統</h1>
                        <div class="subtitle">概念驗證 Demo｜ESG 風險訊號、PCAF 計算與議合素材逐步工作流。</div>
                    </div>
                </div>
                <p>
                    依序展示 Data Agent、Credit Review Agent、Talk-Walk Gap、Engagement/PCAF、HITL 與 Post-loan Monitoring 的逐步 demo 流程。
                </p>
            </section>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(icon, label, value, note, accent="green"):
    color = {"green": PRIMARY, "blue": "#2563EB", "mint": MINT}.get(accent, PRIMARY)
    return f"""
    <div class="metric-card">
        <div class="metric-icon" style="color:{color};">{icon}</div>
        <div>
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
    </div>
    """


def render_home_kpis():
    cols = st.columns(3)
    cards = [
        metric_card("●●", "高氣候轉型風險產業客戶", "899", "示意情境數據", "green"),
        metric_card("◐", "議合覆蓋率", "87.5%", "示意已議合 / 應議合客戶", "mint"),
        metric_card("↯", "AI-assisted 工時節省", "1,248 小時", "示意流程估算", "blue"),
    ]
    for col, card in zip(cols, cards):
        col.markdown(card, unsafe_allow_html=True)


def render_workflow():
    st.markdown("#### ESG 徵信審查與議合工作流程（6 大步驟）")
    flow = [
        ("1", "徵提資料", "多源資料蒐集與標準化"),
        ("2", "ESG 指標評估", "20 項指標評估與量化評分"),
        ("3", "Talk-Walk Gap", "揭露與實際作為差距分析"),
        ("4", "議合包", "產出議合重點與建議方案"),
        ("5", "人工覆核", "專家覆核與調整議合策略"),
        ("6", "貸後追蹤", "追蹤承諾落實與績效改善"),
    ]
    cols = st.columns([1, 0.16, 1, 0.16, 1, 0.16, 1, 0.16, 1, 0.16, 1])
    flow_idx = 0
    for idx, col in enumerate(cols):
        if idx % 2:
            col.markdown("<div class='flow-arrow'>›</div>", unsafe_allow_html=True)
            continue
        number, title, note = flow[flow_idx]
        done = " done" if int(number) <= int(st.session_state.get("current_step", 0) or 0) else ""
        col.markdown(
            f"""
            <div class="flow-card{done}">
                <div class="flow-number">{number}</div>
                <div class="flow-title">{title}</div>
                <div class="flow-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        flow_idx += 1


def count_esg_scores(client):
    scores = [score for values in client["esg_20_scores"].values() for score in values]
    passed = sum(score == 1 for score in scores)
    needs_improvement = sum(score == 0 for score in scores)
    missing = sum(score is None for score in scores)
    return passed, needs_improvement, missing


def esg_risk_score(client):
    scores = [score for values in client["esg_20_scores"].values() for score in values]
    available = [score for score in scores if score is not None]
    pass_rate = sum(score == 1 for score in available) / len(available) if available else 0
    bonus_total = sum(client.get("credit_bonus", {}).values())
    bonus_rate = min(bonus_total / 9, 1)
    gap = client.get("talk_walk_gap")
    gap_strength = 0 if gap is None else 1 - gap
    strength_score = pass_rate * 55 + bonus_rate * 15 + gap_strength * 20
    if client.get("env_penalties"):
        strength_score -= min(len(client["env_penalties"]) * 3, 8)
    if client.get("cbam_exposed"):
        strength_score -= 2
    return max(0, min(100, round(100 - strength_score)))


def gap_detail(result):
    if result["status"] != "OK":
        return "NEED_HUMAN_REVIEW"
    label = result["label"]
    if "高" in label:
        return "高落差"
    if "中" in label:
        return "中落差"
    return "低落差"


def gap_visual_state(gap):
    if gap >= 0.6:
        return "高落差", CHART_RISK_RED
    if gap >= 0.4:
        return "中落差", CHART_WARNING
    return "低落差", CHART_GREEN


def render_talk_walk_gap_card(result):
    if result["status"] != "OK":
        st.markdown(
            """
            <div class="gap-gauge-card">
                <div class="label">Talk-Walk Gap</div>
                <div class="score">NEED_HUMAN_REVIEW</div>
                <div class="note">資料不足，系統不自動推測 Talk-Walk Gap。</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    gap = result["gap"]
    state, color = gap_visual_state(gap)
    st.markdown(
        f"""
        <div class="gap-gauge-card">
            <div class="label">Talk-Walk Gap</div>
            <div class="score">{gap:.2f} / 1.00</div>
            <div class="state" style="background:{color};">{state}</div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{gap * 100:.1f}%; background:{color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_risk_kpis(client):
    risk_label, _ = calculate_risk_level(client)
    risk_text = plain_risk_label(risk_label)
    talk_walk = calculate_talk_walk_gap(client)
    pcaf = calculate_pcaf_financed_emissions(client)
    pcaf_value = f"{pcaf['financed_emissions_tco2e']:,} tCO2e" if pcaf["status"] == "OK" else "NEED_HUMAN_REVIEW"
    pcaf_dq = f"{pcaf['pcaf_dq']} / 5" if pcaf["status"] == "OK" else f"{client.get('pcaf_dq', 5)} / 5"
    gap_value = f"{talk_walk['gap']:.2f}" if talk_walk["status"] == "OK" else "N/A"
    cols = st.columns(4)
    cards = [
        ("red", "ESG 風險等級", risk_text, f"綜合評分：{esg_risk_score(client)} / 100"),
        ("yellow", "Talk-Walk Gap", gap_value, gap_detail(talk_walk)),
        ("green", "PCAF 融資排放", pcaf_value, "範疇 1+2（2024）"),
        ("blue", "PCAF DQ", pcaf_dq, "資料品質等級：" + ("最弱，待補件" if is_sme_data_gap_client(client) else "一般")),
    ]
    for col, (style, label, value, detail) in zip(cols, cards):
        col.markdown(
            f"""
            <div class="risk-card {style}">
                <div class="risk-label">{label}</div>
                <div class="risk-value">{value}</div>
                <div class="risk-detail">{detail}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dashboard_title():
    st.markdown(
        """
        <div class="dashboard-title">
            <h1>ESG 徵信與議合工作台</h1>
            <p>AI-assisted ESG risk signal、PCAF 融資排放與企業議合 POC。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_metric_card(label, value, note, color):
    st.markdown(
        f"""
        <div class="kpi-inner">
            <div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="color:{color};">{value}</div>
            </div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_metric_cards(client):
    risk_label, risk_color = calculate_risk_level(client)
    risk_text = plain_risk_label(risk_label)
    talk_walk = calculate_talk_walk_gap(client)
    pcaf = calculate_pcaf_financed_emissions(client)
    hitl_label = hitl_summary_label(st.session_state.get("hitl_status", "pending"))

    exposure = client["exposure_e_twd"]
    exposure_color = RISK_RED if exposure >= 100 else PRIMARY
    if pcaf["status"] == "OK":
        pcaf_value = f"{pcaf['financed_emissions_tco2e']:,} tCO2e"
        pcaf_note = f"PCAF DQ {pcaf['pcaf_dq']}/5｜範疇 1+2 示意"
        pcaf_color = RISK_RED if pcaf["financed_emissions_tco2e"] >= 150_000 else PRIMARY
    else:
        pcaf_value = "NEED_HUMAN_REVIEW"
        pcaf_note = f"PCAF DQ {client.get('pcaf_dq', 5)}/5｜資料缺口待補"
        pcaf_color = RISK_RED

    if talk_walk["status"] == "OK":
        gap = talk_walk["gap"]
        gap_value = f"{gap:.2f}"
        gap_note = gap_detail(talk_walk)
        gap_color = RISK_RED if gap >= 0.6 else "#F59E0B" if gap >= 0.4 else PRIMARY
    else:
        gap_value = "N/A"
        gap_note = "NEED_HUMAN_REVIEW"
        gap_color = RISK_RED

    cards = [
        ("融資暴險 (Exposure)", format_number(exposure, " 億元"), "示意授信暴險金額", exposure_color),
        ("風險等級 (Risk Level)", risk_text, f"ESG risk score {esg_risk_score(client)}/100｜HITL：{hitl_label}", risk_color),
        ("PCAF 融資排放", pcaf_value, pcaf_note, pcaf_color),
        ("Talk-Walk Gap", gap_value, gap_note, gap_color),
    ]
    cols = st.columns(4)
    for col, (label, value, note, color) in zip(cols, cards):
        with col:
            with st.container(border=True):
                kpi_metric_card(label, value, note, color)


def render_ai_summary_compact(client):
    hitl_status = st.session_state.get("hitl_status", "pending")
    rows = {row["項目"]: row["結果"] for row in build_esg_credit_summary(client, hitl_status)}
    st.markdown(
        f"""
        <div class="summary-list">
            <div class="summary-point"><b>議合優先排名</b><span>{rows['議合優先排名']}</span></div>
            <div class="summary-point"><b>建議議合方式</b><span>{rows['建議議合方式']}</span></div>
            <div class="summary-point"><b>SBT / SLL 路線圖</b><span>{rows['SBT / SLL 路線圖']}</span></div>
            <div class="summary-point"><b>HITL 覆核結論</b><span>{rows['HITL 覆核結論']}</span></div>
            <div class="summary-point"><b>下次重評時間</b><span>{rows['下次重評時間']}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_core_visualizations(client):
    left_col, right_col = st.columns([7, 3])
    with left_col:
        st.markdown("<div class='dashboard-section-title'>核心視覺化</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### SHAP 貢獻度圖表")
            shap_values = {item["feature"]: item["value"] for item in client.get("shap_top5", [])}
            if shap_values:
                shap_risk_driver_chart(shap_values)
            else:
                st.warning("NEED_HUMAN_REVIEW：缺 SHAP 驅動因子示意資料。")
        with st.container(border=True):
            st.markdown("#### SBT/SLL 減碳路線圖")
            render_sbt_pathway_preview(client)
    with right_col:
        st.markdown("<div class='dashboard-section-title'>客戶快照</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### 客戶基本資料卡")
            company_card(client)
        with st.container(border=True):
            st.markdown("#### AI 輔助 ESG 徵信摘要")
            render_ai_summary_compact(client)


def wrapped_label(label, width=16):
    return "\n".join(textwrap.wrap(str(label), width=width, break_long_words=False, replace_whitespace=False))


def apply_professional_chart_style(ax, title, subtitle=None, xlabel=None, ylabel=None):
    fig = ax.figure
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_title(title, loc="left", fontsize=16, fontweight="bold", color=CHART_DARK, pad=24 if subtitle else 16)
    if subtitle:
        ax.text(
            0,
            1.02,
            subtitle,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=11,
            color=CHART_GRAY,
        )
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11, color=CHART_DARK, labelpad=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11, color=CHART_DARK, labelpad=10)
    ax.tick_params(axis="both", labelsize=10.5, colors=CHART_DARK)
    ax.grid(axis="x", color=CHART_GRID, alpha=0.42, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#D1D5DB")
        ax.spines[spine].set_linewidth(0.8)


def format_emissions_axis(ax):
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{int(value):,}"))


def render_professional_pyplot(fig):
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True, width="stretch")


def sbt_pathway_preview(client):
    if is_sme_data_gap_client(client) or client.get("annual_emissions_tco2e") is None:
        return {
            "status": "NEED_HUMAN_REVIEW",
            "message": SBT_PATHWAY_MISSING_MESSAGE,
        }
    return {
        "status": "OK",
        "title": "SBT / SLL KPI 減碳路線圖預覽",
        "subtitle": "以基準年排放量、目標路徑與貸後追蹤節點建立議合基礎",
        "rows": [
            {"year": 2024, "label": "Baseline emissions", "emissions_tco2e": 18_000_000},
            {"year": 2026, "label": "2026 target", "emissions_tco2e": 17_100_000},
            {"year": 2027, "label": "2027 target", "emissions_tco2e": 16_200_000},
            {"year": 2030, "label": "2030 target", "emissions_tco2e": 13_500_000},
            {"year": 2050, "label": "Net Zero / near zero pathway", "emissions_tco2e": 0},
        ],
    }


def sbt_route_summary(client):
    if is_sme_data_gap_client(client) or client.get("annual_emissions_tco2e") is None:
        return "資料不足，需補件後建立"
    return "已建立示意減碳路線圖，待 HITL 覆核後移交貸後追蹤"


def render_sbt_pathway_preview(client):
    preview = sbt_pathway_preview(client)
    if preview["status"] != "OK":
        st.warning(preview["message"])
        return

    st.markdown(f"#### {preview['title']}")
    st.caption(preview["subtitle"])
    rows = preview["rows"]
    years = [row["year"] for row in rows]
    emissions = [row["emissions_tco2e"] for row in rows]
    fig, ax = plt.subplots(figsize=(8.8, 4.4), dpi=200)
    ax.plot(years, emissions, color=CHART_GREEN, marker="o", linewidth=2.8, label="SBT / SLL milestone pathway")
    for row in rows:
        ax.annotate(
            row["label"],
            xy=(row["year"], row["emissions_tco2e"]),
            xytext=(0, 12),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            color=CHART_DARK,
        )
    apply_professional_chart_style(
        ax,
        "SBT / SLL KPI Reduction Pathway Preview",
        "Baseline emissions, target pathway and post-loan checkpoints",
        "Year",
        "Emissions (tCO2e)",
    )
    ax.grid(axis="y", color=CHART_GRID, alpha=0.42, linewidth=0.8)
    ax.set_xticks(years)
    ax.set_ylim(0, 19_800_000)
    format_emissions_axis(ax)
    ax.legend(frameon=False, loc="upper right")
    render_professional_pyplot(fig)


def post_loan_monitoring_pathway():
    return {
        "years": [2024, 2025, 2026, 2027, 2030],
        "actual_emissions": [18_000_000, 17_800_000, 17_100_000, None, None],
        "sbt_target_pathway": [18_000_000, 17_550_000, 17_100_000, 16_200_000, 13_500_000],
        "industry_transition_pathway": [18_000_000, 17_700_000, 17_300_000, 16_800_000, 14_500_000],
    }


def render_post_loan_sbt_pathway_chart():
    pathway = post_loan_monitoring_pathway()
    years = pathway["years"]
    fig, ax = plt.subplots(figsize=(9.4, 4.8), dpi=200)
    ax.plot(
        years,
        pathway["actual_emissions"],
        color=CHART_GREEN,
        linestyle="-",
        marker="o",
        linewidth=2.8,
        label="Baseline / Actual emissions",
    )
    ax.plot(
        years,
        pathway["sbt_target_pathway"],
        color=CHART_RISK_RED,
        linestyle="--",
        marker="o",
        linewidth=2.4,
        label="SBT target pathway",
    )
    ax.plot(
        years,
        pathway["industry_transition_pathway"],
        color="#607D8B",
        linestyle=":",
        marker="o",
        linewidth=2.6,
        label="Industry transition pathway",
    )
    apply_professional_chart_style(
        ax,
        "SBT Reduction Pathway & Post-loan Monitoring",
        "Actual emissions vs SBT target vs industry transition pathway",
        "Year",
        "Emissions (tCO2e)",
    )
    ax.grid(axis="y", color=CHART_GRID, alpha=0.42, linewidth=0.8)
    ax.set_xticks(years)
    ax.set_ylim(13_000_000, 18_700_000)
    format_emissions_axis(ax)
    ax.legend(frameon=False, loc="upper right")
    render_professional_pyplot(fig)


def donut_indicator_chart(client):
    passed, needs_improvement, missing = count_esg_scores(client)
    values = [passed, needs_improvement, missing]
    labels = ["通過", "待改善", "待補件"]
    colors = [CHART_GREEN, CHART_WARNING, "#9CA3AF"]
    fig, ax = plt.subplots(figsize=(5.2, 4.2), dpi=200)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    wedges, _ = ax.pie(values, colors=colors, startangle=90, counterclock=False, wedgeprops={"width": 0.38, "edgecolor": "white"})
    ax.text(0, 0.08, "20", ha="center", va="center", fontsize=26, color=CHART_DARK, fontweight="bold")
    ax.text(0, -0.16, "ESG 指標", ha="center", va="center", fontsize=10.5, color=CHART_GRAY)
    ax.set_title("ESG Indicator Review Mix", loc="left", fontsize=15, fontweight="bold", color=CHART_DARK, pad=12)
    ax.text(0, 0.98, "20 項 ESG 指標通過 / 待改善 / 待補件分布", transform=ax.transAxes, fontsize=10.5, color=CHART_GRAY)
    ax.legend(wedges, [f"{label} ({value})" for label, value in zip(labels, values)], loc="center left", bbox_to_anchor=(0.96, 0.5), frameon=False, fontsize=9.5)
    ax.set(aspect="equal")
    render_professional_pyplot(fig)


def radar_chart(client):
    def avg(items):
        available = [value for value in items if value is not None]
        return sum(available) / len(available) if available else 0

    gap = client.get("talk_walk_gap")
    values = [
        avg(client["esg_20_scores"]["E"]),
        avg(client["esg_20_scores"]["S"]),
        avg(client["esg_20_scores"]["G"]),
        0.45 if gap is None else max(0, 1 - gap),
        client.get("talk_features", {}).get("永續報告書完整度", avg(client["esg_20_scores"]["G"])),
    ]
    labels = ["環境(E)", "社會(S)", "治理(G)", "氣候策略(CS)", "治理與透明度(GT)"]
    angles = [n / float(len(labels)) * 2 * 3.141592653589793 for n in range(len(labels))]
    values += values[:1]
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(5.2, 4.3), dpi=200, subplot_kw={"polar": True})
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.plot(angles, values, color=CHART_GREEN, linewidth=2.6, label=client["name"].split("(")[0])
    ax.fill(angles, values, color=CHART_LIGHT_GREEN, alpha=0.55)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9.5, color=CHART_DARK)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], fontsize=8, color=CHART_GRAY)
    ax.set_ylim(0, 1)
    ax.grid(color=CHART_GRID, alpha=0.65)
    ax.spines["polar"].set_color("#D1D5DB")
    ax.set_title("ESG Dimension Profile", loc="left", fontsize=15, fontweight="bold", color=CHART_DARK, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.08), frameon=False, fontsize=8.5)
    render_professional_pyplot(fig)


def transition_trend_chart(client):
    gap = client.get("talk_walk_gap")
    if gap is None:
        st.warning("NEED_HUMAN_REVIEW：缺 Talk-Walk Gap 資料，無法繪製轉型落差趨勢。")
        return
    years = ["2022", "2023", "2024", "2025E", "2030 目標"]
    values = [min(gap + 0.24, 1), min(gap + 0.13, 1), gap, max(gap - 0.12, 0.05), 0.20]
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=200)
    ax.plot(years[:4], values[:4], marker="o", color=CHART_RISK_BLUE, linewidth=2.8, label="實際 / 預估")
    ax.plot(years[3:], values[3:], marker="o", color=CHART_GREEN, linestyle="--", linewidth=2.5, label="目標")
    for x, y in zip(years, values):
        ax.text(x, y + 0.035, f"{y:.2f}", ha="center", fontsize=9, color=CHART_DARK, fontweight="bold")
    ax.set_ylim(0, 1)
    apply_professional_chart_style(
        ax,
        "Transition Gap Trend",
        "SBT 產業路徑與客戶目前轉型落差趨勢",
        ylabel="Transition Gap",
    )
    ax.grid(axis="y", color=CHART_GRID, alpha=0.38)
    ax.legend(frameon=False, loc="upper right", fontsize=9.5)
    render_professional_pyplot(fig)


def render_chart_dashboard(client):
    chart_cols = st.columns([1, 1, 1.22])
    charts = [
        ("ESG 20 項指標評估分布", donut_indicator_chart),
        ("ESG 構面雷達圖", radar_chart),
        ("轉型落差（Transition Gap）趨勢", transition_trend_chart),
    ]
    for col, (title, renderer) in zip(chart_cols, charts):
        with col:
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-heading"><h3>{title}</h3><span class="status-chip">示意</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            renderer(client)


def render_ai_summary_card():
    items = [
        ("◌", "提升氣候策略與減碳執行力"),
        ("▥", "擴大綠色產品與低碳轉型資本支出"),
        ("◇", "強化供應鏈 ESG 管理"),
        ("▤", "優化資訊揭露品質"),
        ("♙", "建議議合策略"),
    ]
    rows = "".join(
        f"<div class='ai-summary-item'><div class='ai-summary-icon'>{icon}</div><div>{text}</div></div>"
        for icon, text in items
    )
    st.markdown(
        f"""
        <div class="section-card ai-summary">
            <div class="section-heading"><h3>AI Agent 建議摘要</h3><span class="status-chip">資料整理完成｜待 HITL 覆核</span></div>
            {rows}
            <div class="html-button"><span>查看完整議合包</span><span>›</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def audit_row(step, tool, source, actor="AI Agent", review_status="AI completed", hitl="N/A"):
    return {
        "時間戳": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "步驟": step,
        "工具名": tool,
        "來源": source,
        "人工覆核": hitl,
        "執行者": actor,
        "資料版本": DATA_VERSION,
        "覆核狀態": review_status,
    }


def add_audit(step, tool, source, hitl="N/A", actor="AI Agent", review_status="AI completed"):
    row = audit_row(step, tool, source, actor, review_status, hitl)
    existing_index = next((idx for idx, item in enumerate(st.session_state.audit) if item["步驟"] == step), None)
    if existing_index is None:
        st.session_state.audit.append(row)
    else:
        st.session_state.audit[existing_index] = row
    st.session_state.audit_status = review_status


def step_header(
    number,
    title,
    pain_label,
    lifecycle_placeholder=None,
    tools=None,
    status_text="Agent 工作完成",
    work_status=None,
    lifecycle_step=None,
):
    st.session_state.current_step = int(lifecycle_step if lifecycle_step is not None else number)
    if lifecycle_placeholder is not None:
        render_lifecycle_sidebar(lifecycle_placeholder)
    tools_text = tools or "由對應 Agent 工具鏈自動呼叫並保留稽核軌跡"
    work_status_text = work_status or "資料蒐集、計算與輸出已完成，待徵審人員覆核。"
    st.markdown(
        f"""
        <div class="agent-card">
            <div class="card-title-row">
                <h3>Step {number}/6｜{title}</h3>
                <span class="status-chip">{status_text}</span>
            </div>
            <div class="agent-grid">
                <div class="agent-field pain-box"><b>解決痛點</b>{pain_label}</div>
                <div class="agent-field"><b>Agent 工作狀態</b>{work_status_text}</div>
                <div class="agent-field"><b>呼叫工具紀錄</b>{tools_text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def company_card(client):
    risk_label, risk_color = calculate_risk_level(client)
    high_climate_risk = client.get("high_climate_risk")
    if isinstance(high_climate_risk, str):
        climate_risk_text = high_climate_risk
    else:
        climate_risk_text = "是" if high_climate_risk else "否"
    st.markdown(
        f"""
        <div class="demo-card compact-company">
            <span class="pill">{client['industry']}</span>
            <h3>{client['name']}</h3>
            <div class="compact-row"><b>Ticker</b><span>{client['ticker']}</span></div>
            <div class="compact-row"><b>融資暴險</b><span>{format_number(client['exposure_e_twd'], ' 億元')}</span></div>
            <div class="compact-row"><b>高氣候轉型風險</b><span>{climate_risk_text}</span></div>
            <div class="compact-row"><b>政策性投資</b><span>{'是' if client['is_policy'] else '否'}</span></div>
            <div class="compact-row"><b>風險等級</b><span style="color:{risk_color};">{risk_label}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_news(news):
    if not news:
        st.info("查無近3年負面新聞（示意）。")
        return
    for item in news:
        st.write(f"- {item['date']}｜{item['title']}｜來源：{item['source']}")


def render_penalties(penalties):
    if not penalties:
        st.info("查無近2年環保裁罰（示意）。")
        return
    st.dataframe(pd.DataFrame(penalties), hide_index=True, width="stretch")


def esg_indicator_rows(client):
    rows = []
    for pillar, labels in ESG_INDICATORS.items():
        for label, score in zip(labels, client["esg_20_scores"][pillar]):
            if score is None:
                mark = "— 待補件"
            else:
                mark = "✓ 通過" if score == 1 else "✗ 待改善"
            rows.append({"面向": pillar, "指標": label, "結果": mark})
    return rows


def render_esg_indicators(client):
    rows = esg_indicator_rows(client)
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=735)


def talk_walk_signal_profile_chart(values):
    items = []
    for raw_label, value in values.items():
        kind, feature = raw_label.split("｜", 1) if "｜" in raw_label else ("Talk", raw_label)
        display_kind = "Talk disclosure signals" if kind == "Talk" else "Walk performance signals"
        items.append((display_kind, feature, value))
    items = sorted(items, key=lambda item: (0 if item[0].startswith("Talk") else 1, item[1]))
    labels = [wrapped_label(feature, 18) for _, feature, _ in items]
    nums = [value for _, _, value in items]
    colors = [CHART_GREEN if kind.startswith("Talk") else CHART_TEAL for kind, _, _ in items]

    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=200)
    y_positions = range(len(items))
    ax.barh(y_positions, nums, color=colors, height=0.58, edgecolor="none")
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(labels, fontsize=10.5, color=CHART_DARK)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.axvline(0.5, color="#CBD5E1", linewidth=1.2, linestyle="--", alpha=0.9)
    for y, value in zip(y_positions, nums):
        ax.text(min(value + 0.025, 0.98), y, f"{value:.2f}", va="center", ha="left", fontsize=10, color=CHART_DARK, fontweight="bold")
    apply_professional_chart_style(
        ax,
        "Talk vs Walk ESG Signal Profile",
        "揭露承諾與實際轉型證據之間的特徵比較",
        xlabel="Signal strength (0-1)",
    )
    from matplotlib.patches import Patch

    ax.legend(
        handles=[
            Patch(facecolor=CHART_GREEN, label="Talk disclosure signals"),
            Patch(facecolor=CHART_TEAL, label="Walk performance signals"),
        ],
        loc="lower right",
        frameon=False,
        fontsize=9.5,
    )
    render_professional_pyplot(fig)


def shap_risk_driver_chart(values):
    ordered = sorted(values.items(), key=lambda item: item[1])
    labels = [wrapped_label(label, 24) for label, _ in ordered]
    nums = [value for _, value in ordered]
    colors = [CHART_RISK_RED if value > 0 else CHART_RISK_BLUE for value in nums]
    limit = max(abs(min(nums, default=0)), abs(max(nums, default=0))) + 0.08

    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    y_positions = range(len(ordered))
    ax.barh(y_positions, nums, color=colors, height=0.58, edgecolor="none")
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(labels, fontsize=10.8, color=CHART_DARK)
    ax.set_xlim(-limit, limit)
    ax.axvline(0, color=CHART_DARK, linewidth=0.9, alpha=0.78)
    for y, value in zip(y_positions, nums):
        offset = 0.012 if value >= 0 else -0.012
        ha = "left" if value >= 0 else "right"
        ax.text(value + offset, y, f"{value:+.2f}", va="center", ha=ha, fontsize=10, color=CHART_DARK, fontweight="bold")
    apply_professional_chart_style(
        ax,
        "Top Risk Drivers from SHAP Explanation",
        "紅色表示提高風險，藍色表示降低風險",
        xlabel="SHAP contribution to ESG risk signal",
    )
    ax.grid(axis="x", color=CHART_GRID, alpha=0.35)
    render_professional_pyplot(fig)


def bar_chart(title, values, positive_negative=False):
    if positive_negative:
        shap_risk_driver_chart(values)
        return
    if any(str(label).startswith("Talk｜") or str(label).startswith("Walk｜") for label in values):
        talk_walk_signal_profile_chart(values)
        return

    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=200)
    labels = list(values.keys())
    nums = list(values.values())
    colors = [CHART_GREEN] * len(nums)
    ax.barh([wrapped_label(label, 22) for label in labels], nums, color=colors, height=0.58)
    for y, value in enumerate(nums):
        ax.text(value + 0.025, y, f"{value:.2f}", va="center", ha="left", fontsize=10, color=CHART_DARK, fontweight="bold")
    ax.set_xlim(min(0, min(nums, default=0) - 0.05), max(nums, default=1) + 0.08)
    apply_professional_chart_style(ax, title, xlabel="Signal strength")
    render_professional_pyplot(fig)


def line_gap_chart(client):
    if client.get("annual_emissions_tco2e") is None:
        st.warning("NEED_HUMAN_REVIEW：缺排放量資料，無法繪製 SBT 路徑 vs 客戶實際。")
        return
    baseline = client["annual_emissions_tco2e"]
    industry_rate = 0.035 if client["industry"] in ["石化", "水泥", "鋼鐵"] else 0.025
    actual_rate = max(0.005, industry_rate * (1 - (client.get("talk_walk_gap") or 0.4)))
    years = ["2024", "2025", "2026", "2027", "2028"]
    path = [baseline * ((1 - industry_rate) ** i) for i in range(5)]
    actual = [baseline * ((1 - actual_rate) ** i) for i in range(5)]
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=200)
    ax.plot(years, path, marker="o", color=CHART_GREEN, linewidth=2.8, markersize=6.5, label="產業 SBT 路徑")
    ax.plot(years, actual, marker="o", color=CHART_RISK_RED, linewidth=2.8, markersize=6.5, label="客戶目前趨勢")
    for x, y in zip(years, path):
        ax.text(x, y, f"{y/1_000_000:.1f}M", ha="center", va="bottom", fontsize=8.5, color=CHART_GREEN, fontweight="bold")
    for x, y in zip(years, actual):
        ax.text(x, y, f"{y/1_000_000:.1f}M", ha="center", va="top", fontsize=8.5, color=CHART_RISK_RED, fontweight="bold")
    apply_professional_chart_style(
        ax,
        "SBT Path vs Client Actual Trend",
        "貸後追蹤：產業減碳路徑與客戶目前排放趨勢比較",
        ylabel="tCO2e",
    )
    ax.grid(axis="y", color=CHART_GRID, alpha=0.38)
    ax.legend(frameon=False, loc="upper right", fontsize=9.5)
    render_professional_pyplot(fig)


def run_status(lines):
    with st.status("Agent 工作中...", expanded=True) as status:
        for line in lines:
            st.write(line)
            time.sleep(0.35)
        status.update(label="Agent 工作完成 ✓", state="complete", expanded=True)


def pain_intro_text():
    return """現行痛點：
- 貸前：七大類 ESG 徵信資料（環保裁處、溫室氣體、勞動法規、訴訟、AML、負面新聞、認證評鑑）需人工逐案蒐集，20 項 ESG 指標每半年重新檢視
- 貸中：高碳排客戶議合需準備 ESG 現況、減碳缺口、轉型風險、PCAF 融資排放，人工難以規模化
- 貸後：需重算 PCAF、追蹤 SBT 目標、SLL KPI、偵測負面事件，揭露時程壓力大
- 中小企業：資料最缺，但仍須納入融資排放計算

本系統以 AI Agent 協助上述流程，將重複性資料整理工作 AI-assisted 化，保留徵審人員最終判斷。"""


def render_pain_intro():
    st.info(pain_intro_text())


def pcaf_formula_note():
    return """PCAF 示意公式：
歸因係數 = 示意融資暴險 ÷ 企業價值（EVIC）
融資排放 = 歸因係數 × 企業 Scope 1+2 排放量
PCAF DQ = 資料品質分數（1 最佳、5 最差）
本 demo 僅為概念驗證，實際導入時需依 PCAF 資產類別、Scope 邊界與內部模型驗證調整。"""


def render_pcaf_formula_note():
    st.markdown(
        f"<div class='source-note'>{pcaf_formula_note().replace(chr(10), '<br>')}</div>",
        unsafe_allow_html=True,
    )


def tool_calculation_explanation_rows(client):
    talk_values = list(client.get("talk_features", {}).values())
    walk_values = list(client.get("walk_features", {}).values())
    talk_avg = sum(talk_values) / len(talk_values) if talk_values else None
    walk_avg = sum(walk_values) / len(walk_values) if walk_values else None
    gap = calculate_talk_walk_gap(client)
    priority = calculate_engagement_priority(client)

    if gap["status"] != "OK" or talk_avg is None or walk_avg is None:
        gap_result = "NEED_HUMAN_REVIEW"
        gap_formula = "Talk / Walk 特徵不足，工具不臆測分數。"
    else:
        gap_result = f"{gap['gap']:.2f}"
        gap_formula = (
            "POC 加權公式：Talk 平均、Walk 平均、爭議事件與產業路徑缺口加權後正規化；"
            f"Talk 平均 {talk_avg:.2f}、Walk 平均 {walk_avg:.2f}。"
        )

    if priority["status"] != "OK":
        priority_result = "NEED_HUMAN_REVIEW"
        priority_formula = "缺公司價值、排放或 Talk-Walk 資料，工具不臆測排序。"
    else:
        exposure_component = min(client["exposure_e_twd"] / 150, 1) * 35
        emissions_component = min(client["annual_emissions_tco2e"] / 25_000_000, 1) * 25
        gap_component = client["talk_walk_gap"] * 30
        controversy_component = min(len(client["negative_news"]) + len(client["env_penalties"]), 5) / 5 * 10
        priority_result = f"{priority['priority_score']:.1f}"
        priority_formula = (
            "暴險 35% + 排放量 25% + Talk-Walk Gap 30% + 爭議事件 10%；"
            f"本案 = {exposure_component:.1f} + {emissions_component:.1f} + "
            f"{gap_component:.1f} + {controversy_component:.1f}。"
        )

    return [
        {
            "指標": "Talk-Walk Gap",
            "公式": gap_formula,
            "計算結果": gap_result,
            "治理說明": "由工具依權重計算；LLM 僅負責摘要與格式化，不猜測分數。",
        },
        {
            "指標": "Engagement Priority",
            "公式": priority_formula,
            "計算結果": priority_result,
            "治理說明": "由 ENGAGEMENT_PRIORITY 工具計算排序；人工可於 HITL 覆核調整策略。",
        },
    ]


def render_tool_calculation_explanation(client):
    st.markdown("#### Talk-Walk Gap 與 Engagement Priority 公式說明")
    st.dataframe(pd.DataFrame(tool_calculation_explanation_rows(client)), hide_index=True, width="stretch")


def competitive_landscape_rows():
    return [
        {
            "方案": "人工 ESG 徵信",
            "優點": "判斷脈絡完整、責任歸屬清楚",
            "缺點": "逐案蒐集耗時、半年重評負擔高、跨案一致性較難控管",
            "適用情境": "高風險授信與例外案件最終判斷",
        },
        {
            "方案": "Excel / RPA",
            "優點": "導入快、可處理固定格式報表",
            "缺點": "非結構化新聞與報告書摘要能力弱，資料缺口與來源治理需另行設計",
            "適用情境": "固定欄位彙整、例行報表產製",
        },
        {
            "方案": "外部 ESG 資料商",
            "優點": "覆蓋廣、可快速取得外部評等與爭議資料",
            "缺點": "黑箱分數難解釋，未必貼合銀行授信流程與 HITL 稽核需求",
            "適用情境": "外部 benchmark 與資料補強",
        },
        {
            "方案": "本系統 POC",
            "優點": "串接 PCAF、Talk-Walk Gap、議合包、HITL 與 Audit Trail，強調工具計算與可追溯",
            "缺點": "仍需正式資料串接、模型驗證、權限控管與法遵審查",
            "適用情境": "銀行 ESG 徵信與議合流程的 AI-assisted 概念驗證",
        },
    ]


def cost_benefit_risk_rows():
    return [
        {
            "項目": "七大類 ESG 徵信資料整理",
            "人工工時": "3-4 小時 / 案",
            "AI-assisted 工時": "約 20-30 分鐘初稿 + 人工覆核",
            "主要風險": "來源標籤誤導、資料更新落差",
            "控制措施": "示意來源標籤明示、正式導入需 API log、來源版本與 HITL 覆核",
        },
        {
            "項目": "PCAF / EVIC / 融資排放計算",
            "人工工時": "30-60 分鐘 / 案",
            "AI-assisted 工時": "工具即時計算，人工抽核",
            "主要風險": "排放邊界或 EVIC 欄位錯置",
            "控制措施": "PCAF_CALCULATOR 欄位檢核、缺值回傳 NEED_HUMAN_REVIEW、DQ 分級",
        },
        {
            "項目": "議合包與貸後追蹤移交",
            "人工工時": "2-3 小時 / 案",
            "AI-assisted 工時": "約 15-30 分鐘初稿 + HITL 決策",
            "主要風險": "AI 語氣被誤解為授信核定",
            "控制措施": "Step 5 HITL checkpoint、Step 6 未核准前僅列預計呼叫工具、Audit Trail 留痕",
        },
    ]


def render_commercial_context_blocks():
    st.markdown("### Competitive Landscape")
    st.markdown(
        """
        <div class="section-card">
            <div class="section-heading"><h3>競品與替代方案比較</h3><span class="status-chip">POC 定位</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(pd.DataFrame(competitive_landscape_rows()), hide_index=True, width="stretch")

    st.markdown("### Cost-benefit & Risk")
    st.markdown(
        """
        <div class="section-card">
            <div class="section-heading"><h3>工時效益、主要風險與控制措施</h3><span class="status-chip">Governance</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(pd.DataFrame(cost_benefit_risk_rows()), hide_index=True, width="stretch")


def pcaf_calculation_rows(client):
    pcaf = calculate_pcaf_financed_emissions(client)
    if pcaf["status"] != "OK":
        return [
            {"項目": "示意融資暴險", "值": format_number(client["exposure_e_twd"], " 億元")},
            {"項目": "EVIC", "值": "資料不足 / 待補件"},
            {"項目": "歸因係數", "值": "需以產業別、營收或排放係數估算"},
            {"項目": "Scope 1+2 排放量", "值": "未揭露"},
            {"項目": "融資排放", "值": "需以產業別、營收或排放係數估算"},
            {"項目": "PCAF DQ", "值": f"{client.get('pcaf_dq', 5)}/5"},
            {"項目": "DQ 說明", "值": "中小企業未揭露排放資料，僅標示資料缺口，不自動編造排放數字。"},
        ]
    return [
        {"項目": "示意融資暴險", "值": format_number(client["exposure_e_twd"], " 億元")},
        {"項目": "EVIC", "值": format_number(client["company_value_e_twd"], " 億元")},
        {"項目": "歸因係數", "值": f"{pcaf['attribution_factor']:.4f}"},
        {"項目": "Scope 1+2 排放量", "值": f"{client['annual_emissions_tco2e']:,} tCO2e"},
        {"項目": "融資排放", "值": f"{pcaf['financed_emissions_tco2e']:,} tCO2e"},
        {"項目": "PCAF DQ", "值": f"{pcaf['pcaf_dq']}/5"},
        {"項目": "DQ 說明", "值": "部分排放資料來自永續報告書與估算資料，尚待第三方查證或補件確認。"},
    ]


def render_pcaf_visual_ratio(client, pcaf):
    if pcaf["status"] != "OK":
        st.markdown(
            """
            <div class="pcaf-visual-card">
                <div class="label">PCAF visual check</div>
                <div class="note">資料不足，無法呈現歸因係數比例條；請先補齊 EVIC 與 Scope 1+2 排放量。</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    attribution = pcaf["attribution_factor"]
    visual_width = min(max(attribution * 100, 1.2), 100)
    st.markdown(
        f"""
        <div class="pcaf-visual-card">
            <div class="label">PCAF Attribution Factor</div>
            <div class="pcaf-visual-grid">
                <div class="pcaf-mini-card">
                    <span class="metric-note">示意融資暴險</span>
                    <b>{format_number(client['exposure_e_twd'], ' 億元')}</b>
                </div>
                <div class="pcaf-mini-card">
                    <span class="metric-note">EVIC</span>
                    <b>{format_number(client['company_value_e_twd'], ' 億元')}</b>
                </div>
                <div class="pcaf-mini-card">
                    <span class="metric-note">融資排放</span>
                    <b>{pcaf['financed_emissions_tco2e']:,} tCO2e</b>
                </div>
            </div>
            <div class="progress-track" aria-label="Attribution factor">
                <div class="progress-fill" style="width:{visual_width:.2f}%; background:{CHART_GREEN};"></div>
            </div>
            <div class="note">歸因係數 = {client['exposure_e_twd']:,} / {client['company_value_e_twd']:,} = {attribution:.4f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def normalize_hitl_result(hitl_result):
    if hitl_result in HITL_STATUS_LABELS:
        return hitl_summary_label(hitl_result)
    if not hitl_result:
        return "待覆核"
    if "退回" in hitl_result:
        return "退回補件"
    if "核准" in hitl_result or hitl_result == "Passed":
        return "已核准議合"
    return "待覆核"


def build_esg_credit_summary(client, hitl_status="pending"):
    risk_label, _ = calculate_risk_level(client)
    pcaf = calculate_pcaf_financed_emissions(client)
    talk_walk = calculate_talk_walk_gap(client)
    priority = calculate_engagement_priority(client)

    if pcaf["status"] == "OK":
        financed_emissions = f"{pcaf['financed_emissions_tco2e']:,} tCO2e"
        pcaf_dq = f"{pcaf['pcaf_dq']}/5"
    else:
        financed_emissions = "NEED_HUMAN_REVIEW"
        pcaf_dq = f"{client.get('pcaf_dq', 5)}/5"

    if talk_walk["status"] == "OK":
        talk_walk_gap = f"{talk_walk['gap']:.2f} {talk_walk['label']}"
    else:
        talk_walk_gap = "NEED_HUMAN_REVIEW"

    if priority["status"] == "OK":
        ranking = rank_portfolio()
        rank = next(i + 1 for i, item in enumerate(ranking) if item["name"] == client["name"])
        engagement_rank = f"第 {rank} 名"
    else:
        engagement_rank = "NEED_HUMAN_REVIEW"

    return [
        {"項目": "客戶", "結果": display_client_name(client["name"])},
        {"項目": "產業", "結果": client["industry"]},
        {"項目": "ESG 風險等級", "結果": risk_label},
        {"項目": "PCAF 融資排放", "結果": financed_emissions},
        {"項目": "PCAF DQ", "結果": pcaf_dq},
        {"項目": "Talk-Walk Gap", "結果": talk_walk_gap},
        {"項目": "議合優先排名", "結果": engagement_rank},
        {"項目": "建議議合方式", "結果": client["engagement_package"]["engagement_method"]},
        {"項目": "SBT / SLL 路線圖", "結果": sbt_route_summary(client)},
        {"項目": "HITL 覆核結論", "結果": normalize_hitl_result(hitl_status)},
        {"項目": "下次重評時間", "結果": next_reassessment_date()},
    ]


def monitoring_reassessment_note(date_text):
    return (
        f"下次自動重評時間：{date_text}\n"
        "來源：MONITORING_SCHEDULER 工具計算；系統每季自動重評，不需人工重新蒐集。"
    )


def render_esg_credit_summary(client):
    st.markdown("<div class='summary-card'><b>📋 AI 輔助 ESG 徵信摘要</b></div>", unsafe_allow_html=True)
    hitl_status = st.session_state.get("hitl_status", "pending")
    st.dataframe(pd.DataFrame(build_esg_credit_summary(client, hitl_status)), hide_index=True, width="stretch")
    st.caption(CREDIT_SUMMARY_DISCLAIMER)


def step1_data_agent(client, lifecycle_placeholder=None):
    step_header(
        "1",
        "Data Agent — 自動蒐集七大類 ESG 徵信資料",
        PAIN_POINTS["1.3.1"],
        lifecycle_placeholder,
        "search_negative_news() / lookup_env_penalties() / build_esg_checklist()",
    )
    run_status(["🔍 呼叫工具 search_negative_news()...", "🏛️ 呼叫工具 lookup_env_penalties()...", "📋 彙整銀行七大類 ESG 檢核表..."])
    st.subheader("負面新聞")
    render_news(search_negative_news(client))
    st.subheader("環境裁罰")
    render_penalties(lookup_env_penalties(client))
    checklist = build_esg_checklist(client)
    st.subheader("銀行七大類 ESG 檢核表")
    st.dataframe(pd.DataFrame(checklist), hide_index=True, width="stretch")
    st.metric("⏱ 工時對比", "AI-assisted：完成", "人工蒐集：3-4 小時")
    add_audit("Step 1 Data Agent", "search_negative_news() / lookup_env_penalties() / build_esg_checklist()", "Google News（示意）、環保裁處資料庫（示意）、永續報告書 p.42 / PCAF資料表（示意）")


def step2_credit_review(client, lifecycle_placeholder=None):
    step_header(
        "2",
        "Credit Review Agent — 20 項 ESG 指標評估",
        PAIN_POINTS["1.3.1_step2"],
        lifecycle_placeholder,
        "score_esg_20_indicators() / calculate_risk_level() / credit_bonus()",
    )
    run_status(["📊 呼叫工具 score_esg_20_indicators()...", "🧮 計算三面向 ESG 風險評分輔助因子...", "🧾 產出徵信覆核摘要..."])
    passed, needs_improvement, missing = count_esg_scores(client)
    m1, m2, m3 = st.columns(3)
    m1.metric("通過", f"{passed} / 20")
    m2.metric("待改善", f"{needs_improvement} / 20" if not missing else f"{missing} / 20 待補件")
    m3.metric("重大缺口", "CBAM、能源管理、污染裁罰、供應鏈管理")
    with st.expander("20 項 ESG 指標完整清單", expanded=False):
        render_esg_indicators(client)
    cols = st.columns(3)
    for col, (label, value) in zip(cols, client["credit_bonus"].items()):
        col.metric(label, f"{value} 分", help="來源：CREDIT_BONUS工具計算")
    if client.get("cbam_exposed"):
        st.markdown("<div class='orange-box'>⚠ CBAM 暴險：銷貨前五大廠商含歐盟成員，須說明影響與因應。</div>", unsafe_allow_html=True)
    risk_label, risk_color = calculate_risk_level(client)
    st.markdown(f"**總體風險等級：<span style='color:{risk_color};'>{risk_label}</span>**", unsafe_allow_html=True)
    add_audit("Step 2 Credit Review", "score_esg_20_indicators() / calculate_risk_level()", "20項ESG指標、CBAM、信用加分規則（示意）")


def step3_talk_walk(client, lifecycle_placeholder=None):
    step_header(
        "3",
        "Talk-Walk Gap Detection — ESG 揭露與實際表現落差偵測",
        "企業 ESG 揭露與實際表現落差缺乏量化偵測工具",
        lifecycle_placeholder,
        "extract_talk_features() / extract_walk_features() / SHAP_EXPLAINER()",
    )
    run_status(["🧠 呼叫工具 extract_talk_features()...", "🚶 呼叫工具 extract_walk_features()...", "📈 計算 Talk-Walk Gap 與 SHAP 驅動因子..."])
    result = calculate_talk_walk_gap(client)
    if result["status"] != "OK":
        st.error("資料不足，無法可靠計算 Talk-Walk Gap。系統不推測、不自動產生 greenwashing risk score。")
        render_talk_walk_gap_card(result)
        st.caption(TALK_WALK_DISCLAIMER)
        add_audit("Step 3 Talk-Walk Gap", "calculate_talk_walk_gap()", "缺資料不臆測", "Required")
        return
    metric_cols = st.columns([1, 2])
    with metric_cols[0]:
        render_talk_walk_gap_card(result)
    combined = {f"Talk｜{k}": v for k, v in client["talk_features"].items()}
    combined.update({f"Walk｜{k}": v for k, v in client["walk_features"].items()})
    with metric_cols[1]:
        bar_chart("Talk 特徵 vs Walk 特徵", combined)
    shap_values = {item["feature"]: item["value"] for item in client["shap_top5"]}
    bar_chart("SHAP 前5大驅動因子（紅色推高 / 藍色推低）", shap_values, positive_negative=True)
    st.caption(TALK_WALK_DISCLAIMER)
    add_audit("Step 3 Talk-Walk Gap", "calculate_talk_walk_gap() / SHAP_EXPLAINER()", "永續報告書、外部ESG評等、新聞事件（示意）")


def step4_engagement(client, lifecycle_placeholder=None):
    step_header(
        "4",
        "Engagement Agent — 依銀行議合三步驟產出議合包",
        PAIN_POINTS["1.3.2"],
        lifecycle_placeholder,
        STEP4_ENGAGEMENT_TOOLS,
    )
    run_status(["🧮 呼叫工具 PCAF_CALCULATOR()...", "🏁 呼叫工具 ENGAGEMENT_PRIORITY()...", "📝 產出銀行三步驟議合包..."])
    pcaf = calculate_pcaf_financed_emissions(client)
    if pcaf["status"] != "OK":
        st.error("PCAF 無法計算：NEED_HUMAN_REVIEW")
        c1, c2, c3 = st.columns(3)
        c1.metric("歸因係數", "NEED_HUMAN_REVIEW", help="缺 EVIC 或排放資料")
        c2.metric("融資排放", "NEED_HUMAN_REVIEW", help="缺資料不自動估算")
        c3.metric("PCAF DQ", f"{client.get('pcaf_dq', 5)}/5")
        render_pcaf_formula_note()
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("歸因係數", f"{pcaf['attribution_factor']:.4f}", help="暴險 / 公司價值；來源：PCAF_CALCULATOR工具計算")
        c2.metric("融資排放", f"{pcaf['financed_emissions_tco2e']:,} tCO2e", help="歸因係數 × 年排放；來源：PCAF_CALCULATOR工具計算")
        c3.metric("PCAF DQ", f"{pcaf['pcaf_dq']}/5", help="來源：PCAF資料品質規則（示意）")
        render_pcaf_formula_note()
    priority = calculate_engagement_priority(client)
    if priority["status"] == "OK":
        ranking = rank_portfolio()
        rank = next(i + 1 for i, item in enumerate(ranking) if item["name"] == client["name"])
        st.metric("優先議合分數與排名", f"{priority['priority_score']} 分｜第 {rank} 名", priority["rank_reason"], help=priority["source_note"])
        if priority["policy_downweight"]:
            st.info("政策性投資：排序時已降權，展示排除/降權邏輯。")
    else:
        st.warning(f"優先議合分數：NEED_HUMAN_REVIEW｜{priority['rank_reason']}")
    package = client["engagement_package"]
    with st.expander("議合包：對應銀行投融資議合三步驟", expanded=True):
        st.markdown("#### 【Step 1 議合目標】客戶 ESG 現況摘要 + 議合目標")
        st.write(package["current_summary"])
        st.write(package["gap_analysis"])
        st.markdown("#### 【Step 2 議合策略】建議議合方式 + 對話問題 + SLL")
        st.write(f"建議方式：**{package['engagement_method']}**")
        for question in package["dialogue_questions"]:
            st.write(question)
        st.info(package["sll_suggestion"])
        st.markdown("#### 【Step 3 追蹤 KPI】移交 Post-loan Monitoring Agent")
        st.dataframe(pd.DataFrame(package["tracking_kpis"]), hide_index=True, width="stretch")
    st.metric("⏱ 工時對比", "AI-assisted：完成", "人工議合準備：2-3 小時")
    add_audit("Step 4 Engagement", STEP4_ENGAGEMENT_TOOLS, "PCAF Part A、授信政策、SBT路線圖、議合三步驟（示意）")


def step5_hitl(client, lifecycle_placeholder=None):
    step_header(
        "5",
        "HITL Checkpoint — 人工覆核",
        "設計原則：高風險案件需人工覆核",
        lifecycle_placeholder,
        "human_checkpoint() / risk_policy_gate() / reviewer_action()",
        "HITL Checkpoint 已觸發｜等待徵審人員決策",
        "Step 1-4 已完成資料整理與工具計算；目前停在人工覆核關卡。",
    )
    trigger, reason = needs_hitl(client)
    if trigger:
        st.markdown(
            f"""
            <div class='red-box'>
                <b>觸發 HITL Checkpoint：</b><br>{reason}<br><br>
                <b>所有高風險案件強制人工覆核，AI 不自動放行。</b>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        if c1.button("✅ 核准議合並移交貸後追蹤", key=f"approve_{client['ticker']}"):
            st.session_state.hitl_status = "approved"
            add_audit("Step 5 HITL", "human_checkpoint()", reason, "核准議合並移交貸後追蹤", "徵審人員", "Human approved")
            st.rerun()
        if c2.button("🔄 退回補件", key=f"return_{client['ticker']}"):
            st.session_state.hitl_status = "returned"
            add_audit("Step 5 HITL", "human_checkpoint()", reason, "退回補件", "徵審人員", "Need supplement")
            st.rerun()
        status = st.session_state.get("hitl_status", "pending")
        if status == "approved":
            st.success("人工覆核結果：已核准議合並移交貸後追蹤")
        elif status == "returned":
            st.warning("人工覆核結果：退回補件")
        else:
            st.warning("請由徵審人員按鈕確認後，系統才會移交貸後追蹤。")
            add_audit("Step 5 HITL", "human_checkpoint()", reason, "Pending", "徵審人員", "Pending review")
    else:
        st.markdown("<div class='blue-box'>低風險案件：進入一般追蹤。</div>", unsafe_allow_html=True)
        st.session_state.hitl_status = "approved"
        add_audit("Step 5 HITL", "human_checkpoint()", "低風險一般追蹤", "Passed", "徵審人員", "Human approved")


def step6_monitoring(client, lifecycle_placeholder=None):
    view = monitoring_view_for_status(st.session_state.get("hitl_status", "pending"), client)
    status_text = "Monitoring 已啟動" if view["mode"] == "full" else "尚未啟動｜待 HITL 核准後移交貸後追蹤"
    tools_text = STEP6_MONITORING_TOOLS if view["mode"] == "full" else view.get("tools_label", f"預計呼叫工具：{STEP6_MONITORING_TOOLS}")
    work_status = (
        "貸後追蹤排程與監控工具已啟動。"
        if view["mode"] == "full"
        else "人工覆核尚未核准，系統不建立貸後追蹤排程。"
    )
    step_header(
        "6",
        "Post-loan Monitoring Agent — 設定貸後追蹤",
        PAIN_POINTS["1.3.3"],
        lifecycle_placeholder,
        tools_text,
        status_text,
        work_status,
        6 if view["mode"] == "full" else 5,
    )
    if view["mode"] == "blocked":
        st.info(view["message"])
        return
    if view["mode"] == "supplement":
        st.warning(view["message"])
        st.markdown("#### 需補件清單")
        st.dataframe(pd.DataFrame({"補件項目": view["items"]}), hide_index=True, width="stretch")
        return
    run_status(["📅 建立季度重評排程...", "🚨 設定負面事件與SLL履約偵測...", "📉 呼叫工具 SBT_PATHWAY_TRACKER() / TRANSITION_GAP_CHART()..."])
    milestones = pd.DataFrame(client["engagement_package"]["tracking_kpis"])
    milestones["監控工具"] = ["KPI_TRACKER", "SBT_PATHWAY_TRACKER", "TRANSITION_GAP_CHART"][: len(milestones)]
    st.dataframe(milestones, hide_index=True, width="stretch")
    st.subheader("SBT 貸後追蹤減碳路線圖")
    render_post_loan_sbt_pathway_chart()
    st.subheader("異常事件偵測設定")
    st.write("- 新增環保裁罰或重大負面新聞 → 48小時內通知 RM 與徵審主管")
    st.write("- SLL KPI 未達標或資料未補件 → 升級議合強度或調整授信條件")
    st.write("- PCAF DQ 降級或缺資料 → 回傳 NEED_HUMAN_REVIEW")
    reassessment_date = next_reassessment_date()
    reassessment_note = monitoring_reassessment_note(reassessment_date)
    st.markdown(
        f"""
        <div class="risk-card blue">
            <div class="risk-label">{reassessment_note.splitlines()[0]}</div>
            <div class="risk-detail">{reassessment_note.splitlines()[1]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    add_audit("Step 6 Post-loan Monitoring", STEP6_MONITORING_TOOLS, "貸後追蹤考核表、SBT路徑、新聞事件（示意）", "Scheduled", "AI Agent", "Monitoring scheduled")


def audit_trail():
    st.markdown(
        """
        <div class="section-card">
            <div class="section-heading"><h3>Audit Trail 稽核軌跡</h3><span class="status-chip">可追溯</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not st.session_state.audit:
        st.info("啟動 Agent 後將顯示逐步紀錄。")
    else:
        columns = ["時間戳", "步驟", "工具名", "來源", "執行者", "資料版本", "覆核狀態"]
        st.dataframe(pd.DataFrame(st.session_state.audit)[columns], hide_index=True, width="stretch")


def initialize_session_state():
    if "audit" not in st.session_state:
        st.session_state.audit = []
    if "hitl_status" not in st.session_state:
        st.session_state.hitl_status = "pending"
    if "workflow_started" not in st.session_state:
        st.session_state.workflow_started = False
    if "run_started" not in st.session_state:
        st.session_state.run_started = st.session_state.workflow_started
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0
    if "selected_client" not in st.session_state:
        st.session_state.selected_client = None
    if "audit_status" not in st.session_state:
        st.session_state.audit_status = "Not started"


def sync_selected_client(selected_name, lifecycle_placeholder):
    if st.session_state.selected_client is None:
        st.session_state.selected_client = selected_name
    elif st.session_state.selected_client != selected_name:
        st.session_state.selected_client = selected_name
        st.session_state.workflow_started = False
        st.session_state.run_started = False
        st.session_state.hitl_status = "pending"
        st.session_state.current_step = 0
        st.session_state.audit = []
        st.session_state.audit_status = "Not started"
        render_lifecycle_sidebar(lifecycle_placeholder)


def start_workflow_if_requested(start_clicked, lifecycle_placeholder):
    if start_clicked:
        st.session_state.audit = []
        st.session_state.current_step = 0
        st.session_state.hitl_status = "pending"
        st.session_state.audit_status = "Pending review"
        render_lifecycle_sidebar(lifecycle_placeholder)
        st.session_state.workflow_started = True
        st.session_state.run_started = True


def render_workflow_linear(client, lifecycle_placeholder):
    st.markdown("<div class='dashboard-section-title'>Agent 工作流程</div>", unsafe_allow_html=True)
    if not st.session_state.workflow_started:
        return

    steps = [
        ("Step 1/6｜Data Agent", step1_data_agent),
        ("Step 2/6｜Credit Review Agent", step2_credit_review),
        ("Step 3/6｜Talk-Walk Gap Detection", step3_talk_walk),
        ("Step 4/6｜Engagement Agent", step4_engagement),
        ("Step 5/6｜HITL Checkpoint", step5_hitl),
        ("Step 6/6｜Post-loan Monitoring Agent", step6_monitoring),
    ]
    for label, renderer in steps:
        with st.status(label, expanded=True) as status:
            renderer(client, lifecycle_placeholder)
            status.update(label=f"{label}｜已展開", state="complete", expanded=True)


def render_dashboard_disclaimer():
    st.caption(DASHBOARD_DISCLAIMER)


def main():
    page_setup()
    initialize_session_state()
    lifecycle_placeholder = sidebar()

    hero_section()
    render_pain_intro()

    current_name = st.session_state.get("selected_client")
    if current_name is None:
        current_index = default_client_index()
    else:
        current_index = next(
            (idx for idx, item in enumerate(DEMO_PORTFOLIO) if item["name"] == current_name),
            default_client_index(),
        )
    selector_col, card_col = st.columns([2, 1])
    with selector_col:
        selected_name = st.selectbox(
            "選擇示意企業",
            [client["name"] for client in DEMO_PORTFOLIO],
            index=current_index,
        )
    sync_selected_client(selected_name, lifecycle_placeholder)
    client = next(item for item in DEMO_PORTFOLIO if item["name"] == st.session_state.selected_client)
    with card_col:
        company_card(client)

    start_clicked = st.button("▶ 啟動 Agent 徵信與議合流程", type="primary", use_container_width=True)
    start_workflow_if_requested(start_clicked, lifecycle_placeholder)
    st.caption("示意關鍵數據：本 demo 假設 899 戶高氣候轉型風險產業客戶達成初步議合，覆蓋率約 87.5%；非真實銀行內部資料。")

    if st.session_state.workflow_started:
        render_workflow_linear(client, lifecycle_placeholder)
        render_esg_credit_summary(client)
    audit_trail()
    render_dashboard_disclaimer()


if __name__ == "__main__":
    main()
