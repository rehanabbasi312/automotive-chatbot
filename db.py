import mysql.connector
from flask import Flask, request, jsonify, abort, redirect, render_template

# Database configuration for MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'autolinkme'
}
 
# Function to establish a database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        abort(500, description="Database connection error.")

# Function to insert a new user into the database
def insert_user(name, username, password, account_status):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "INSERT INTO users (name, username, password, account_status) VALUES (%s, %s, %s, %s)"
        values = (name, username, password, account_status)
        cursor.execute(query, values)
        connection.commit()  # Commit the transaction
        cursor.close()
        connection.close()
        print("User inserted successfully")
        return True
    except mysql.connector.Error as e:
        print(f"Error inserting user: {e}")
        return False

# Function to verify user credentials
def verify_user(email, password):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT account_status FROM users WHERE username = %s AND password = %s"
        values = (email, password)
        cursor.execute(query, values)
        result = cursor.fetchone()  # Fetch one matching record
        cursor.close()
        connection.close()
        if result:
            return result[0]  # Return the account_status
        return None
    except mysql.connector.Error as e:
        print(f"Error during verify_user: {e}")
        return None

# Function to check if an email already exists in the database
def is_email_exists(email):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM users WHERE username = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] > 0  # Returns True if email exists
    except mysql.connector.Error as e:
        print(f"Error checking if email exists: {e}")
        return False



def get_all_makes():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT DISTINCT make FROM inventory"  # Replace 'make' with your column name for car makes
        cursor.execute(query)
        # Filter out empty or None values from the fetched rows
        makes = [row[0] for row in cursor.fetchall() if row[0]]  
        cursor.close()
        connection.close()
        return makes
    except mysql.connector.Error as e:
        print(f"Error fetching makes: {e}")
        return []
    

def get_all_years():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT DISTINCT year FROM inventory"  # Replace 'year' with your column name for car makes
        cursor.execute(query)
        # Filter out empty or None values from the fetched rows
        makes = [row[0] for row in cursor.fetchall() if row[0]]  
        cursor.close()
        connection.close()
        return makes
    except mysql.connector.Error as e:
        print(f"Error fetching makes: {e}")
        return []


def get_all_fuel():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT DISTINCT fuel FROM inventory"  # Replace 'fuel' with your column name for car makes
        cursor.execute(query)
        # Filter out empty or None values from the fetched rows
        makes = [row[0] for row in cursor.fetchall() if row[0]]  
        cursor.close()
        connection.close()
        return makes
    except mysql.connector.Error as e:
        print(f"Error fetching fuel: {e}")
        return []
    
def get_all_colors():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT DISTINCT ext_color FROM inventory"  # Replace 'color' with your column name for car makes
        cursor.execute(query)
        # Filter out empty or None values from the fetched rows
        makes = [row[0] for row in cursor.fetchall() if row[0]]  
        cursor.close()
        connection.close()
        return makes
    except mysql.connector.Error as e:
        print(f"Error fetching color: {e}")
        return []

def get_all_miles():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT DISTINCT mileage FROM inventory"  # Replace 'color' with your column name for car makes
        cursor.execute(query)
        # Filter out empty or None values from the fetched rows
        makes = [row[0] for row in cursor.fetchall() if row[0]]  
        cursor.close()
        connection.close()
        return makes
    except mysql.connector.Error as e:
        print(f"Error fetching color: {e}")
        return []

def get_cars_by_make(make):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query to fetch car details including images
        query = """
        SELECT id, description, options, imagelist, mileage, price,transmission, drivetrain, engine, fuel, ext_color, int_color, make, new_used, model 
        FROM inventory 
        WHERE make = %s
        """
        cursor.execute(query, (make,))
        
        cars = cursor.fetchall()
        valid_cars = []
        
        for car in cars:
            if car['imagelist']:
                if isinstance(car['imagelist'], str):
                    images = car['imagelist'].split(',')
                elif isinstance(car['imagelist'], list):
                    images = car['imagelist']
                else:
                    images = []

                if images:  # Ensure the images list is not empty
                    # Add image_link (the first image) to the car details
                    car['image_link'] = images[0]
                    
                    # Assign unique IDs for each image (car id + image index)
                    car['image_ids'] = [{'image_id': f"{car['id']}_{index}", 'image_link': image} for index, image in enumerate(images)]
                    
                    valid_cars.append(car)  # Only add cars with a valid image

        cursor.close()
        connection.close()
        return valid_cars

    except mysql.connector.Error as e:
        print(f"Error fetching cars for make '{make}': {e}")
        return []

    
