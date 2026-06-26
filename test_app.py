import unittest
from pathlib import Path

import app
from data import DEMO_PORTFOLIO, ESG_INDICATORS, calculate_pcaf_financed_emissions, calculate_talk_walk_gap


class LifecycleStatusRowsTest(unittest.TestCase):
    def test_marks_completed_items_up_to_current_step(self):
        self.assertTrue(hasattr(app, "lifecycle_status_rows"), "lifecycle_status_rows should exist")

        rows = app.lifecycle_status_rows(3)

        self.assertEqual(
            rows,
            [
                "1. 徵提資料 ✅",
                "2. 徵信調查與實地訪查 ✅",
                "3. ESG 風險評分 ✅",
                "4. 完成徵信報告",
                "5. 徵信覆核 △",
                "HITL 人工覆核中",
                "6. 移交徵審核定 △",
            ],
        )

    def test_no_checkmarks_before_agent_starts(self):
        self.assertTrue(hasattr(app, "lifecycle_status_rows"), "lifecycle_status_rows should exist")

        rows = app.lifecycle_status_rows(0)

        self.assertTrue(all("✅" not in row for row in rows))

    def test_step_one_marks_first_two_lifecycle_items(self):
        rows = app.lifecycle_status_rows(1)

        self.assertEqual(
            rows,
            [
                "1. 徵提資料 ✅",
                "2. 徵信調查與實地訪查 ✅",
                "3. ESG 風險評分",
                "4. 完成徵信報告",
                "5. 徵信覆核 △",
                "HITL 人工覆核中",
                "6. 移交徵審核定 △",
            ],
        )


