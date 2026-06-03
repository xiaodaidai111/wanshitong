import unittest
from unittest.mock import patch

from services.health_score import HealthScoreCalculator


class HealthScoreCalculatorTest(unittest.TestCase):
    def test_qwen_vision_config_accepts_existing_env_names(self):
        with patch.dict(
            "os.environ",
            {
                "DASHSCOPE_API_KEY": "dashscope-key",
                "QWEN_VISION_API_URL": "https://example.com/v1/chat/completions",
                "QWEN_IMAGE_MODEL": "qwen-vl-max",
            },
            clear=True,
        ):
            self.assertEqual(
                HealthScoreCalculator._env_first("QWEN_API_KEY", "DASHSCOPE_API_KEY"),
                "dashscope-key",
            )
            self.assertEqual(
                HealthScoreCalculator._qwen_endpoint(vision=True),
                "https://example.com/v1/chat/completions",
            )
            self.assertEqual(HealthScoreCalculator._qwen_vision_model(), "qwen-vl-max")

    def test_image_analysis_reports_missing_vision_key(self):
        with patch.dict("os.environ", {}, clear=True), patch.object(
            HealthScoreCalculator, "_score_with_llm", return_value=None
        ):
            result = HealthScoreCalculator.analyze_food_from_image(b"fake-image")

        self.assertEqual(result["model"]["vision_source"], "heuristic")
        self.assertEqual(result["model"]["vision_error"], "missing_qwen_or_dashscope_api_key")

    def test_llm_score_overrides_fallback_score(self):
        llm_result = {
            "score": 91,
            "suggestions": ["蛋白质结构较好", "注意控制钠摄入"],
            "source": "deepseek",
        }

        with patch.object(HealthScoreCalculator, "_score_with_llm", return_value=llm_result):
            result = HealthScoreCalculator.analyze_food_from_text(
                "鸡胸肉沙拉",
                {
                    "ingredients": ["鸡胸肉", "生菜", "玉米", "番茄"],
                    "cooking_method": "steamed",
                    "packaging_material": "paper",
                    "food_temperature": "cold",
                },
            )

        self.assertEqual(result["score"], 91)
        self.assertEqual(result["model"]["scoring_source"], "deepseek")
        self.assertIn("蛋白质结构较好", result["suggestions"])

    def test_fallback_score_used_when_llm_unavailable(self):
        with patch.object(HealthScoreCalculator, "_score_with_llm", return_value=None):
            result = HealthScoreCalculator.analyze_food_from_text(
                "炸鸡配米饭",
                {
                    "ingredients": ["鸡肉", "米饭"],
                    "cooking_method": "fried",
                    "packaging_material": "pp",
                    "food_temperature": "hot",
                },
            )

        self.assertEqual(result["model"]["scoring_source"], "heuristic")
        self.assertEqual(result["score"], result["model"]["fallback_score"])

    def test_fallback_score_can_reach_high_range(self):
        with patch.object(HealthScoreCalculator, "_score_with_llm", return_value=None):
            result = HealthScoreCalculator.analyze_food_from_text(
                "steamed chicken salad rice",
                {
                    "ingredients": ["chicken", "salad", "broccoli", "rice"],
                    "portion_grams": 700,
                    "cooking_method": "steamed",
                    "packaging_material": "paper",
                    "food_temperature": "cold",
                    "delivery_time": 20,
                    "safe_time": 40,
                },
            )

        self.assertGreaterEqual(result["score"], 85)
        self.assertEqual(result["model"]["scoring_source"], "heuristic")
        self.assertIn("score_basis", result["model"])

    def test_fallback_score_can_reach_low_range(self):
        with patch.object(HealthScoreCalculator, "_score_with_llm", return_value=None):
            result = HealthScoreCalculator.analyze_food_from_text(
                "deep fried chicken rice",
                {
                    "ingredients": ["chicken", "rice"],
                    "cooking_method": "deep_fried",
                    "packaging_material": "pvc",
                    "food_temperature": "hot",
                    "delivery_time": 90,
                    "safe_time": 40,
                },
            )

        self.assertLessEqual(result["score"], 30)
        self.assertEqual(result["model"]["scoring_source"], "heuristic")
        self.assertGreater(result["model"]["score_basis"]["delivery_penalty"], 0)


if __name__ == "__main__":
    unittest.main()
