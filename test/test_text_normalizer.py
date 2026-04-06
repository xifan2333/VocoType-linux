from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


MODULE_PATH = Path(__file__).resolve().parents[1] / "app" / "text_normalizer.py"
SPEC = importlib.util.spec_from_file_location("vocotype_text_normalizer", MODULE_PATH)
assert SPEC and SPEC.loader
text_normalizer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = text_normalizer
SPEC.loader.exec_module(text_normalizer)


def test_normalize_dates_and_basic_counts():
    assert (
        text_normalizer.normalize_chinese_numbers("二零二六年四月五号我跑了三百二十米")
        == "2026年4月5号我跑了320米"
    )


def test_normalize_decimals_percent_and_ordinals():
    assert (
        text_normalizer.normalize_chinese_numbers("第三十二章增长百分之三点五")
        == "第32章增长3.5%"
    )


def test_normalize_spoken_short_numbers():
    assert text_normalizer.normalize_chinese_numbers("一万二和一千二百三") == "12000和1230"


def test_normalize_ranges_and_time_context():
    assert text_normalizer.normalize_chinese_numbers("三到五天后两点半开始") == "3到5天后2点半开始"


def test_preserve_approximate_phrases():
    assert text_normalizer.normalize_chinese_numbers("七八个三五成群十五六岁") == "七八个三五成群十五六岁"


def test_preserve_non_numeric_phrase_with_dian():
    assert text_normalizer.normalize_chinese_numbers("我一点也不困") == "我一点也不困"


def test_preserve_yixia_phrase():
    assert (
        text_normalizer.normalize_chinese_numbers("阅读这个文档，了解一下项目")
        == "阅读这个文档，了解一下项目"
    )


def test_preserve_approximate_xiasi_phrase():
    assert (
        text_normalizer.normalize_chinese_numbers("一不小心蹭了三四下车")
        == "一不小心蹭了三四下车"
    )
