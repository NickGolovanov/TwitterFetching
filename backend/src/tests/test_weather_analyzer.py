import pytest
import torch
from src.database.ai_weather_analyzer import WeatherAnalyzer


@pytest.fixture
def weather_analyzer():
    return WeatherAnalyzer()


def test_initialization(weather_analyzer):
    assert weather_analyzer.device in ["cuda", "cpu"]
    assert weather_analyzer.model is not None
    assert weather_analyzer.tokenizer is not None
    assert len(weather_analyzer.weather_types) > 0
    assert len(weather_analyzer.severity_modifiers) > 0


def test_basic_weather_analysis_english(weather_analyzer):
    text = "There is a severe thunderstorm approaching."
    result = weather_analyzer.analyze_weather_text(text)

    assert result["weather_type"] == "thunderstorm"
    assert result["severity_score"] > 9  # Base severity (9) + modifier for "severe"
    assert result["severity_category"] == "extreme"
    assert result["language"] == "english"
    assert isinstance(result["explanation"], str)
    assert len(result["all_detected_types"]) > 0


def test_basic_weather_analysis_dutch(weather_analyzer):
    text = "Er komt een zware onweersbui aan."
    result = weather_analyzer.analyze_weather_text(text)

    assert result["weather_type"] == "onweer"
    assert result["severity_score"] > 9  # Base severity (9) + modifier for "zware"
    assert result["severity_category"] == "extreme"
    assert result["language"] == "dutch"
    assert isinstance(result["explanation"], str)


def test_multiple_weather_conditions(weather_analyzer):
    text = "Heavy rain and strong wind with occasional thunder."
    result = weather_analyzer.analyze_weather_text(text)

    assert result["weather_type"] in ["thunder", "heavy rain", "strong wind"]
    assert len(result["all_detected_types"]) >= 3
    assert result["severity_score"] > 0
    assert isinstance(result["explanation"], str)


def test_unknown_weather(weather_analyzer):
    text = "An open-source YouTube Music client that’s lightweight, ad-free, and fully customizable."
    result = weather_analyzer.analyze_weather_text(text)

    assert result["weather_type"] == "unknown"
    assert result["severity_score"] == 0
    assert result["severity_category"] == "unknown"


def test_text_length_limit(weather_analyzer):
    long_text = "thunderstorm " * 100
    result = weather_analyzer.analyze_weather_text(long_text)

    assert len(long_text) > 280  # Original text longer than limit
    assert result["weather_type"] == "thunderstorm"  # Still detects weather
    assert result["severity_score"] > 0


def test_terms_are_close(weather_analyzer):
    text = "severe thunderstorm"
    assert weather_analyzer._terms_are_close(
        text, "severe", "thunderstorm", max_distance=5
    )

    text = "severe weather with thunderstorm later today"
    assert not weather_analyzer._terms_are_close(
        text, "severe", "thunderstorm", max_distance=2
    )
    assert weather_analyzer._terms_are_close(
        text, "severe", "thunderstorm", max_distance=5
    )


def test_severity_categories(weather_analyzer):
    assert weather_analyzer._get_severity_category(9) == "extreme"
    assert weather_analyzer._get_severity_category(7) == "high"
    assert weather_analyzer._get_severity_category(4) == "moderate"
    assert weather_analyzer._get_severity_category(2) == "low"
    assert weather_analyzer._get_severity_category(0) == "unknown"


def test_contextual_severity_assessment(weather_analyzer):
    text = "The devastating hurricane caused widespread destruction."
    result = weather_analyzer.analyze_weather_text(text)

    assert result["severity_score"] >= weather_analyzer.weather_types["hurricane"]
    assert result["severity_category"] == "extreme"


@pytest.mark.parametrize(
    "text,expected_type,min_severity",
    [
        ("A mild drizzle is falling", "drizzle", 0),
        ("Extreme hurricane conditions", "hurricane", 9),
        ("Light snow is expected", "snow", 0),
        ("Catastrophic flooding reported", "flood", 8),
    ],
)
def test_various_weather_conditions(
    weather_analyzer, text, expected_type, min_severity
):
    result = weather_analyzer.analyze_weather_text(text)
    assert result["weather_type"] == expected_type
    assert result["severity_score"] >= min_severity
