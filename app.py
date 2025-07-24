from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import get_db_connection
import hashlib
from datetime import datetime
import pickle
import numpy as np
import logging
from flask_cors import CORS
import os
from health_model import HealthModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_recommendations(input_data, health_score):
    recommendations = []
    
    # Sleep recommendations
    sleep_hours = input_data['sleep_hours']
    if sleep_hours < 6:
        recommendations.append({
            'category': 'Sleep',
            'message': 'Your sleep duration is very low. Aim for 7-9 hours per night for optimal health.',
            'priority': 'critical'
        })
    elif 6 <= sleep_hours < 7:
        recommendations.append({
            'category': 'Sleep',
            'message': 'Your sleep could improve. Try to get 7-9 hours of quality sleep each night.',
            'priority': 'high'
        })
    
    # Exercise recommendations
    exercise_days = input_data['exercise_days']
    if exercise_days < 2:
        recommendations.append({
            'category': 'Exercise',
            'message': 'You exercise very little. Aim for at least 150 minutes of moderate activity per week.',
            'priority': 'critical'
        })
    elif 2 <= exercise_days < 4:
        recommendations.append({
            'category': 'Exercise',
            'message': 'Consider increasing your activity level to 4-5 days per week for better health.',
            'priority': 'high'
        })
    
    # Diet recommendations
    diet_quality = input_data['diet_quality']
    if diet_quality < 4:
        recommendations.append({
            'category': 'Diet',
            'message': 'Your diet needs significant improvement. Focus on whole foods, fruits and vegetables.',
            'priority': 'critical'
        })
    elif 4 <= diet_quality < 7:
        recommendations.append({
            'category': 'Diet',
            'message': 'Your diet could be healthier. Try to reduce processed foods and increase nutrient density.',
            'priority': 'high'
        })
    
    # Hydration recommendations
    water_glasses = input_data['water_glasses']
    if water_glasses < 4:
        recommendations.append({
            'category': 'Hydration',
            'message': 'You seem dehydrated. Aim for 6-8 glasses of water daily.',
            'priority': 'high'
        })
    elif 4 <= water_glasses < 6:
        recommendations.append({
            'category': 'Hydration',
            'message': 'Your hydration is okay but could improve. Try drinking more water throughout the day.',
            'priority': 'medium'
        })
    
    # Stress recommendations
    stress_level = input_data['stress_level']
    if stress_level >= 8:
        recommendations.append({
            'category': 'Stress',
            'message': 'Your stress levels are very high. Consider meditation, deep breathing, or professional help.',
            'priority': 'critical'
        })
    elif 6 <= stress_level < 8:
        recommendations.append({
            'category': 'Stress',
            'message': 'Your stress levels are elevated. Try relaxation techniques or reducing stressors.',
            'priority': 'high'
        })
    
    # BMI/Weight recommendations
    bmi = input_data['weight_kg'] / ((input_data['height_cm']/100) ** 2)
    bmi_category = HealthModel.calculate_bmi_category(bmi)
    if bmi_category in ['Underweight', 'Obese']:
        recommendations.append({
            'category': 'Weight',
            'message': f'Your BMI indicates {bmi_category}. Consider consulting a nutritionist for personalized advice.',
            'priority': 'critical'
        })
    elif bmi_category == 'Overweight':
        recommendations.append({
            'category': 'Weight',
            'message': 'Your BMI indicates you may be overweight. Small dietary changes can make a big difference.',
            'priority': 'high'
        })
    
    # General recommendations
    if health_score < 50:
        recommendations.append({
            'category': 'General',
            'message': 'Your overall health needs significant attention. Consider a comprehensive health checkup.',
            'priority': 'critical'
        })
    elif 50 <= health_score < 70:
        recommendations.append({
            'category': 'General',
            'message': 'Your health is fair but has room for improvement. Focus on one area at a time.',
            'priority': 'high'
        })
    
    return recommendations



app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['TEMPLATES_AUTO_RELOAD'] = True
health_model = HealthModel()

# Combined application routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('html_page'))  # Changed from dashboard to html_page
    return render_template('Home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('html_page'))  # Redirect to html.html if already logged in
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "danger")
            return redirect(url_for('login'))
            
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM register WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['first_name'] = user.get('first_name', 'User')
                return redirect(url_for('html_page'))  # Redirect to html.html after login
            else:
                flash('Invalid email or password', 'danger')
        except Exception as e:
            flash(f"Login error: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('html_page'))  # Redirect to html.html if already logged in
        
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        dob = request.form.get('date_of_birth')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([first_name, last_name, email, dob, password, confirm_password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "danger")
            return redirect(url_for('register'))
            
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM register WHERE email=%s", (email,))
            if cursor.fetchone():
                flash('Email already exists', 'danger')
                return redirect(url_for('register'))
            
            cursor.execute(
                """INSERT INTO register 
                (first_name, last_name, email, date_of_birth, password) 
                VALUES (%s, %s, %s, %s, %s)""",
                (first_name, last_name, email, dob, hashed_password)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash(f'Registration error: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

# New route to serve html.html
@app.route('/tracker')
def html_page():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    return render_template('tracker.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        input_data = request.get_json()
        
        features = {
            'age': float(input_data['age']),
            'gender': input_data['gender'],
            'weight_kg': float(input_data['weight_kg']),
            'height_cm': float(input_data['height_cm']),
            'sleep_hours': float(input_data['sleep_hours']),
            'water_glasses': float(input_data['water_glasses']),
            'diet_quality': float(input_data['diet_quality']),
            'exercise_days': float(input_data['exercise_days']),
            'stress_level': float(input_data['stress_level'])
        }
        
        health_score = health_model.predict_health(features)
        health_score = max(0, min(100, round(health_score, 1)))
        
        bmi = features['weight_kg'] / ((features['height_cm']/100) ** 2)
        recommendations = generate_recommendations(features, health_score)
        
        response = {
            'result': {
                'score': health_score,
                'status': HealthModel.get_health_status(health_score),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'metrics': {
                    'bmi': round(bmi, 1),
                    'bmi_category': HealthModel.calculate_bmi_category(bmi),
                    'sleep_hours': features['sleep_hours'],
                    'exercise_days': features['exercise_days'],
                    'water_glasses': features['water_glasses']
                },
                'recommendations': recommendations
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400      
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)