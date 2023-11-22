@app.route('/')
def home():
    return render_template('home.html')


@app.route('/runs', methods=['POST'])
def query1():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""SELECT BATSMAN,SUM(BATSMAN_RUNS) FROM BALL_BY_BALL
GROUP BY BATSMAN ORDER BY SUM(BATSMAN_RUNS) DESC LIMIT 10""")
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    formatted_data = [f'{name}: {runs}' for name,runs in results]
    
    return render_template('general.html', data1=formatted_data)

@app.route('/wickets', methods=['POST'])
def query2():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""SELECT BOWLER,SUM(IS_WICKET) FROM BALL_BY_BALL 
GROUP BY BOWLER ORDER BY SUM(IS_WICKET) DESC LIMIT 10""")
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    formatted_data = [f'{name}: {wickets}' for name,wickets in results]

    return render_template('general.html', data2=formatted_data)

@app.route('/matches',methods=['POST'])
def query3(): 
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('SELECT YEAR(DATE),COUNT(*) FROM MATCHES GROUP BY YEAR(DATE)')
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    formatted_data = [f'{year}: {matches}' for year,matches in results]

    return render_template('general.html',data3=formatted_data)

@app.route('/dismissals',methods=['POST'])
def query4(): 
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""SELECT DISMISSAL_KIND,COUNT(*) FROM BALL_BY_BALL WHERE DISMISSAL_KIND!='NA'
GROUP BY DISMISSAL_KIND""")
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    formatted_data = [f'{dismissal_mode}: {count}' for dismissal_mode,count in results]

    return render_template('general.html',data4=formatted_data) 