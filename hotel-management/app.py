import random
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "126945c1bdc73d55bb3d364aed2611f8"
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow CORS for all origins

def get_connection():
    """
    Establishes a connection to the MySQL database.
    Replace 'root' and 'Liku@123#' with your MySQL credentials.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Liku@123#",
            database="hotel_management",
            auth_plugin='mysql_native_password'
        )
        print("Database connected!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to the database: {err}")
        raise

@app.route('/')
def home():
    """
    Serve a simple home page or message at the root endpoint.
    """
    return jsonify({"message": "Welcome to the Hotel Management System API!"})
@app.route('/reservations', methods=['POST'])
def create_reservation():
    try:
        data = request.json

        # Retrieve and validate fields
        required_fields = [
            'guest_name', 'contact_number', 'email', 'gender', 'id_proof_type',
            'id_proof_number', 'address', 'check_in', 'check_out', 'room_category', 'room_number'
        ]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        guest_name = data['guest_name']
        contact_number = data['contact_number']
        email = data['email']
        gender = data['gender']
        id_proof_type = data['id_proof_type']
        id_proof_number = data['id_proof_number']
        address = data['address']
        check_in = data['check_in']
        check_out = data['check_out']
        room_category = data['room_category']
        room_number = data['room_number']
        special_requests = data.get('special_requests', '')

        # Price calculation
        room_prices = {"suite": 1500, "deluxe": 3000, "superdelux": 5000}
        gst_rates = {"suite": 0.12, "deluxe": 0.18, "superdelux": 0.18}
        if room_category not in room_prices:
            return jsonify({"error": "Invalid room category"}), 400

        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
        except ValueError as ve:
            return jsonify({"error": f"Invalid date format: {ve}"}), 400

        if check_out_date <= check_in_date:
            return jsonify({"error": "Check-out date must be after check-in date"}), 400

        nights = max((check_out_date - check_in_date).days, 1)
        base_price = room_prices[room_category] * nights
        price = base_price + base_price * gst_rates[room_category]

        conn = get_connection()
        cursor = conn.cursor()

        # Check if room exists and is available
        cursor.execute("SELECT current_status, room_category FROM rooms WHERE room_number = %s", (room_number,))
        room = cursor.fetchone()
        if not room:
            conn.close()
            return jsonify({"error": "Room number does not exist"}), 400
        if room[0] != 'available':
            conn.close()
            return jsonify({"error": "Room is not available"}), 400
        if room[1] != room_category:
            conn.close()
            return jsonify({"error": "Room category does not match the selected room"}), 400

        # Insert reservation
        query = """
        INSERT INTO reservations (
            guest_name, contact_number, email, gender, id_proof_type, id_proof_number,
            address, check_in, check_out, room_category, room_number, special_requests, price
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            guest_name, contact_number, email, gender, id_proof_type, id_proof_number,
            address, check_in, check_out, room_category, room_number, special_requests, price
        ))

        # Update room status to booked
        cursor.execute("UPDATE rooms SET current_status = 'booked' WHERE room_number = %s", (room_number,))

        conn.commit()
        conn.close()
        return jsonify({"message": "Reservation created successfully!"}), 201

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500

