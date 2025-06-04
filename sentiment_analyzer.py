from typing import Dict, List, Tuple, Optional
from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SentimentAnalyzer:
    def __init__(self):
        # Initialize the LLM with Claude
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0
        )
        
        # Initialize the memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """
        Internal method to analyze sentiment using the LLM
        """
        messages = [
            ("system", """You are a sentiment analysis expert. Your task is to classify text as positive, negative, or neutral.
            
            Rules for classification:
            1. NEGATIVE: Text containing words like 'worst', 'terrible', 'hate', 'awful', 'bad', 'poor', 'disappointing'
            2. POSITIVE: Text containing words like 'love', 'great', 'excellent', 'amazing', 'wonderful', 'best'
            3. NEUTRAL: Text that is factual or contains mixed sentiments
            
            You must strictly follow these rules. If the text contains any negative words, it MUST be classified as negative.
            
            Return a JSON object with these fields:
            - sentiment: "positive", "negative", or "neutral"
            - confidence: number between 0 and 1
            - implications: list of any hidden meanings
            - explanation: brief explanation of your classification"""),
            ("human", f"Analyze this text: {text}")
        ]
        
        response = self.llm.invoke(messages)
        return self._parse_response(response.content)
    
    def _analyze_comparison(self, text: str) -> Dict:
        """
        Internal method to analyze comparisons between objects
        """
        messages = [
            ("system", """You are an expert at analyzing comparisons between objects in text.
            
            When analyzing text, identify:
            1. The objects being compared
            2. Their respective attributes
            3. The comparison relationship
            4. The sentiment towards each object
            
            Return a JSON object with this structure:
            {
                "objects_being_compared": [
                    {"name": "object1_name"},
                    {"name": "object2_name"}
                ],
                "attributes": {
                    "object1_name": {
                        "explicit_attributes": {
                            "attribute1": "value1",
                            "attribute2": "value2"
                        }
                    }
                }
            }"""),
            ("human", f"Analyze this text: {text}")
        ]
        
        response = self.llm.invoke(messages)
        return self._parse_response(response.content)
    
    def _parse_response(self, response: str) -> Dict:
        try:
            # Remove markdown code block markers if present
            if response.startswith('```json'):
                response = response[7:]  # Remove ```json
            if response.endswith('```'):
                response = response[:-3]  # Remove ```
            response = response.strip()
            
            # Parse the JSON response
            parsed_data = json.loads(response)
            
            # For comparison analysis, ensure we have the right structure
            if "objects_being_compared" in parsed_data:
                try:
                    return {
                        "comparison": {
                            "object1": parsed_data["objects_being_compared"][0].get("name", ""),
                            "object2": parsed_data["objects_being_compared"][1].get("name", ""),
                            "attributes": {
                                attr: {
                                    parsed_data["objects_being_compared"][0].get("name", ""): value,
                                    parsed_data["objects_being_compared"][1].get("name", ""): value
                                }
                                for attr, value in parsed_data.get("attributes", {}).get(parsed_data["objects_being_compared"][0].get("name", ""), {}).get("explicit_attributes", {}).items()
                            }
                        }
                    }
                except Exception as e:
                    print(f"Comparison parsing error: {e}, response: {parsed_data}")
                    return {"sentiment": "error", "confidence": 0.0, "explanation": f"Comparison parsing error: {e}"}
            
            # For sentiment analysis, ensure we have the required fields
            if "sentiment" in parsed_data and "confidence" in parsed_data:
                return parsed_data
            else:
                print(f"Warning: LLM response did not contain expected keys. Response: {response}")
                return {"sentiment": "error", "confidence": 0.0, "explanation": "Failed to parse LLM response"}
                
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from LLM response: {response}")
            return {"sentiment": "error", "confidence": 0.0, "explanation": "Invalid JSON response from LLM"}
        except Exception as e:
            print(f"An unexpected error occurred during parsing: {e}, response: {response}")
            return {"sentiment": "error", "confidence": 0.0, "explanation": f"Parsing error: {e}"}
    
    def analyze(self, text: str) -> Dict:
        """
        Main method to analyze text using the LLM
        """
        # Check for empty input
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
            
        # Determine if the text contains a comparison
        comparison_prompt = f"""Does the following text contain a direct comparison between two or more distinct objects/entities?
        Examples of comparisons:
        - "The iPhone is faster than the Samsung"
        - "Product A has better features than Product B"
        - "Company X's revenue is higher than Company Y's"
        
        Examples of non-comparisons:
        - "The food was great but the service was terrible" (mixed sentiment)
        - "I like both options" (general statement)
        - "The movie was interesting, to say the least" (implication)
        
        Text: {text}
        Answer with just 'yes' or 'no'."""
        
        is_comparison = self.llm.invoke(comparison_prompt).content.strip().lower() == 'yes'
        
        if is_comparison:
            return self._analyze_comparison(text)
        else:
            return self._analyze_sentiment(text)

def main():
    # Example usage
    analyzer = SentimentAnalyzer()
    
    # Example 1: Simple sentiment
    text1 = "I absolutely love this new restaurant!"
    print("\nAnalyzing simple sentiment:")
    print(analyzer.analyze(text1))
    
    # Example 2: Implication
    text2 = "The movie was interesting, to say the least."
    print("\nAnalyzing implication:")
    print(analyzer.analyze(text2))
    
    # Example 3: Attribute comparison
    text3 = "The new iPhone is faster but more expensive than the Samsung."
    print("\nAnalyzing attribute comparison:")
    print(analyzer.analyze(text3))

if __name__ == "__main__":
    main() 