from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root", # Change to your MySQL user
        password="", # Change to your MySQL password
        database="bincomphptest" # The DB name inside the file is actually bincomphptest
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all polling units to populate your index.html dropdown
    cursor.execute("SELECT uniqueid, polling_unit_name FROM polling_unit WHERE polling_unit_name != ''")
    polling_units = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', polling_units=polling_units)

@app.route('/polling-result')
def polling_result():
    # This grabs the value submitted from the index.html dropdown
    uniqueid = request.args.get('polling_unit_id') 
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT party_abbreviation, party_score 
        FROM announced_pu_results 
        WHERE polling_unit_uniqueid = %s
    """
    cursor.execute(query, (uniqueid,))
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('polling_unit.html', results=results, pu_id=uniqueid)

@app.route('/lga-results', methods=['GET', 'POST'])
def lga_results():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Always fetch LGAs for the dropdown
    cursor.execute("SELECT lga_id, lga_name FROM lga")
    lgas = cursor.fetchall()
    
    results = []
    selected_lga = None

    if request.method == 'POST':
        selected_lga = request.form.get('lga_id')
        
        # The crucial JOIN query
        query = """
            SELECT r.party_abbreviation, SUM(r.party_score) as total_score
            FROM announced_pu_results r
            JOIN polling_unit p ON r.polling_unit_uniqueid = p.uniqueid
            WHERE p.lga_id = %s
            GROUP BY r.party_abbreviation
        """
        cursor.execute(query, (selected_lga,))
        results = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('lga_result.html', lgas=lgas, results=results, selected_lga=selected_lga)

@app.route('/add-results', methods=['GET', 'POST'])
def add_results():
    if request.method == 'POST':
        pu_id = request.form.get('polling_unit_uniqueid')
        user_name = request.form.get('entered_by_user')
        
        # List of expected parties from the 'party' table
        parties = ['PDP', 'DPP', 'ACN', 'PPA', 'CDC', 'JP', 'ANPP', 'LABOUR', 'CPP']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO announced_pu_results 
            (polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user, date_entered, user_ip_address) 
            VALUES (%s, %s, %s, %s, NOW(), '127.0.0.1')
        """
        
        # Loop through each party to see if a score was submitted
        for party in parties:
            score = request.form.get(party)
            if score and score.isdigit(): # Ensure it's a valid number
                cursor.execute(insert_query, (pu_id, party, score, user_name))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return "Results successfully added!" # In a real app, redirect or flash a success message
        
    return render_template('add_result.html')

# 1. API route to get all LGAs (Delta State is ID 25)
@app.route('/api/lgas')
def get_lgas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # We filter by state_id = 25 since the database only contains Delta state data
    cursor.execute("SELECT lga_id, lga_name FROM lga WHERE state_id = 25")
    lgas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(lgas)

# 2. API route to get Wards based on the selected LGA
@app.route('/api/wards/<int:lga_id>')
def get_wards(lga_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT ward_id, ward_name FROM ward WHERE lga_id = %s", (lga_id,))
    wards = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(wards)

# 3. API route to get Polling Units based on the selected Ward
@app.route('/api/polling-units/<int:ward_id>')
def get_polling_units(ward_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT uniqueid, polling_unit_name FROM polling_unit WHERE ward_id = %s", (ward_id,))
    polling_units = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(polling_units)

if __name__ == '__main__':
    app.run(debug=True)