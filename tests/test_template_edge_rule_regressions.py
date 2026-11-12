from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TemplateEdgeRuleRegressionTests(unittest.TestCase):
    def test_merged_no_applicant_placeholder_must_not_be_restructured(self):
        text = (ROOT / "rules" / "word-template.md").read_text(encoding="utf-8")
        self.assertIn("不得為填入欄位而自行取消合併、拆格或重建資料列", text)
        self.assertIn("其他可映射正式範本照常填入", text)

    def test_copied_sheet_self_reference_is_verified_without_formula_rewrite(self):
        text = (ROOT / "rules" / "template-profile.md").read_text(encoding="utf-8")
        self.assertIn("只允許把來源頁名改成新頁名，不得改變公式邏輯", text)
        self.assertIn("不再指向模板頁、來源頁或其他申請人頁", text)


if __name__ == "__main__":
    unittest.main()
