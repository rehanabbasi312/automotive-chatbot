import os
import pyodbc
import mysql.connector
from flask import Flask, render_template, request, jsonify, redirect, session
from chatbot import get_chat_chain, format_messages_for_chain
from db import insert_user, is_email_exists, verify_user, get_db_connection, get_all_makes, get_cars_by_make, get_all_years, get_cars_by_year, get_all_fuel, get_cars_by_fuel, get_all_colors, get_cars_by_colors, get_all_miles, get_cars_by_mileage, get_car_by_id
import google.generativeai as genai
import uuid
import requests


app = Flask(__name__)

genai.configure(api_key='AIzaSyAQLzOSHPX2emeevYmTGBAyL3DD8I5H8Wg')

app.secret_key = '426aa9cce892b131c73301a87ac2e850c694215119794aa4'  # # Generated a 24-byte secret key

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'autolinkme'
}

chat_history = {}
language = "English"
car_preferences = {}
user_email = ""



# Function to get database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

def format_bot_response(response: str) -> str:
    return response

def summarize_conversation(messages):
    user_messages = [msg['content'] for msg in messages if msg['role'] == 'user']
    assistant_messages = [msg['content'] for msg in messages if msg['role'] == 'assistant']
    
    if user_messages:
        summary = user_messages[0]
        if assistant_messages:
            summary += " - " + assistant_messages[-1][:30]
        return summary
    return "New Chat"

# Function to map user query to the corresponding SQL query
def get_car_query(user_message, chat_id):

    keyword_synonyms = {
        'used cars': ['used cars', 'pre-owned cars', 'second-hand cars', 'cars under budget', 'affordable used cars'],
        'cheapest cars': ['cheapest cars', 'budget cars', 'low-cost cars', 'most affordable cars'],
        'latest year cars': ['latest year cars', 'newest models', 'recently manufactured cars', '2023 cars', '2024 cars', '2025 cars'],
    }

    query_map = {
        'used cars': "SELECT * FROM inventory WHERE new_used = 'Used' AND make IS NOT NULL AND model IS NOT NULL AND engine IS NOT NULL AND mileage IS NOT NULL AND fuel IS NOT NULL AND year IS NOT NULL AND imagelist IS NOT NULL AND imagelist <> '' AND id IS NOT NULL ORDER BY RAND() LIMIT 3",
        'cheapest cars': "SELECT * FROM inventory WHERE price IS NOT NULL AND make IS NOT NULL AND model IS NOT NULL AND engine IS NOT NULL AND mileage IS NOT NULL AND fuel IS NOT NULL AND year IS NOT NULL AND new_used IS NOT NULL AND imagelist IS NOT NULL AND imagelist <> '' AND id IS NOT NULL ORDER BY price ASC LIMIT 3",
        'latest year cars': "SELECT * FROM inventory WHERE year IS NOT NULL AND make IS NOT NULL AND model IS NOT NULL AND engine IS NOT NULL AND mileage IS NOT NULL AND fuel IS NOT NULL AND new_used IS NOT NULL AND imagelist IS NOT NULL AND imagelist <> '' AND id IS NOT NULL ORDER BY year DESC LIMIT 3"
    }

      # Normalize user message to lowercase for matching
    user_message = user_message.lower()

    # Check if the user message matches any keyword or its synonyms
    for keyword, synonyms in keyword_synonyms.items():
        if any(phrase in user_message for phrase in synonyms):
            # Return the corresponding SQL query
            return query_map[keyword], None

    # Check if model is provided in car_preferences
    if "model" in car_preferences[chat_id]:
        model = car_preferences[chat_id]["model"]
        print(f"[DEBUG] Model '{model}' provided, querying database...")

        query = """
            SELECT id, new_used, year, make, model, body_style, doors, trim, ext_color, int_color, 
                   engine, fuel, cylinders, transmission, mileage, displacement, price, 
                   description, imagelist, status 
            FROM inventory 
            WHERE model = %s AND make IS NOT NULL AND year IS NOT NULL AND engine IS NOT NULL AND mileage IS NOT NULL AND fuel IS NOT NULL AND new_used IS NOT NULL AND imagelist IS NOT NULL AND imagelist <> ''
        """
        return query, (model,)
    
    return None, None

