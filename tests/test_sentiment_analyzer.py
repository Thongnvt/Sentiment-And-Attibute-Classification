import pytest
from sentiment_analyzer import SentimentAnalyzer

@pytest.fixture
def analyzer():
    return SentimentAnalyzer()

def test_sentiment_analysis(analyzer):
    # Test positive sentiment
    result = analyzer.analyze("I absolutely love this product!")
    assert result["sentiment"] == "positive"
    assert result["confidence"] > 0.5
    
    # Test negative sentiment
    result = analyzer.analyze("This is the worst experience ever.")
    assert result["sentiment"] == "negative"
    assert result["confidence"] > 0.5
    
    # Test neutral sentiment
    result = analyzer.analyze("The weather is cloudy today.")
    assert result["sentiment"] == "neutral"
    assert result["confidence"] > 0.5

def test_comparison_analysis(analyzer):
    # Test comparison between objects
    result = analyzer.analyze("The iPhone is faster but more expensive than the Samsung.")
    assert "comparison" in result
    assert result["comparison"]["object1"] == "iPhone"
    assert result["comparison"]["object2"] == "Samsung"
    assert "attributes" in result["comparison"]

def test_empty_input(analyzer):
    # Test empty input
    with pytest.raises(Exception):
        analyzer.analyze("")

def test_special_characters(analyzer):
    # Test text with special characters
    result = analyzer.analyze("This is amazing!!! 😊")
    assert result["sentiment"] == "positive"
    assert result["confidence"] > 0.5 