@app.route('/reservations', methods=['GET'])
def get_reservations():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, ro.room_category AS room_category, ro.current_status AS room_status
            FROM reservations r
            JOIN rooms ro ON r.room_number = ro.room_number
        """)
        reservations = cursor.fetchall()
        conn.close()
        return jsonify(reservations), 200

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500

@app.route('/reservations/<int:id>', methods=['PUT'])
def update_reservation(id):
    try:
        data = request.json
        conn = get_connection()
        cursor = conn.cursor()

        fields = []
        values = []
        for field in ['guest_name', 'contact_number', 'email', 'gender', 'id_proof_type', 'id_proof_number', 'address', 'check_in', 'check_out', 'room_category', 'room_number', 'special_requests']:
            if field in data:
                fields.append(f"{field} = %s")
                values.append(data[field])

        if fields:
            # Fetch existing room_number if updating room_number
            if 'room_number' in data:
                cursor.execute("SELECT room_number FROM reservations WHERE id = %s", (id,))
                old_room_number = cursor.fetchone()
                if old_room_number:
                    cursor.execute("UPDATE rooms SET current_status = 'available' WHERE room_number = %s", (old_room_number[0],))
            
            values.append(id)
            query = f"UPDATE reservations SET {', '.join(fields)} WHERE id = %s"
            cursor.execute(query, values)

            if 'room_number' in data:
                cursor.execute("UPDATE rooms SET current_status = 'booked' WHERE room_number = %s", (data['room_number'],))

            conn.commit()

        conn.close()
        return jsonify({"message": "Reservation updated successfully!"}), 200

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500

@app.route('/reservations/<int:id>', methods=['DELETE'])
def delete_reservation(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT room_number FROM reservations WHERE id = %s", (id,))
        room_number = cursor.fetchone()

        cursor.execute("DELETE FROM reservations WHERE id = %s", (id,))

        if room_number:
            cursor.execute("UPDATE rooms SET current_status = 'available' WHERE room_number = %s", (room_number[0],))

        conn.commit()
        conn.close()
        return jsonify({"message": "Reservation deleted successfully!"}), 200

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500

# @app.route('/reservations', methods=['POST'])
# def create_reservation():
#     try:
#         data = request.json

#         # Retrieve and validate fields
#         required_fields = [
#             'guest_name', 'contact_number', 'email', 'gender', 'id_proof_type', 
#             'id_proof_number', 'address', 'check_in', 'check_out', 'room_category', 'room_number'
#         ]
#         if not all(data.get(field) for field in required_fields):
#             return jsonify({"error": "Missing required fields"}), 400

#         guest_name = data['guest_name']
#         contact_number = data['contact_number']
#         email = data['email']
#         gender = data['gender']
#         id_proof_type = data['id_proof_type']
#         id_proof_number = data['id_proof_number']
#         address = data['address']
#         check_in = data['check_in']
#         check_out = data['check_out']
#         room_category = data['room_category']
#         room_number = data['room_number']
#         special_requests = data.get('special_requests', '')

#         # Price calculation
#         room_prices = {"suite": 1500, "deluxe": 3000, "superdelux": 5000}
#         gst_rates = {"suite": 0.12, "deluxe": 0.18, "superdelux": 0.18}
#         if room_category not in room_prices:
#             return jsonify({"error": "Invalid room category"}), 400

#         check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
#         check_out_date = datetime.strptime(check_out, '%Y-%m-%d')

#         if check_out_date < check_in_date:
#             return jsonify({"error": "Check-out date must be after check-in date"}), 400

#         nights = max((check_out_date - check_in_date).days, 1)
#         base_price = room_prices[room_category] * nights
#         price = base_price + base_price * gst_rates[room_category]

#         conn = get_connection()
#         cursor = conn.cursor()

#         # Check if room exists and is available
#         cursor.execute("SELECT current_status FROM rooms WHERE room_number = %s", (room_number,))
#         room = cursor.fetchone()
#         if not room or room[0] != 'available':
#             conn.close()
#             return jsonify({"error": "Room is not available"}), 400

#         # Insert reservation
#         query = """
#         INSERT INTO reservations (
#             guest_name, contact_number, email, gender, id_proof_type, id_proof_number,
#             address, check_in, check_out, room_category, room_number, special_requests, price
#         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         cursor.execute(query, (
#             guest_name, contact_number, email, gender, id_proof_type, id_proof_number,
#             address, check_in, check_out, room_category, room_number, special_requests, price
#         ))

#         # Update room status to booked
#         cursor.execute("UPDATE rooms SET current_status = 'booked' WHERE room_number = %s", (room_number,))

#         conn.commit()
#         conn.close()
#         return jsonify({"message": "Reservation created successfully!"}), 201

#     except mysql.connector.Error as db_err:
#         return jsonify({"error": f"Database error: {db_err}"}), 500
#     except Exception as e:
#         return jsonify({"error": f"Internal error: {e}"}), 500

# @app.route('/reservations', methods=['GET'])
# def get_reservations():
#     try:
#         conn = get_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("""
#             SELECT r.*, ro.room_category AS room_category, ro.current_status AS room_status
#             FROM reservations r
#             JOIN rooms ro ON r.room_number = ro.room_number
#         """)
#         reservations = cursor.fetchall()
#         conn.close()
#         return jsonify(reservations), 200

#     except mysql.connector.Error as db_err:
#         return jsonify({"error": f"Database error: {db_err}"}), 500
#     except Exception as e:
#         return jsonify({"error": f"Internal error: {e}"}), 500

# @app.route('/reservations/<int:id>', methods=['PUT'])
# def update_reservation(id):
#     try:
#         data = request.json
#         conn = get_connection()
#         cursor = conn.cursor()