# Function to fetch car data from the database based on the query
def fetch_cars_from_db(query, params):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    cars = cursor.fetchall()
    connection.close()
    return cars

@app.route('/')
def index():
    makes = get_all_makes()  # Fetch all makes from the database
    return render_template('index.html', makes=makes)  # Pass the list as 'makes'

@app.route('/model/<make>')
def model(make):
    # Fetch all makes from the database
    makes = get_all_makes()
    # Fetch cars for the selected make
    cars = get_cars_by_make(make)

    return render_template('model.html', make=make, cars=cars, makes=makes)  # Pass cars to the template


@app.route('/years/<make>')
def years(make):
    # Fetch all makes from the database
    years = get_all_years()
    # Fetch cars for the selected make
    cars = get_cars_by_make(make)
    return render_template('years.html', make=make, cars=cars, years=years)


@app.route('/fuel/<yearr>')
def fuel(yearr):
    # Ensure yearr is a valid year (e.g., convert from string to int if necessary)
    try:
        yearr = int(yearr)  # Convert to integer
    except ValueError:
        return "Invalid year provided", 400
    
    fuels=get_all_fuel()

    # Fetch cars for the selected year
    cars = get_cars_by_year(yearr)
    
    return render_template('fuel.html', cars=cars, yearr=yearr,fuels=fuels)


@app.route('/colors/<fuell>')
def colors(fuell):
    colors = get_all_colors()
    
    cars = get_cars_by_fuel(fuell)
    return render_template('colors.html', cars=cars, colors=colors, fuell=fuell)


@app.route('/miles/<colors>')
def miles(colors):
    miles = get_all_miles()
    
    cars = get_cars_by_colors(colors)
    return render_template('miles.html',cars=cars, miles=miles, colors=colors)

@app.route('/selected-miles/<min_mileage>-<max_mileage>')
def selectedmiles(min_mileage, max_mileage):
    # Call the function to get cars based on the mileage range
    cars = get_cars_by_mileage(min_mileage, max_mileage)
    
    # Return the filtered cars to the template
    return render_template('selected-miles.html', cars=cars, min_mileage=min_mileage, max_mileage=max_mileage)

@app.route('/vdp/<int:car_id>')
def vdp(car_id):
    # Fetch the car details by its unique ID
    car = get_car_by_id(car_id)  # Fetch car details by ID
    print(car)
    
    if car:
        # Pass the car details to the template
        return render_template('vdp.html', car=car)
    else:
        # Handle case if car not found (optional)
        return "Car not found", 404


