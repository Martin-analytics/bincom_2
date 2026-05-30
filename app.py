from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", 
        database="bincomphptest" 
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT uniqueid, polling_unit_name FROM polling_unit WHERE polling_unit_name != ''")
    polling_units = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', polling_units=polling_units)

@app.route('/polling-result')
def polling_result():
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
    
    cursor.execute("SELECT lga_id, lga_name FROM lga")
    lgas = cursor.fetchall()
    
    results = []
    selected_lga = None

    if request.method == 'POST':
        selected_lga = request.form.get('lga_id')
        
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
    
    return render_template('lga_results.html', lgas=lgas, results=results, selected_lga=selected_lga)

@app.route('/add-results', methods=['GET', 'POST'])
def add_results():
    if request.method == 'POST':
        pu_id = request.form.get('polling_unit_uniqueid')
        user_name = request.form.get('entered_by_user')
        
        parties = ['PDP', 'DPP', 'ACN', 'PPA', 'CDC', 'JP', 'ANPP', 'LABOUR', 'CPP']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO announced_pu_results 
            (polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user, date_entered, user_ip_address) 
            VALUES (%s, %s, %s, %s, NOW(), '127.0.0.1')
        """
        
        for party in parties:
            score = request.form.get(party)
            if score and score.isdigit(): 
                cursor.execute(insert_query, (pu_id, party, score, user_name))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return "Results successfully added!" 
        
    return render_template('add_result.html')


@app.route('/api/lgas')
def get_lgas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT lga_id, lga_name FROM lga WHERE state_id = 25")
    lgas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(lgas)

@app.route('/api/wards/<int:lga_id>')
def get_wards(lga_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT ward_id, ward_name FROM ward WHERE lga_id = %s", (lga_id,))
    wards = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(wards)

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