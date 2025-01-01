from typing import Any, List, Optional, Dict
from langchain.llms.base import LLM
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import HumanMessage, AIMessage
from pydantic import Field, PrivateAttr
import google.generativeai as genai

class GeminiLLM(LLM):
    model_name: str = Field(default="gemini-pro")
    max_output_tokens: int = Field(default=1024)
    _model: Any = PrivateAttr()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model = genai.GenerativeModel(self.model_name)

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # Ensure the message is car-related, otherwise redirect the user
        if not self.is_car_related(prompt):
            return "I'm an Automotive AI Assistant, and my expertise is focused on cars and automotive-related topics. Let's discuss anything about cars, such as models, maintenance, or buying advice! How can I assist you with your car-related needs?"

        response = self._model.generate_content(prompt, generation_config={
            "max_output_tokens": self.max_output_tokens,
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
        })
        return response.text

    def is_car_related(self, user_message: str) -> bool:
        car_keywords = [
            "car", "vehicle", "engine", "mileage", "model", "sedan", "suv", "hatchback",
            "auto", "automobile", "tires", "maintenance", "repair", "brakes", "hybrid",
            "electric", "gasoline", "diesel", "horsepower", "buy", "sell", "troubleshoot",
            "battery", "safety", "specifications", "features"
        ]
        return any(keyword in user_message.lower() for keyword in car_keywords)

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"name_of_model": self.model_name, "max_output_tokens": self.max_output_tokens}

    @property
    def _llm_type(self) -> str:
        return "gemini"

def get_chat_chain():
    llm = GeminiLLM()

    prompt = ChatPromptTemplate.from_messages([
    ("system", """You are only Automotive Assistant, an Automotive Assistant specialized in providing information about cars and helping users find the right car for their needs. Your personality is friendly, patient, and enthusiastic about cars. You engage in natural, flowing conversations and can ask questions to better understand the user's needs.

    Your knowledge covers:
    - Car models, makes, and manufacturers
    - Technical specifications and features
    - Car maintenance and troubleshooting
    - Auto industry news and trends
    - Car buying and selling advice
    - Vehicle safety and regulations
    - Classic and vintage cars
    - Electric and hybrid vehicles
    - Automotive technology advancements

    **Important Behavior Instructions:**
    - You must **only respond to car-related and automotive queries**. If the user asks about a non-car-related topic, acknowledge their query briefly, but steer the conversation back to automotive topics.
    - Politely suggest a car-related topic the user might find interesting to guide the conversation.

    **Conversation Flow:**
    1. Start with a warm greeting and introduce yourself.
    2. If it's the user's first message, ask about their interest in cars or if they need help finding a car.
    3. If the user is unsure or new to cars, guide them by asking relevant questions about their needs, preferences, and budget.
    4. Based on their responses, provide car recommendations or relevant information.
    5. If the user asks about topics unrelated to cars, acknowledge their question, then politely redirect the conversation back to cars.

    **Response Formatting Instructions:**
    - Use **bold** text for headings or key points.
    - If you provide a list, use bullet points (`-`) for each item.
    - Separate major sections with line breaks to ensure readability.
    - Start each response in a friendly and conversational way.
    
    Example Response Formatting:
    **Size and Space**: SUVs are larger, offering more interior space, whereas sedans are more compact, providing better fuel efficiency.
    
    **Performance**: 
    - SUVs are better for off-road capabilities.
    - Sedans are more suited for city driving and fuel economy.

    **Behavior in Non-Automotive Queries:**
    - If the user asks about a non-car-related topic, you can respond like this:
        "That's an interesting question! However, my expertise is focused on cars and automotive topics. Is there a car-related query I can help you with, such as finding the right vehicle, understanding car features, or maintenance tips?"
    - If the user persists with non-car topics, respond kindly and remain focused on automotive expertise.

    Remember:
    - Maintain a friendly and conversational tone.
    - Be patient with users who are new to cars and explain concepts clearly.
    - If you don't have specific information about a particular car model, acknowledge this and offer to provide general information about similar cars or the manufacturer.
    - Always prioritize safety and encourage users to consult with professionals for serious car issues or when making significant financial decisions.
    - Do not start chat with AI:, [Automotive Assistant]:, Automotive Assistant:, or any other AI-related phrases, just start with normal chat.

    Respond in {language}.
    """),
    MessagesPlaceholder(variable_name="messages"),
])


    chain = prompt | llm | StrOutputParser()

    return chain


# Add a new method to extract car details from user input
def extract_car_details(user_message: str) -> dict:
    extract_prompt = f"""
    You are an expert in extracting car-related information. Given the user's input, extract the following details if available:
    - **Car Name** (e.g., BMW, Tesla, Toyota)
    - **Model** (e.g., 2016, 2021)
    - **Engine** (e.g., 2.0L, V6)
    - **Mileage** (e.g., 25 mpg, 30 km/l)
    - **Condition** (New or Used)
    - **Budget** (numeric value, e.g., 20000, $25,000)

    If a specific detail is not available in the user message, return "None" for that detail.

    User Message: "{user_message}"

    Please extract the details and return them in the format:
    Car Name: <value>
    Model: <value>
    Engine: <value>
    Mileage: <value>
    Condition: <value>
    Budget: <value>
    """

    llm = GeminiLLM()
    response = llm._call(extract_prompt).strip()

    # Parse the response into a dictionary
    details = {}
    for line in response.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            details[key.strip()] = value.strip()

    return details

# Add a new method to extract the car name from user input
def extract_car_name(user_message: str) -> Optional[str]:
    # Explicitly prompt the model to identify if a car name or brand is mentioned
    extract_prompt = f"""
    You are an expert in automotive brands. Given the following user input, identify the car make or model mentioned. 
    User input: "{user_message}"
    
    Respond only with the car name or model, or "None" if no car is mentioned.
    """
    llm = GeminiLLM()
    car_name = llm._call(extract_prompt).strip()

    # If the response is "None", return None
    if car_name.lower() == "none":
        return None
    return car_name

def format_messages_for_chain(messages):
    return [
        HumanMessage(content=msg["content"]) if msg["role"] == "user" 
        else AIMessage(content=msg["content"]) 
        for msg in messages
    ]