@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data['message']
    chat_id = data['chat_id']
    user_id = ""
   
    print(f"[DEBUG] Received message: '{user_message}' for chat_id: '{chat_id}'")

    # Create new chat history if not exists
    if chat_id not in chat_history:
        print(f"[DEBUG] Creating new chat history for chat_id: '{chat_id}'")
        chat_history[chat_id] = {'messages': [], 'title': 'New Chat'}
        car_preferences[chat_id] = {}

    # Add user message to history
    chat_history[chat_id]['messages'].append({"role": "user", "content": user_message})

    # Check if query matches any car types or if a model is provided
    query, params = get_car_query(user_message, chat_id)
    cars = []
    car_images = []
    car_details = []
    car_details_links = []
    car_images_str = ""  # Initialize car_images_str as an empty string


    if query:
        cars = fetch_cars_from_db(query, params)
        response = generate_car_response(cars)
        car_images = [car['imagelist'].split(',')[0] for car in cars]
        car_images_str = ','.join(car_images)  # Convert list to a comma-separated string
        car_details = [{
            "make": car['make'],
            "model": car['model'],
            "year": car['year'],
            "price": car['price'],
            "condition": car['new_used'],
            "engine": car['engine'],
            "mileage": car['mileage'],
            "fuel": car['fuel'],
            "car_images": car['imagelist'].split(','),  # Assuming imagelist is a comma-separated string
            "id": car['id'],
            "description": car['description'] 
        } for car in cars]
        car_details_links = [f"/car-details/{car['model']}" for car in cars]
        
        # Save the car details in car_preferences for later retrieval in /car-details route
        car_preferences[chat_id]['car_details'] = car_details
        car_preferences[chat_id]['car_details_links'] = car_details_links
    else:
        # Generate response using chatbot if no matching car query
        response = generate_chatbot_response(chat_id)

    # Insert user message and bot response into the database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Example insert query to store user message and bot response
        cursor.execute(
            "INSERT INTO chat_history (chatID, userID, userChat, botChat, imageList) VALUES (%s, %s, %s, %s, %s)",
            (chat_id, user_id, user_message, response, car_images_str)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[DEBUG] Chat history inserted successfully for chat_id: {chat_id}")
        print("Links: ",car_images_str)
    except Exception as e:
        print(f"[ERROR] Failed to insert chat history into the database: {e}")

    # Return the response along with car details if any
    return jsonify({
        "response": response,
        "car_images": car_images if len(cars) > 0 else [],
        "car_details": car_details if len(cars) > 0 else [],
        "car_details_links": car_details_links if len(cars) > 0 else []
    })


# Function to generate the car response based on the fetched cars
def generate_car_response(cars):
    if cars:
        response = "Here are some cars based on your request:\n"
        for car in cars:
            response += f"\n- **Year**: {car['year']}\n"
            response += f"- **Make**: {car['make']}\n"
            response += f"- **Model**: {car['model']}\n"
            response += f"- **Price**: {car['price']}\n"
            response += f"- **Condition**: {car['new_used']}\n"
            response += f"- **Engine**: {car['engine']}\n"
            response += f"- **Mileage**: {car['mileage']}\n"
            response += f"- **Fuel**: {car['fuel']}\n"
            response += f"- **Id**: {car['id']}\n"
            response += f"- **Desc**: {car['description']}\n"
            response += "\n"
        return response
    return "Sorry, no cars found matching your preference."

# Function to generate chatbot response
def generate_chatbot_response(chat_id):
    chat_chain = get_chat_chain()
    chain_input = {
        "messages": format_messages_for_chain(chat_history[chat_id]['messages']),
        "language": "English"
    }
    try:
        response = chat_chain.invoke(chain_input)
        return format_bot_response(response)
    except Exception as e:
        print(f"[ERROR] Failed to invoke chat chain: {e}")
        return "Sorry, there was an error processing your request."

@app.route('/car-details/<car_name>', methods=['GET'])
def car_details(car_name):
    car_name_lower = car_name.lower().strip()  # Convert to lowercase and remove any extra spaces

    # Initialize variables
    car_details_list = []
    car_images = []
    matched_chat_id = None

    # Search for the matching car model in car_preferences
    for chat_id, preferences in car_preferences.items():
        if preferences.get('car_details'):
            # Find the correct model
            for car in preferences['car_details']:
                if car['model'].lower().strip() == car_name_lower:
                    matched_chat_id = chat_id
                    car_details_list = [car]  # Found the car details
                    car_images = car['car_images']  # Get all images for the car
                    break
        if matched_chat_id:
            break

    if not matched_chat_id:
        print(f"[DEBUG] No matching car model found for car_name '{car_name}'")
        # You can fetch the car details from the database if needed
        # If no match is found, you might want to query the database and fetch the car again

    # Render the car-details.html page with the car details and images
    return render_template('car-details.html', car_name=car_name, images=car_images, car_details=car_details_list)


# Route for starting a new chat
@app.route('/new_chat', methods=['POST'])
def new_chat():
    chat_id = str(uuid.uuid4())
    chat_history[chat_id] = {'messages': [], 'title': 'New Chat'}
    car_preferences[chat_id] = {}
    print(f"[DEBUG] New chat created with chat_id: '{chat_id}'")
    return jsonify({"status": "success", "chat_id": chat_id})

# Route for getting chat history
@app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    history = [{"id": chat_id, "title": chat['title']} for chat_id, chat in chat_history.items()]
    print(f"[DEBUG] Returning chat history: {history}")
    return jsonify({"history": history})

# Route for clearing chat history
@app.route('/clear_history', methods=['POST'])
def clear_history():
    global chat_history
    chat_history = {}
    car_preferences.clear()
    print(f"[DEBUG] Chat history cleared")
    return jsonify({"status": "success"})

# Route for dealer page
@app.route('/dealer', methods=['GET'])
def dealer():
    return render_template('dealer.html')

#if __name__ == '__main__':
#    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
