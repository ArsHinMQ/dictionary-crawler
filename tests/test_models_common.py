from dict_crawler.models.common import CEFRLevel


def test_cefr_levels():
    assert CEFRLevel.A1.value == "A1"
    assert CEFRLevel.A2.value == "A2"
    assert CEFRLevel.B1.value == "B1"
    assert CEFRLevel.B2.value == "B2"
    assert CEFRLevel.C1.value == "C1"
    assert CEFRLevel.C2.value == "C2"


def test_cefr_level_from_value():
    assert CEFRLevel("A1") == CEFRLevel.A1
    assert CEFRLevel("C2") == CEFRLevel.C2


def test_cefr_level_invalid():
    try:
        CEFRLevel("D1")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
