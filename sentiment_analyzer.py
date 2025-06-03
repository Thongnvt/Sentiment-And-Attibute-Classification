from typing import Dict, List, Tuple, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
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
        
        # Define the tools for the agent
        self.tools = [
            Tool(
                name="analyze_sentiment",
                func=self._analyze_sentiment,
                description="Analyzes the sentiment of a given text, including implications"
            ),
            Tool(
                name="analyze_comparison",
                func=self._analyze_comparison,
                description="Analyzes and compares attributes between multiple objects in text"
            )
        ]
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert sentiment analyzer that can:
            1. Detect the overall sentiment (positive, negative, or neutral)
            2. Understand implications and hidden meanings in text
            3. Compare attributes between multiple objects when present
            4. Provide detailed explanations for your analysis
            5. Interpolate missing attributes when comparing objects
            
            When analyzing text with multiple objects, identify:
            - The objects being compared
            - Their respective attributes
            - The comparison relationship
            - The sentiment towards each object
            - Missing attributes that can be inferred
            
            Provide your analysis in a structured format."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Initialize the memory with the new approach
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        # Initialize the agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory
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
            
            You must strictly follow these rules. If the text contains any negative words, it MUST be classified as negative."""),
            ("human", f"""Analyze this text: "{text}"
            
            Return a JSON object with these fields:
            - sentiment: "positive", "negative", or "neutral"
            - confidence: number between 0 and 1
            - implications: list of any hidden meanings
            - explanation: brief explanation of your classification""")
        ]
        
        response = self.llm.invoke(messages)
        return self._parse_response(response.content)
    
    def _analyze_comparison(self, text: str) -> Dict:
        """
        Internal method to analyze comparisons between objects
        """
        prompt = f"""Analyze the following text for object comparison and attribute analysis:
        
        Text: {text}
        
        Provide a detailed analysis including:
        1. Objects being compared
        2. Attributes of each object (including interpolated attributes)
        3. Comparison relationships
        4. Sentiment towards each object
        5. Confidence scores for each comparison
        
        Format the response as a JSON object with these fields."""
        
        response = self.llm.invoke(prompt)
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
                return {
                    "comparison": {
                        "object1": parsed_data["objects_being_compared"][0]["name"],
                        "object2": parsed_data["objects_being_compared"][1]["name"],
                        "attributes": {
                            attr: {
                                parsed_data["objects_being_compared"][0]["name"]: value,
                                parsed_data["objects_being_compared"][1]["name"]: value
                            }
                            for attr, value in parsed_data["attributes"][parsed_data["objects_being_compared"][0]["name"]]["explicit_attributes"].items()
                        }
                    }
                }
            
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
            print(f"An unexpected error occurred during parsing: {e}")
            return {"sentiment": "error", "confidence": 0.0, "explanation": f"Parsing error: {e}"}
    
    def analyze(self, text: str) -> Dict:
        """
        Main method to analyze text using the agent
        """
        # Check for empty input
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
            
        # Determine if the text contains a comparison
        comparison_prompt = f"""Does the following text contain a comparison between two or more objects?
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