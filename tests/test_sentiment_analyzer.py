import pytest
from sentiment_analyzer import SentimentAnalyzer
import os
import json

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
    with pytest.raises(ValueError):
        analyzer.analyze("")
    
    # Test whitespace-only input
    with pytest.raises(ValueError):
        analyzer.analyze("   ")

@skip_if_no_api_key
def test_special_characters(analyzer):
    # Test text with special characters
    result = analyzer.analyze("This is amazing!!! 😊")
    assert result["sentiment"] == "positive"
    assert result["confidence"] > 0.5

@skip_if_no_api_key
def test_parse_response(analyzer):
    # Test parsing JSON response with markdown
    json_with_markdown = """```json
    {
        "sentiment": "positive",
        "confidence": 0.9,
        "implications": ["User is satisfied"],
        "explanation": "Text contains positive words"
    }
    ```"""
    result = analyzer._parse_response(json_with_markdown)
    assert result["sentiment"] == "positive"
    assert result["confidence"] == 0.9

    # Test parsing invalid JSON
    result = analyzer._parse_response("invalid json")
    assert result["sentiment"] == "error"
    assert result["confidence"] == 0.0

@skip_if_no_api_key
def test_comparison_parse_response(analyzer):
    # Test parsing comparison response
    comparison_json = """{
        "objects_being_compared": [
            {"name": "Product A"},
            {"name": "Product B"}
        ],
        "attributes": {
            "Product A": {
                "explicit_attributes": {
                    "price": "high",
                    "quality": "good"
                }
            }
        }
    }"""
    result = analyzer._parse_response(comparison_json)
    assert "comparison" in result
    assert result["comparison"]["object1"] == "Product A"
    assert result["comparison"]["object2"] == "Product B"
    assert "price" in result["comparison"]["attributes"]

@skip_if_no_api_key
def test_mixed_sentiment(analyzer):
    # Test text with mixed sentiment
    result = analyzer.analyze("The food was great but the service was terrible.")
    print("Mixed sentiment result:", result)
    assert "sentiment" in result, f"Result missing 'sentiment' key: {result}"
    assert result["sentiment"] in ["negative", "neutral"], f"Unexpected sentiment: {result['sentiment']}, full result: {result}"
    assert result["confidence"] > 0.5

@skip_if_no_api_key
def test_implications(analyzer):
    # Test text with implications
    result = analyzer.analyze("The movie was interesting, to say the least.")
    assert "implications" in result
    assert isinstance(result["implications"], list) 