#         fields = []
#         values = []
#         for field in ['guest_name', 'contact_number', 'email', 'gender', 'id_proof_type', 'id_proof_number', 'address', 'check_in', 'check_out', 'room_category', 'room_number', 'special_requests']:
#             if field in data:
#                 fields.append(f"{field} = %s")
#                 values.append(data[field])

#         if fields:
#             values.append(id)
#             query = f"UPDATE reservations SET {', '.join(fields)} WHERE id = %s"
#             cursor.execute(query, values)
#             conn.commit()

#         conn.close()
#         return jsonify({"message": "Reservation updated successfully!"}), 200

#     except mysql.connector.Error as db_err:
#         return jsonify({"error": f"Database error: {db_err}"}), 500
#     except Exception as e:
#         return jsonify({"error": f"Internal error: {e}"}), 500

# @app.route('/reservations/<int:id>', methods=['DELETE'])
# def delete_reservation(id):
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()

#         cursor.execute("DELETE FROM reservations WHERE id = %s", (id,))

#         conn.commit()
#         conn.close()
#         return jsonify({"message": "Reservation deleted successfully!"}), 200

#     except mysql.connector.Error as db_err:
#         return jsonify({"error": f"Database error: {db_err}"}), 500
#     except Exception as e:
#         return jsonify({"error": f"Internal error: {e}"}), 500

@app.route('/event_reservations', methods=['POST'])
def create_event_reservation():
    """
    Handles event reservation form submission.
    """
    try:
        data = request.json

        # Extract fields from the JSON payload
        event_name = data.get('event_name')
        date_time = data.get('date_time')
        duration = data.get('duration')
        attendees = data.get('attendees')
        client_name = data.get('client_name')
        contact_number = data.get('contact_number')
        email = data.get('email')
        address = data.get('address')
        total_cost = data.get('total_cost')

        # Validate mandatory fields
        if not all([event_name, date_time, duration, attendees, client_name, contact_number]):
            return jsonify({"error": "Missing required fields"}), 400

        # Insert data into the database
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO event_reservations (
            event_name, date_time, duration, attendees, client_name, 
            contact_number, email, address, total_cost
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            event_name, date_time, duration, attendees, client_name, 
            contact_number, email, address, total_cost
        ))
        conn.commit()
        conn.close()

        return jsonify({"message": "Event reservation created successfully!"}), 201
    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/event_reservations', methods=['GET'])
def get_event_reservations():
    """
    Fetches all event reservations from the database.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)  # Fetch rows as dictionaries
        cursor.execute("SELECT * FROM event_reservations")
        reservations = cursor.fetchall()
        conn.close()

        # Return JSON data
        return jsonify(reservations), 200
    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/staff', methods=['POST'])
def create_staff():
    """Handles staff creation form submission."""
    try:
        data = request.json

        # Retrieve fields from the request
        employee_name = data.get('employee_name')
        role = data.get('role')
        contact_information = data.get('contact_information')
        date_of_joining = data.get('date_of_joining')
        assigned_shift = data.get('assigned_shift')
        task_allocation = data.get('task_allocation')

        # Validate mandatory fields
        if not all([employee_name, role, contact_information, date_of_joining, assigned_shift, task_allocation]):
            return jsonify({"error": "Missing required fields"}), 400

        # Generate unique employee ID
        unique_id = f"EMP{int(datetime.now().timestamp())}{random.randint(1000, 9999)}"

        # Insert staff details into the database
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO staff (
            employee_id, employee_name, role, contact_information, date_of_joining, assigned_shift, task_allocation
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            unique_id, employee_name, role, contact_information, date_of_joining, assigned_shift, task_allocation
        ))
        conn.commit()
        conn.close()

        return jsonify({"message": "Staff created successfully!", "employee_id": unique_id}), 201

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/staff', methods=['GET'])
def get_staff():
    """Fetches all staff details from the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)  # Fetch rows as dictionaries
        cursor.execute("SELECT * FROM staff")
        staff_list = cursor.fetchall()
        conn.close()

        return jsonify(staff_list), 200
    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/staff/<employee_id>', methods=['PUT'])
