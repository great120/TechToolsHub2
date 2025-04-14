# app.py
from flask import Flask, render_template, request, jsonify, send_file, url_for, redirect
import qrcode
from io import BytesIO
import base64
import cv2
import numpy as np
import math
import datetime
import pytesseract
import pdf2image
import os
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tech_tools_hub_secret_key'
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Tools page
@app.route('/tools')
def tools():
    return render_template('tools.html')

# About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Privacy Policy page
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# Individual tool routes
@app.route('/tools/qr-generator', methods=['GET', 'POST'])
def qr_generator():
    qr_image = None
    if request.method == 'POST':
        data = request.form.get('data', '')
        if data:
            img = qrcode.make(data)
            buffered = BytesIO()
            img.save(buffered)
            qr_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return render_template('tools/qr_generator.html', qr_image=qr_image)

@app.route('/tools/text-extraction', methods=['GET', 'POST'])
def text_extraction():
    extracted_text = None
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('tools/text_extraction.html', error="No file uploaded")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('tools/text_extraction.html', error="No file selected")
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Check if PDF or image
        if filename.lower().endswith('.pdf'):
            pages = pdf2image.convert_from_path(filepath)
            extracted_text = ""
            for page in pages:
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], f"page_{pages.index(page)}.jpg")
                page.save(img_path, 'JPEG')
                extracted_text += pytesseract.image_to_string(img_path) + "\n\n"
                os.remove(img_path)  # Clean up temporary files
        else:
            # Assume it's an image
            img = cv2.imread(filepath)
            extracted_text = pytesseract.image_to_string(img)
        
        os.remove(filepath)  # Clean up temporary files
    
    return render_template('tools/text_extraction.html', extracted_text=extracted_text)

@app.route('/tools/scientific-calculator')
def scientific_calculator():
    return render_template('tools/scientific_calculator.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression', '')
    
    try:
        # Replace mathematical expressions with Python equivalents
        expression = expression.replace('^', '**')
        expression = expression.replace('sin(', 'math.sin(')
        expression = expression.replace('cos(', 'math.cos(')
        expression = expression.replace('tan(', 'math.tan(')
        expression = expression.replace('log(', 'math.log10(')
        expression = expression.replace('ln(', 'math.log(')
        expression = expression.replace('sqrt(', 'math.sqrt(')
        expression = expression.replace('π', 'math.pi')
        expression = expression.replace('e', 'math.e')
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": None}, {"math": math})
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/tools/date-difference')
def date_difference():
    return render_template('tools/date_difference.html')

