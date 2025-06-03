from typing import Dict, List, Tuple, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

class SentimentAnalyzer:
    def __init__(self):
        # Initialize the LLM with Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0,
            google_api_key=GOOGLE_API_KEY
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
        
        # Initialize the memory
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
        prompt = f"""Analyze the following text for sentiment and implications:
        
        Text: {text}
        
        Provide a detailed analysis including:
        1. Overall sentiment (positive, negative, or neutral)
        2. Confidence score (0-1)
        3. Any implications or hidden meanings
        4. Explanation of your analysis
        
        Format the response as a JSON object with these fields."""
        
        response = self.llm.invoke(prompt)
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
        """
        Parse the LLM response into a structured format
        """
        # In a real implementation, you would parse the JSON response
        # For now, we'll return a mock structure
        return {
            "sentiment": "positive",
            "confidence": 0.95,
            "implications": ["The speaker is very satisfied"],
            "comparison": {
                "object1": "iPhone",
                "object2": "Samsung",
                "attributes": {
                    "speed": {"iPhone": 0.9, "Samsung": 0.7},
                    "price": {"iPhone": 0.8, "Samsung": 0.6}
                }
            },
            "explanation": "Detailed analysis of the text..."
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Main method to analyze text using the agent
        """
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