def update_staff(employee_id):
    """Updates staff details for a given employee ID."""
    try:
        data = request.json

        # Retrieve fields from the request
        employee_name = data.get('employee_name')
        role = data.get('role')
        contact_information = data.get('contact_information')
        date_of_joining = data.get('date_of_joining')
        assigned_shift = data.get('assigned_shift')
        task_allocation = data.get('task_allocation')

        # Validate mandatory fields
        if not all([employee_name, role, contact_information, date_of_joining, assigned_shift, task_allocation]):
            return jsonify({"error": "Missing required fields"}), 400

        # Update staff details in the database
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        UPDATE staff SET 
            employee_name = %s, 
            role = %s, 
            contact_information = %s, 
            date_of_joining = %s, 
            assigned_shift = %s, 
            task_allocation = %s
        WHERE employee_id = %s
        """
        cursor.execute(query, (
            employee_name, role, contact_information, date_of_joining, assigned_shift, task_allocation, employee_id
        ))
        conn.commit()
        conn.close()

        return jsonify({"message": "Staff updated successfully!"}), 200

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/staff/<employee_id>', methods=['DELETE'])
def delete_staff(employee_id):
    """Deletes staff details for a given employee ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM staff WHERE employee_id = %s"
        cursor.execute(query, (employee_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Staff deleted successfully!"}), 200

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/menus', methods=['POST'])
def create_menu_item():
    """Handles the creation of a new menu item."""
    try:
        data = request.json

        # Retrieve fields from the request
        menu_name = data.get('menu_name')
        menu_description = data.get('menu_description')
        menu_category = data.get('menu_category')
        price = data.get('price')
        item_name = data.get('item_name')
        room_number = data.get('room_number')
        ordered_quantity = data.get('ordered_quantity')

        # Validate mandatory fields
        if not all([menu_name, menu_category, price, item_name, room_number, ordered_quantity]):
            return jsonify({"error": "Missing required fields"}), 400

        # Calculate the order total (12% GST)
        order_total = round(float(price) * int(ordered_quantity) * 1.12, 2)

        # Insert the menu item into the database
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO menus (
            menu_name, menu_description, menu_category, price, item_name, room_number, ordered_quantity, order_total
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            menu_name, menu_description, menu_category, price, item_name, room_number, ordered_quantity, order_total
        ))
        conn.commit()
        conn.close()

        return jsonify({"message": "Menu item created successfully!"}), 201

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/menus', methods=['GET'])
def get_menu_items():
    """Fetches all menu items from the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)  # Fetch rows as dictionaries
        cursor.execute("SELECT * FROM menus")
        menu_items = cursor.fetchall()
        conn.close()

        return jsonify(menu_items), 200
    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/menus/<int:menu_id>', methods=['PUT'])
def update_menu_item(menu_id):
    """Updates menu item details for a given menu ID."""
    try:
        data = request.json

        # Retrieve fields from the request
        menu_name = data.get('menu_name')
        menu_description = data.get('menu_description')
        menu_category = data.get('menu_category')
        price = data.get('price')
        item_name = data.get('item_name')
        room_number = data.get('room_number')
        ordered_quantity = data.get('ordered_quantity')

        # Validate mandatory fields
        if not all([menu_name, menu_category, price, item_name, room_number, ordered_quantity]):
            return jsonify({"error": "Missing required fields"}), 400

        # Calculate the updated order total (12% GST)
        order_total = round(float(price) * int(ordered_quantity) * 1.12, 2)

        # Update menu item details in the database
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        UPDATE menus SET 
            menu_name = %s, 
            menu_description = %s, 
            menu_category = %s, 
            price = %s, 
            item_name = %s, 
            room_number = %s, 
            ordered_quantity = %s, 
            order_total = %s
        WHERE id = %s
        """
        cursor.execute(query, (
            menu_name, menu_description, menu_category, price, item_name, room_number, ordered_quantity, order_total, menu_id
        ))

        # Check if any rows were affected
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Menu item not found"}), 404

        conn.commit()
        conn.close()

        return jsonify({"message": "Menu item updated successfully!"}), 200

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/menus/<int:menu_id>', methods=['DELETE'])
def delete_menu_item(menu_id):
    """Deletes a menu item for a given menu ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM menus WHERE id = %s"
        cursor.execute(query, (menu_id,))

        # Check if any rows were affected
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Menu item not found"}), 404

        conn.commit()
        conn.close()

        return jsonify({"message": "Menu item deleted successfully!"}), 200

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/rooms', methods=['POST'])
def create_room():
    """Handles the creation of a new room."""
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415

    try:
        data = request.json

        # Match field names from the frontend
        room_number = data.get('room_no')  # Adjusted to match frontend
        room_category = data.get('room_category')
        room_feature = data.get('room_feature')
        current_status = data.get('current_status')

        # Validate input
        if not all([room_number, room_category, room_feature, current_status]):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate ENUM constraints
        valid_categories = ['suite', 'deluxe', 'superdelux']
        valid_statuses = ['available', 'booked', 'maintenance']

        if room_category not in valid_categories:
            return jsonify({"error": f"Invalid room category. Must be one of {valid_categories}"}), 400

        if current_status not in valid_statuses:
            return jsonify({"error": f"Invalid room status. Must be one of {valid_statuses}"}), 400

        conn = get_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to the database."}), 500

        cursor = conn.cursor()

        # Check if room already exists
        cursor.execute("SELECT * FROM rooms WHERE room_number = %s", (room_number,))
        if cursor.fetchone():
            return jsonify({"error": "Room number already exists"}), 400

        # Insert new room
        query = """
        INSERT INTO rooms (room_number, room_category, room_feature, current_status)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (room_number, room_category, room_feature, current_status))
        conn.commit()

        return jsonify({"message": "Room created successfully!"}), 201

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500


