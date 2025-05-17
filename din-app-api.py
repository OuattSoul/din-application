from flask import Flask, request, jsonify
import pymysql
import hashlib
import os
from pymysql.cursors import DictCursor

app = Flask(__name__)

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'db': 'din_recru',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

# Function to get database connection
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# Hash function for email
def hash_password(password):
    # Using SHA-256 for hashing
    return hashlib.sha256(password.lower().encode()).hexdigest()

# Test route
@app.route('/api/test', methods=['GET'])
def test_route():
    return jsonify({"message": "API is working!"})

# Add a new user with hashed email
@app.route('/api/users', methods=['POST'])
def add_user():
    try:
        data = request.json
        fname = data.get('fname')
        lname = data.get('lname')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')
        
        if not fname or not lname or not email or not password or not phone:
            return jsonify({"error": "Name and email are required"}), 400
            
        # Hash the email before storing
        password_hash = hash_password(password)
        
        # Connect to database
        connection = get_db_connection()
        
        try:
            with connection.cursor() as cursor:
                # Check if email hash already exists
                sql_check = "SELECT id FROM user_register WHERE email = %s"
                cursor.execute(sql_check, (email))
                if cursor.fetchone():
                    return jsonify({"error": "Email already registered"}), 409
                
                # Insert new user
                sql_insert = "INSERT INTO user_register (fname, lname, email, phone, password) VALUES (%s, %s, %s,  %s, %s)"
                cursor.execute(sql_insert, (fname, lname, email, phone, password_hash))
            
            # Commit changes
            connection.commit()
            
            # Get the newly created user
            with connection.cursor() as cursor:
                sql_get = "SELECT id, fname, lname, phone, email FROM user_register WHERE password = %s"
                cursor.execute(sql_get, (password_hash,))
                user = cursor.fetchone()
            
            return jsonify({"message": "User added successfully", "user": user}), 201
            
        finally:
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        connection = get_db_connection()
        
        try:
            with connection.cursor() as cursor:
                # Get all users (exclude password_hash for security)
                sql = "SELECT id, fname,lname,phone,email FROM user_register"
                cursor.execute(sql)
                users = cursor.fetchall()
            
            return jsonify({"users": users})
            
        finally:
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Authenticate a user
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        phone = data.get('phone')
        password = data.get('password')
        
        if not phone or not password:
            return jsonify({"error": "Email is required"}), 400
            
        # Hash the email for lookup
        password_hash = hash_password(password)
        
        connection = get_db_connection()
        
        try:
            with connection.cursor() as cursor:
                # Find user by email hash
                sql = "SELECT id, fname, lname, email, phone FROM user_register WHERE password = %s"
                cursor.execute(sql, (password_hash))
                user = cursor.fetchone()
            
            if user:
                return jsonify({"message": "Login successful", "user": user}), 200
            else:
                return jsonify({"error": "User not found"}), 404
                
        finally:
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============== ADMIN 

# Add a new user with hashed email
@app.route('/api/admin-register', methods=['POST'])
def add_admin():
    try:
        data = request.json
        username = data.get('username')
        user_type = data.get('user_type')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
            
        # Hash the email before storing
        password_hash = hash_password(password)
        
        # Connect to database
        connection = get_db_connection()
        
        try:
            with connection.cursor() as cursor:
                # Check if admin name already exists
                sql_check = "SELECT id FROM admin WHERE username = %s"
                cursor.execute(sql_check, (username))
                if cursor.fetchone():
                    return jsonify({"error": "Name already registered"}), 409
                
                # Insert new user
                sql_insert = "INSERT INTO admin (user_type, username, password) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert, (user_type, username, password_hash))
            
            # Commit changes
            connection.commit()
            
            # Get the newly created user
            with connection.cursor() as cursor:
                sql_get = "SELECT id, username FROM admin WHERE password = %s"
                cursor.execute(sql_get, (password_hash,))
                user = cursor.fetchone()
            
            return jsonify({"message": "User added successfully", "user": user}), 201
            
        finally:
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all admin
@app.route('/api/admin', methods=['GET'])
def get_admin():
    try:
        connection = get_db_connection()
        
        try:
            with connection.cursor() as cursor:
                # Get all admin
                sql = "SELECT id, username FROM admin"
                cursor.execute(sql)
                users = cursor.fetchall()
            
            return jsonify({"users": users})
            
        finally:
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Authenticate a user
@app.route('/api/admin-login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Email and password are required"}), 400
            
        # Hash the email for lookup
        password_hash = hash_password(password)
        
        connection = get_db_connection()
        
        try:
            with connection.cursor() as cursor:
                # Find user by email hash
                sql = "SELECT id, username FROM admin WHERE password_hash = %s"
                cursor.execute(sql, (password_hash,))
                user = cursor.fetchone()
            
            if user:
                return jsonify({"message": "Admin successful", "user": user}), 200
            else:
                return jsonify({"error": "User not found"}), 404
                
        finally:
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============== JOB APPLICATION 

# Add a new user with hashed email
@app.route('/api/apply-job', methods=['POST'])
def job_apply():
    try:
        data = request.json
        fname = data.get('fname')
        lname = data.get('lname')
        email = data.get('email')
        phone = data.get('phone')
        position = data.get('position')
        experience = data.get('experience')
        level = data.get('level')
        contract_type = data.get('contract_type')
        
        
        if not fname or not lname or not email or not phone or not position or not experience or not level or not contract_type:
            return jsonify({"error": "Fields are required"}), 400
            
        # Connect to database
        connection = get_db_connection()
        
        try:
            with connection.cursor() as cursor:
                # Check if user already applied for job
                # sql_check = "SELECT id FROM users WHERE email = %s"
                # cursor.execute(sql_check, (email))
                # if cursor.fetchone():
                #     return jsonify({"error": "Email already registered"}), 409
                
                # Insert new user
                sql_insert = "INSERT INTO jobs (fname, lname, email, phone, job_position, experience, level, contract_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql_insert, (fname, lname, email, phone, position, experience,level,contract_type))
            
            # Commit changes
            connection.commit()
            
            # Get the newly created user
            with connection.cursor() as cursor:
                sql_get = "SELECT id, fname,lname,email, phone, job_position,experience, level, contract_type FROM jobs WHERE phone = %s"
                cursor.execute(sql_get, (phone,))
                user = cursor.fetchone()
            
            return jsonify({"message": "User added successfully", "user": user}), 201
            
        finally:
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all users
@app.route('/api/get-applications', methods=['GET'])
def get_applications():
    try:
        connection = get_db_connection()
        
        try:
            with connection.cursor() as cursor:
                # Get all users (exclude email_hash for security)
                sql = "SELECT * FROM jobs"
                cursor.execute(sql)
                users = cursor.fetchall()
            
            return jsonify({"users": users})
            
        finally:
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)