class DemoContentTest(unittest.TestCase):
    def test_demo_company_names_use_original_names(self):
        expected = [
            "台塑化(示意)",
            "中鋼(示意)",
            "亞泥(示意)",
            "台泥(示意)",
            "中油(示意)",
            "長榮海運(示意)",
            "遠東新(示意)",
            "某精密中小企業(示意)",
        ]

        self.assertEqual([client["name"] for client in DEMO_PORTFOLIO], expected)
        self.assertFalse(hasattr(app, "DISPLAY_NAME_MAP"))

    def test_monitoring_reassessment_note_keeps_source_sentence_together(self):
        text = app.monitoring_reassessment_note("2026-09-21")

        self.assertEqual(
            text,
            "下次自動重評時間：2026-09-21\n"
            "來源：MONITORING_SCHEDULER 工具計算；系統每季自動重評，不需人工重新蒐集。",
        )

    def test_bank_specific_copy_is_generic(self):
        app_source = Path(app.__file__).read_text(encoding="utf-8")
        old_short_name = "台" + "銀"
        old_full_name = "台灣" + "銀行"

        self.assertNotIn(old_short_name, app_source)
        self.assertNotIn(old_full_name, app_source)
        self.assertIn("對應銀行責任授信生命週期", app_source)
        self.assertIn("銀行七大類 ESG 檢核表", app_source)
        self.assertIn("銀行議合三步驟", app_source)

    def test_pain_intro_mentions_lending_stages(self):
        text = app.pain_intro_text()

        for keyword in ["現行痛點", "貸前", "貸中", "貸後", "中小企業", "AI-assisted"]:
            self.assertIn(keyword, text)

    def test_pcaf_formula_note_explains_metrics(self):
        text = app.pcaf_formula_note()

        for keyword in ["歸因係數", "企業價值（EVIC）", "融資排放", "PCAF DQ", "概念驗證"]:
            self.assertIn(keyword, text)

    def test_esg_credit_summary_contains_final_deliverable_rows(self):
        client = next(item for item in DEMO_PORTFOLIO if item["ticker"] == "1102")

        rows = app.build_esg_credit_summary(client, "approved")

        self.assertTrue(hasattr(app, "display_client_name"))
        self.assertEqual(rows[0], {"項目": "客戶", "結果": app.display_client_name(client["name"])})
        labels = [row["項目"] for row in rows]
        self.assertEqual(
            labels,
            [
                "客戶",
                "產業",
                "ESG 風險等級",
                "PCAF 融資排放",
                "PCAF DQ",
                "Talk-Walk Gap",
                "議合優先排名",
                "建議議合方式",
                "SBT / SLL 路線圖",
                "HITL 覆核結論",
                "下次重評時間",
            ],
        )
        self.assertIn("tCO2e", rows[3]["結果"])
        self.assertEqual(rows[8]["結果"], "已建立示意減碳路線圖，待 HITL 覆核後移交貸後追蹤")
        self.assertEqual(rows[9]["結果"], "已核准議合")

    def test_hitl_pending_blocks_full_monitoring(self):
        view = app.monitoring_view_for_status("pending")

        self.assertEqual(view["mode"], "blocked")
        self.assertEqual(view["message"], "尚未啟動｜待 HITL 核准後移交貸後追蹤")
        self.assertIn("預計呼叫工具", view["tools_label"])

    def test_hitl_summary_labels_follow_status(self):
        client = next(item for item in DEMO_PORTFOLIO if item["ticker"] == "1102")

        pending = app.build_esg_credit_summary(client, "pending")
        approved = app.build_esg_credit_summary(client, "approved")
        returned = app.build_esg_credit_summary(client, "returned")

        self.assertEqual(pending[9]["結果"], "待覆核")
        self.assertEqual(approved[9]["結果"], "已核准議合")
        self.assertEqual(returned[9]["結果"], "退回補件")

    def test_returned_status_shows_supplement_list_instead_of_full_monitoring(self):
        view = app.monitoring_view_for_status("returned")

        self.assertEqual(view["mode"], "supplement")
        self.assertEqual(
            view["items"],
            [
                "範疇三盤查邊界與查證狀態",
                "董事會核准之中期減碳目標與時程",
                "CBAM / 主要客戶減碳要求因應資料",
                "高碳製程資本支出與投產時程",
            ],
        )

    def test_approved_status_allows_full_monitoring(self):
        view = app.monitoring_view_for_status("approved")

        self.assertEqual(view["mode"], "full")

    def test_step4_sbt_pathway_preview_uses_oil_demo_values(self):
        client = next(item for item in DEMO_PORTFOLIO if item["ticker"] == "CPC")

        preview = app.sbt_pathway_preview(client)

        self.assertEqual(preview["status"], "OK")
        self.assertEqual(preview["title"], "SBT / SLL KPI 減碳路線圖預覽")
        self.assertEqual(
            preview["rows"],
            [
                {"year": 2024, "label": "Baseline emissions", "emissions_tco2e": 18_000_000},
                {"year": 2026, "label": "2026 target", "emissions_tco2e": 17_100_000},
                {"year": 2027, "label": "2027 target", "emissions_tco2e": 16_200_000},
                {"year": 2030, "label": "2030 target", "emissions_tco2e": 13_500_000},
                {"year": 2050, "label": "Net Zero / near zero pathway", "emissions_tco2e": 0},
            ],
        )

    def test_sme_sbt_pathway_preview_requires_human_review(self):
        client = next(item for item in DEMO_PORTFOLIO if item["ticker"] == "N/A")

        preview = app.sbt_pathway_preview(client)

        self.assertEqual(preview["status"], "NEED_HUMAN_REVIEW")
        self.assertIn("資料不足，尚無法建立可信賴 SBT 減碳路線圖", preview["message"])

    def test_post_loan_monitoring_pathway_contains_three_series(self):
        pathway = app.post_loan_monitoring_pathway()

        self.assertEqual(pathway["years"], [2024, 2025, 2026, 2027, 2030])
        self.assertEqual(pathway["actual_emissions"], [18_000_000, 17_800_000, 17_100_000, None, None])
        self.assertEqual(pathway["sbt_target_pathway"], [18_000_000, 17_550_000, 17_100_000, 16_200_000, 13_500_000])
        self.assertEqual(pathway["industry_transition_pathway"], [18_000_000, 17_700_000, 17_300_000, 16_800_000, 14_500_000])

    def test_audit_toolchains_include_sbt_pathway_tools(self):
        self.assertEqual(
            app.STEP4_ENGAGEMENT_TOOLS,
            "PCAF_CALCULATOR() / ENGAGEMENT_PRIORITY() / package_builder()",
        )
        self.assertEqual(
            app.STEP6_MONITORING_TOOLS,
            "MONITORING_SCHEDULER() / KPI_TRACKER() / SBT_PATHWAY_TRACKER() / TRANSITION_GAP_CHART()",
        )

    def test_workflow_state_labels_are_explicit(self):
        self.assertNotEqual(app.workflow_state(False, "pending"), "not_started")
        self.assertEqual(app.workflow_state(False, "pending"), "READY_TO_START")
        self.assertEqual(app.workflow_state(True, "pending"), "HITL_PENDING")
        self.assertEqual(app.workflow_state(True, "approved"), "approved")
        self.assertEqual(app.workflow_state(True, "returned"), "returned")

    def test_left_lifecycle_uses_support_language_for_credit_approval(self):
        rows = app.lifecycle_status_rows(6)

        self.assertIn("6. 移交徵審核定 △", rows)
        self.assertNotIn("徵信核定 ✅", "\n".join(rows))

    def test_esg_indicator_count_is_20_for_demo_client(self):
        client = next(item for item in DEMO_PORTFOLIO if item["ticker"] == "1102")
        rows = app.esg_indicator_rows(client)

        self.assertEqual(len(rows), 20)
        self.assertEqual(sum(row["結果"] == "✓ 通過" for row in rows), 12)
        self.assertEqual(sum(row["結果"] == "✗ 待改善" for row in rows), 8)

    def test_esg_indicator_labels_match_required_twenty_items(self):
        labels = [label for items in ESG_INDICATORS.values() for label in items]

        self.assertEqual(
            labels,
            [
                "碳排盤查",
                "減碳目標",
                "能源管理",
                "水資源管理",
                "污染裁罰",
                "CBAM因應",
                "氣候風險揭露",
                "廢棄物管理",
                "勞動法規",
                "職安事件",
                "供應鏈管理",
                "人權政策",
                "社區溝通",
                "消費者/客戶權益",
                "董事會治理",
                "資訊揭露",
                "AML/CFT",
                "重大訴訟",
                "誠信經營",
                "外部評鑑/認證",
            ],
        )

    def test_pcaf_financed_emissions_for_demo_client(self):
        client = next(item for item in DEMO_PORTFOLIO if item["ticker"] == "1102")
        pcaf = calculate_pcaf_financed_emissions(client)

        self.assertEqual(pcaf["financed_emissions_tco2e"], 166222)
        self.assertEqual(app.pcaf_calculation_rows(client)[4]["值"], "166,222 tCO2e")

    def test_tool_calculation_explanation_cards_show_weighted_formulas(self):
        client = next(item for item in DEMO_PORTFOLIO if item["ticker"] == "1102")
        rows = app.tool_calculation_explanation_rows(client)

        self.assertEqual(rows[0]["指標"], "Talk-Walk Gap")
        self.assertIn("0.65", rows[0]["計算結果"])
        self.assertIn("Walk 平均", rows[0]["公式"])
        self.assertEqual(rows[1]["指標"], "Engagement Priority")
        self.assertIn("50.2", rows[1]["計算結果"])
        self.assertIn("暴險 35%", rows[1]["公式"])

    def test_ui_keeps_disclaimers_to_three_approved_sentences(self):
        app_source = Path(app.__file__).read_text(encoding="utf-8")
        data_source = Path("data.py").read_text(encoding="utf-8")

        self.assertNotIn("POC_NOTE", app_source)
        self.assertNotIn("MOCK_DATA_DISCLOSURE", app_source)
        self.assertNotIn("示意資料聲明", app_source)
        self.assertNotIn("亞泥示意", app_source + data_source)
        forbidden_mock_label = "Mock source" + " label"
        forbidden_live_api_note = "未即時呼叫" + "外部 API"
        self.assertNotIn(forbidden_mock_label, app_source + data_source)
        self.assertNotIn(forbidden_live_api_note, app_source + data_source)
        self.assertIn("Google News（示意）", app_source + data_source)
        self.assertIn("永續報告書 p.42 / PCAF資料表（示意）", app_source + data_source)
        self.assertEqual(
            app.DASHBOARD_DISCLAIMER,
            "免責聲明：所有企業資料均為示意性假資料，僅供 DSF506A 期末專案概念驗證。",
        )
        self.assertEqual(
            app.TALK_WALK_DISCLAIMER,
            "本模組輸出為輔助訊號（risk signal），非 greenwashing 認定。最終由徵審人員判斷。",
        )
        self.assertEqual(
            app.CREDIT_SUMMARY_DISCLAIMER,
            "本摘要由 AI Agent 自動彙整，所有數值由工具計算並附來源。最終授信決策由徵審人員判斷。",
        )

    def test_competitive_landscape_and_cost_benefit_blocks_exist(self):
        landscape = app.competitive_landscape_rows()
        cost_risk = app.cost_benefit_risk_rows()

        self.assertEqual(
            [row["方案"] for row in landscape],
            ["人工 ESG 徵信", "Excel / RPA", "外部 ESG 資料商", "本系統 POC"],
        )
        self.assertIn("人工工時", cost_risk[0])
        self.assertIn("AI-assisted 工時", cost_risk[0])
        self.assertTrue(any("HITL" in row["控制措施"] for row in cost_risk))

    def test_sme_client_profile_and_gap_branch(self):
        client = next(item for item in DEMO_PORTFOLIO if item["ticker"] == "N/A")

        self.assertEqual(client["name"], "某精密中小企業(示意)")
        self.assertEqual(client["industry"], "製造業")
        self.assertEqual(client["exposure_e_twd"], 8)
        self.assertEqual(calculate_talk_walk_gap(client)["status"], "NEED_HUMAN_REVIEW")
        self.assertEqual(calculate_pcaf_financed_emissions(client)["status"], "NEED_HUMAN_REVIEW")
        self.assertEqual(client["pcaf_dq"], 5)
        summary = app.build_esg_credit_summary(client, "pending")
        self.assertEqual(summary[8]["結果"], "資料不足，需補件後建立")

    def test_sme_returned_status_uses_sme_supplement_list(self):
        client = next(item for item in DEMO_PORTFOLIO if item["ticker"] == "N/A")
        view = app.monitoring_view_for_status("returned", client)

        self.assertEqual(view["mode"], "supplement")
        self.assertEqual(
            view["items"],
            [
                "ESG 自評問卷",
                "最近一年用電量或能源帳單",
                "主要製程與產能資料",
                "溫室氣體盤查規劃",
                "聯徵 ESG 資訊或外部佐證文件",
            ],
        )

    def test_audit_row_contains_governance_fields(self):
        row = app.audit_row("Step 5 HITL", "human_checkpoint", "HITL reason", "徵審人員", "Need supplement")

        self.assertEqual(row["執行者"], "徵審人員")
        self.assertEqual(row["資料版本"], "demo_data_v1.0")
        self.assertEqual(row["覆核狀態"], "Need supplement")

    def test_workflow_renderer_is_linear_without_tabs(self):
        app_source = Path(app.__file__).read_text(encoding="utf-8")

        self.assertIn("def render_workflow_linear", app_source)
        self.assertNotIn("st.tabs", app_source)
        self.assertNotIn("def render_workflow_tabs", app_source)


class DeploymentReadinessTest(unittest.TestCase):
    def test_matplotlib_cache_dir_is_streamlit_cloud_safe(self):
        app_source = Path(app.__file__).read_text(encoding="utf-8")

        self.assertNotIn("/private/tmp", app_source)
        self.assertEqual(app.os.environ.get("MPLCONFIGDIR"), "/tmp/matplotlib")


if __name__ == "__main__":
    unittest.main()
