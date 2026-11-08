import pytest

from app.ai_errors import AIBadOutput
from app.config import Settings
from app.jobs import JOBS, build_analyze_message, build_classify_message, model_for, pick_label

SETTINGS = Settings(_env_file=None, ai_provider="fake", ai_model_light="small", ai_model_heavy="big")


def test_classify_is_light_and_analyze_is_heavy():
    assert JOBS["classify"].tier == "light"
    assert JOBS["analyze"].tier == "heavy"


def test_model_for_uses_the_tier_from_settings():
    assert model_for(JOBS["classify"], SETTINGS) == "small"
    assert model_for(JOBS["analyze"], SETTINGS) == "big"


def test_pick_label_exact_and_loose():
    labels = ["positive", "negative", "neutral"]
    assert pick_label("negative", labels) == "negative"
    assert pick_label('  "Negative".\n', labels) == "negative"
    assert pick_label("I think it is neutral", labels) == "neutral"


def test_pick_label_rejects_unusable_reply():
    with pytest.raises(AIBadOutput):
        pick_label("I am not sure", ["positive", "negative"])


def test_messages_contain_the_inputs():
    assert "a, b" in build_classify_message("hello", ["a", "b"])
    assert "why?" in build_analyze_message("hello", "why?")
    assert "Question" not in build_analyze_message("hello", None)


def test_pick_label_does_not_match_inside_other_words():
    # "no" is inside "cannot" and "a" is inside "decide", but neither is a whole word.
    with pytest.raises(AIBadOutput):
        pick_label("I cannot decide.", ["no", "a"])
    assert pick_label("The answer is no.", ["yes", "no"]) == "no"
