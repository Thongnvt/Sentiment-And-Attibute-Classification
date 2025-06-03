import pytest
from sentiment_analyzer import SentimentAnalyzer
import os

# Skip tests if API key is not present
skip_if_no_api_key = pytest.mark.skipif(
    not os.getenv('ANTHROPIC_API_KEY'),
    reason="Anthropic API key not found in environment variables"
)

@pytest.fixture
def analyzer():
    print(f"ANTHROPIC_API_KEY present: {bool(os.getenv('ANTHROPIC_API_KEY'))}")
    return SentimentAnalyzer()

@skip_if_no_api_key
def test_sentiment_analysis(analyzer):
    # Test positive sentiment
    result = analyzer.analyze("I absolutely love this product!")
    assert result["sentiment"] == "positive"
    assert result["confidence"] > 0.5
    
    # Test negative sentiment
    result = analyzer.analyze("The experience was terrible.")
    assert result["sentiment"] == "negative"
    assert result["confidence"] > 0.5
    
    # Test neutral sentiment
    result = analyzer.analyze("The weather is cloudy today.")
    assert result["sentiment"] == "neutral"
    assert result["confidence"] > 0.5

@skip_if_no_api_key
def test_comparison_analysis(analyzer):
    # Test comparison between objects
    result = analyzer.analyze("The iPhone is faster but more expensive than the Samsung.")
    assert "comparison" in result
    assert result["comparison"]["object1"] == "iPhone"
    assert result["comparison"]["object2"] == "Samsung"
    assert "attributes" in result["comparison"]

@skip_if_no_api_key
def test_empty_input(analyzer):
    # Test empty input
    with pytest.raises(Exception):
        analyzer.analyze("")

@skip_if_no_api_key
def test_special_characters(analyzer):
    # Test text with special characters
    result = analyzer.analyze("This is amazing!!! 😊")
    assert result["sentiment"] == "positive"
    assert result["confidence"] > 0.5 