@app.route('/rooms', methods=['GET'])
def get_rooms():
    """Fetches all rooms from the database."""
    try:
        conn = get_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to the database."}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
        SELECT 
            room_number AS room_no, room_category, room_feature, current_status
        FROM rooms
        """)
        rooms = cursor.fetchall()

        return jsonify(rooms), 200

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500

@app.route('/rooms/<int:room_number>', methods=['PUT'])
def update_room(room_number):
    """Updates an existing room in the database."""
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415

    try:
        data = request.json
        room_category = data.get('room_category')
        room_feature = data.get('room_feature')
        current_status = data.get('current_status')

        if not any([room_category, room_feature, current_status]):
            return jsonify({"error": "No fields provided for update"}), 400

        valid_categories = ['suite', 'deluxe', 'superdelux']
        valid_statuses = ['available', 'booked', 'maintenance']

        if room_category and room_category not in valid_categories:
            return jsonify({"error": f"Invalid room category. Must be one of {valid_categories}"}), 400

        if current_status and current_status not in valid_statuses:
            return jsonify({"error": f"Invalid room status. Must be one of {valid_statuses}"}), 400

        conn = get_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to the database."}), 500

        cursor = conn.cursor()
        updates = []
        values = []
        if room_category:
            updates.append("room_category = %s")
            values.append(room_category)
        if room_feature:
            updates.append("room_feature = %s")
            values.append(room_feature)
        if current_status:
            updates.append("current_status = %s")
            values.append(current_status)

        values.append(room_number)
        query = f"UPDATE rooms SET {', '.join(updates)} WHERE room_number = %s"
        cursor.execute(query, values)
        conn.commit()

        return jsonify({"message": "Room updated successfully!"}), 200

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500

@app.route('/rooms/<int:room_number>', methods=['DELETE'])
def delete_room(room_number):
    """Deletes a room from the database."""
    try:
        conn = get_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to the database."}), 500

        cursor = conn.cursor()

        # Check if the room is booked
        cursor.execute("SELECT current_status FROM rooms WHERE room_number = %s", (room_number,))
        room = cursor.fetchone()
        if not room:
            return jsonify({"error": "Room does not exist"}), 404
        if room[0] == 'booked':
            return jsonify({"error": "Cannot delete a booked room"}), 400

        # Delete room
        query = "DELETE FROM rooms WHERE room_number = %s"
        cursor.execute(query, (room_number,))
        conn.commit()

        return jsonify({"message": "Room deleted successfully!"}), 200

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500
    
    
@app.route('/housekeeping', methods=['POST'])
def create_housekeeping():
    """Handles the creation of a new housekeeping task."""
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    try:
        data = request.json

        room_no = data.get('room_no')
        staff_id = data.get('staff_id')
        task_type = data.get('task_type')
        current_status = data.get('current_status')
        last_clean_date = data.get('last_clean_date')

        if not all([room_no, staff_id, task_type, current_status, last_clean_date]):
            return jsonify({"error": "Missing required fields"}), 400

        conn = get_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to the database."}), 500

        cursor = conn.cursor()

        # Check for existing staff_id
        cursor.execute("SELECT * FROM housekeeping WHERE staff_id = %s", (staff_id,))
        if cursor.fetchone():
            return jsonify({"error": "Staff ID already exists."}), 409  # HTTP 409 Conflict

        # Insert new record
        query = """
        INSERT INTO housekeeping (room_no, staff_id, task_type, current_status, last_clean_date)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (room_no, staff_id, task_type, current_status, last_clean_date))
        conn.commit()

        return jsonify({"message": "Housekeeping task created successfully!"}), 201

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500