@app.route('/api/date-difference', methods=['POST'])
def calculate_date_difference():
    data = request.get_json()
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        
        difference = end_date - start_date
        days = difference.days
        
        # Calculate years, months, weeks
        years = days // 365
        remaining_days = days % 365
        months = remaining_days // 30
        remaining_days = remaining_days % 30
        weeks = remaining_days // 7
        remaining_days = remaining_days % 7
        
        return jsonify({
            "days": days,
            "weeks": int(days / 7),
            "months": int(days / 30),
            "years": int(days / 365),
            "detailed": {
                "years": years,
                "months": months,
                "weeks": weeks,
                "days": remaining_days
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/tools/bmi-calculator')
def bmi_calculator():
    return render_template('tools/bmi_calculator.html')

@app.route('/api/calculate-bmi', methods=['POST'])
def calculate_bmi():
    data = request.get_json()
    weight = float(data.get('weight', 0))
    height = float(data.get('height', 0))
    unit = data.get('unit', 'metric')
    
    if unit == 'metric':
        # Weight in kg, height in cm
        bmi = weight / ((height / 100) ** 2)
    else:
        # Weight in lbs, height in inches
        bmi = (weight / (height ** 2)) * 703
    
    # Determine BMI category
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return jsonify({
        "bmi": round(bmi, 2),
        "category": category
    })

@app.route('/tools/age-calculator')
def age_calculator():
    return render_template('tools/age_calculator.html')

@app.route('/api/calculate-age', methods=['POST'])
def calculate_age():
    data = request.get_json()
    dob_str = data.get('dob')
    
    try:
        dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d')
        today = datetime.datetime.now()
        
        years = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            years -= 1
            
        # Calculate next birthday
        next_birthday = datetime.datetime(today.year, dob.month, dob.day)
        if next_birthday < today:
            next_birthday = datetime.datetime(today.year + 1, dob.month, dob.day)
        
        days_to_next_birthday = (next_birthday - today).days
        
        # Calculate total days, months, weeks
        delta = today - dob
        total_days = delta.days
        total_months = years * 12 + (today.month - dob.month)
        total_weeks = total_days // 7
        
        return jsonify({
            "years": years,
            "months": total_months,
            "weeks": total_weeks,
            "days": total_days,
            "next_birthday_in_days": days_to_next_birthday
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/tools/percentage-calculator')
def percentage_calculator():
    return render_template('tools/percentage_calculator.html')

@app.route('/api/calculate-percentage', methods=['POST'])
def calculate_percentage():
    data = request.get_json()
    calculation_type = data.get('type')
    
    try:
        if calculation_type == 'percentage_of':
            percentage = float(data.get('percentage', 0))
            value = float(data.get('value', 0))
            result = (percentage / 100) * value
            return jsonify({"result": result})
            
        elif calculation_type == 'percentage_change':
            original = float(data.get('original', 0))
            new_value = float(data.get('new_value', 0))
            change = new_value - original
            percentage_change = (change / original) * 100
            return jsonify({
                "change": change,
                "percentage_change": percentage_change
            })
            
        elif calculation_type == 'percentage_score':
            correct = float(data.get('correct', 0))
            total = float(data.get('total', 0))
            percentage = (correct / total) * 100
            return jsonify({"percentage": percentage})
            
        return jsonify({"error": "Invalid calculation type"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/tools/unit-converter')
def unit_converter():
    return render_template('tools/unit_converter.html')

@app.route('/api/convert-unit', methods=['POST'])
def convert_unit():
    data = request.get_json()
    category = data.get('category')
    from_unit = data.get('from_unit')
    to_unit = data.get('to_unit')
    value = float(data.get('value', 0))
    
    # Conversion factors
    conversions = {
        'length': {
            # Base unit: meters
            'mm': 0.001,
            'cm': 0.01,
            'm': 1,
            'km': 1000,
            'inch': 0.0254,
            'foot': 0.3048,
            'yard': 0.9144,
            'mile': 1609.34
        },
        'weight': {
            # Base unit: grams
            'mg': 0.001,
            'g': 1,
            'kg': 1000,
            'oz': 28.3495,
            'lb': 453.592,
            'stone': 6350.29,
            'ton': 907185
        },
        'temperature': {
            # Special case, handled separately
            'celsius': 'C',
            'fahrenheit': 'F',
            'kelvin': 'K'
        },
        'area': {
            # Base unit: square meters
            'sq_m': 1,
            'sq_km': 1000000,
            'sq_ft': 0.092903,
            'sq_yd': 0.836127,
            'acre': 4046.86,
            'hectare': 10000
        },
        'volume': {
            # Base unit: liters
            'ml': 0.001,
            'l': 1,
            'cu_m': 1000,
            'cu_ft': 28.3168,
            'fl_oz': 0.0295735,
            'pint': 0.473176,
            'gallon': 3.78541
        }
    }
    
    try:
        if category == 'temperature':
            # Temperature conversions require special formulas
            if from_unit == 'celsius' and to_unit == 'fahrenheit':
                result = (value * 9/5) + 32
            elif from_unit == 'celsius' and to_unit == 'kelvin':
                result = value + 273.15
            elif from_unit == 'fahrenheit' and to_unit == 'celsius':
                result = (value - 32) * 5/9
            elif from_unit == 'fahrenheit' and to_unit == 'kelvin':
                result = ((value - 32) * 5/9) + 273.15
            elif from_unit == 'kelvin' and to_unit == 'celsius':
                result = value - 273.15
            elif from_unit == 'kelvin' and to_unit == 'fahrenheit':
                result = ((value - 273.15) * 9/5) + 32
            else:
                result = value  # Same unit
                
        else:
            # For other units, convert to base unit first, then to target unit
            base_value = value * conversions[category][from_unit]
            result = base_value / conversions[category][to_unit]
            
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)