def get_cars_by_year(year):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, description, options, imagelist, mileage, price,transmission, drivetrain, engine, fuel, ext_color, int_color, make, new_used, model 
        FROM inventory 
        WHERE year = %s
        """
        cursor.execute(query, (year,))
        
        cars = cursor.fetchall()
        valid_cars = []
        for car in cars:
            if car['imagelist']:
                if isinstance(car['imagelist'], str):
                    images = car['imagelist'].split(',')
                elif isinstance(car['imagelist'], list):
                    images = car['imagelist']
                else:
                    images = []

                if images:  # Ensure the images list is not empty
                    car['image_link'] = images[0]
                    valid_cars.append(car)  # Only add cars with a valid image

        cursor.close()
        connection.close()
        return valid_cars
    except mysql.connector.Error as e:
        print(f"Error fetching cars for year '{year}': {e}")
        return []


def get_cars_by_fuel(fuel):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, description, options, imagelist, mileage, price,transmission, drivetrain, engine, fuel, ext_color, int_color, make, new_used, model 
        FROM inventory 
        WHERE fuel = %s
        """
        cursor.execute(query, (fuel,))
        
        cars = cursor.fetchall()
        valid_cars = []
        for car in cars:
            if car['imagelist']:
                if isinstance(car['imagelist'], str):
                    images = car['imagelist'].split(',')
                elif isinstance(car['imagelist'], list):
                    images = car['imagelist']
                else:
                    images = []

                if images:  # Ensure the images list is not empty
                    car['image_link'] = images[0]
                    valid_cars.append(car)  # Only add cars with a valid image

        cursor.close()
        connection.close()
        return valid_cars
    except mysql.connector.Error as e:
        print(f"Error fetching cars for fuel '{fuel}': {e}")
        return []
    

def get_cars_by_colors(color):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, description, options, imagelist, mileage, price,transmission, drivetrain, engine, fuel, ext_color, int_color, make, new_used, model 
        FROM inventory 
        WHERE ext_color = %s
        """
        cursor.execute(query, (color,))
        
        cars = cursor.fetchall()
        valid_cars = []
        for car in cars:
            if car['imagelist']:
                if isinstance(car['imagelist'], str):
                    images = car['imagelist'].split(',')
                elif isinstance(car['imagelist'], list):
                    images = car['imagelist']
                else:
                    images = []

                if images:  # Ensure the images list is not empty
                    car['image_link'] = images[0]
                    valid_cars.append(car)  # Only add cars with a valid image

        cursor.close()
        connection.close()
        return valid_cars
    except mysql.connector.Error as e:
        print(f"Error fetching cars for color '{color}': {e}")
        return []
    

def get_cars_by_mileage(min_mileage, max_mileage):
    try:
        # Establish DB connection
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, description, options, imagelist, mileage, price,transmission, drivetrain, engine, fuel, ext_color, int_color, make, new_used, model 
        FROM inventory
        WHERE mileage BETWEEN %s AND %s
        """
        
        # Execute the query with the mileage range
        cursor.execute(query, (min_mileage, max_mileage))
        
        # Fetch the results
        cars = cursor.fetchall()
        valid_cars = []

        # Process the cars to check if images exist
        for car in cars:
            if car['imagelist']:
                # Handle the image list
                if isinstance(car['imagelist'], str):
                    images = car['imagelist'].split(',')
                elif isinstance(car['imagelist'], list):
                    images = car['imagelist']
                else:
                    images = []

                if images:  # Ensure the images list is not empty
                    car['image_link'] = images[0]  # Use the first image
                    valid_cars.append(car)  # Add the valid car to the list

        # Close DB connection
        cursor.close()
        connection.close()
        
        return valid_cars
    except mysql.connector.Error as e:
        print(f"Error fetching cars for mileage range '{min_mileage}-{max_mileage}': {e}")
        return []


def get_car_by_id(car_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT id, description, options, imagelist, mileage, price,transmission, drivetrain, engine, fuel, ext_color, int_color, make, new_used, model 
        FROM inventory 
        WHERE id = %s
        """
        cursor.execute(query, (car_id,))

        car = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        if car and car['imagelist']:
            # Split the image list into individual images (assuming it's a string of comma-separated values)
            images = car['imagelist'].split(',')
            car['image_list'] = images  # Store image list in the car dictionary

        return car

    except mysql.connector.Error as e:
        print(f"Error fetching car with id '{car_id}': {e}")
        return None