@app.route('/housekeeping', methods=['GET'])
def get_housekeeping():
    """Fetches all housekeeping tasks from the database."""
    try:
        conn = get_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to the database."}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
        SELECT room_no, staff_id, task_type, current_status, last_clean_date
        FROM housekeeping
        """)
        tasks = cursor.fetchall()

        return jsonify(tasks), 200

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500


@app.route('/housekeeping/staff/<string:staff_id>', methods=['PUT'])
def update_housekeeping(staff_id):
    """Updates an existing housekeeping task by staff_id."""
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415

    try:
        # Get data from the request
        data = request.json
        room_no = data.get('room_no')
        task_type = data.get('task_type')
        current_status = data.get('current_status')
        last_clean_date = data.get('last_clean_date')

        # Validate the required fields
        if not all([room_no, task_type, current_status, last_clean_date]):
            return jsonify({"error": "Missing required fields"}), 400

        # Check if valid values are provided
        if current_status == "Select" or task_type == "Select":
            return jsonify({"error": "Invalid selection for task type or current status"}), 400

        # Connect to the database
        conn = get_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to the database."}), 500

        cursor = conn.cursor()

        # Check if the housekeeping task exists for the given staff_id
        cursor.execute("SELECT * FROM housekeeping WHERE staff_id = %s", (staff_id,))
        existing_task = cursor.fetchone()

        if not existing_task:
            return jsonify({"error": "Housekeeping task not found for the given staff_id"}), 404

        # Update the housekeeping task
        query = """
        UPDATE housekeeping
        SET room_no = %s, task_type = %s, current_status = %s, last_clean_date = %s
        WHERE staff_id = %s
        """
        cursor.execute(query, (room_no, task_type, current_status, last_clean_date, staff_id))
        conn.commit()

        return jsonify({"message": "Housekeeping task updated successfully!"}), 200

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500


@app.route('/housekeeping/staff/<string:staff_id>', methods=['DELETE'])
def delete_housekeeping(staff_id):
    """Deletes a housekeeping task by staff_id."""
    try:
        conn = get_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to the database."}), 500

        cursor = conn.cursor()
        query = "DELETE FROM housekeeping WHERE staff_id = %s"
        cursor.execute(query, (staff_id,))
        conn.commit() 

        return jsonify({"message": "Housekeeping task deleted successfully!"}), 200

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/admin/register', methods=['POST']) 
def admin_register():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if not email or not password or not confirm_password:
            return jsonify({"error": "All fields are required"}), 400

        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT email FROM admin WHERE email = %s", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Email already registered"}), 409

        cursor.execute("INSERT INTO admin (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "Registration successful"}), 201

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500

@app.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM admin WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result and result[0] == password:
            session['logged_in'] = True
            session['admin_email'] = email
            conn.close()
            return jsonify({"message": "Login successful", "redirect": "frontpage.html"}), 200
        else:
            conn.close()
            return jsonify({"error": "Invalid email or password"}), 401

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500

@app.route('/admin/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.json
        email = data.get('email')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not email or not new_password or not confirm_password:
            return jsonify({"error": "All fields are required"}), 400

        if new_password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT email FROM admin WHERE email = %s", (email,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Email not found"}), 404

        cursor.execute("UPDATE admin SET password = %s WHERE email = %s", (new_password, email))
        conn.commit()
        conn.close()
        return jsonify({"message": "Password updated successfully"}), 200

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500

@app.route('/admin/update-email-password', methods=['PUT'])
def update_email_password():
    try:
        data = request.json
        old_email = data.get('old_email')
        new_email = data.get('new_email')
        new_password = data.get('new_password')

        if not old_email or not new_email or not new_password:
            return jsonify({"error": "All fields are required"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT email FROM admin WHERE email = %s", (old_email,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Email not found"}), 404

        cursor.execute("UPDATE admin SET email = %s, password = %s WHERE email = %s", (new_email, new_password, old_email))
        conn.commit()
        conn.close()
        return jsonify({"message": "Email and password updated successfully"}), 200

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
