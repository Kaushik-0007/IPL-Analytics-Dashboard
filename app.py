from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
import mysql.connector


app = Flask(__name__)
app.secret_key = 'your_secret_key' 


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kaushik2003',
    'database': 'IPL',
}

def authenticate_user(username, password):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def check_authentication(template, **data):
    username = request.args.get('username')
    if username:
        return render_template(template, username=username, **data)
    else:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

@app.route('/')
def default():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT Count FROM UserCount')
        user_count = cursor.fetchone()[0]

        return render_template('default.html', user_count=user_count)
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'})

    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = authenticate_user(username, password)

        if user:
            return render_template('login.html', success='Successfully logged in!',redirect_url=url_for('home',username=username))
        else:
            return render_template('login.html', error='Invalid Username or Password')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('register.html', error='Please provide both username and password.')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template('register.html', error='Username already taken. Please choose a different one.')

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('register.html', success='Successfully registered!',redirect_url=url_for('login'))

    return render_template('register.html')

@app.route('/home')
def home():
    username = request.args.get('username')
    
    if username:
        return render_template('home.html', username=username)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/admin', methods=['GET'])
def admin():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users')
    users_data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin.html', users=users_data)

@app.route('/insert_user', methods=['POST'])
def insert_user():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        new_username = request.form['newUsername']
        new_password = request.form['newPassword']

        cursor.execute('INSERT INTO Users (username, password) VALUES (%s, %s)', (new_username, new_password))
        
        conn.commit()
        return jsonify({'message': 'Successfully inserted'})
    except Exception as e:
        return jsonify({'message': f'Error: User with username {new_username} is already taken'})

    finally:
        cursor.close()
        conn.close()

from flask import request, jsonify

# Assuming db_config and app are already defined...

@app.route('/update_user', methods=['POST'])
def update_user():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        user_id_to_update = request.form['updateUserId']
        new_username = request.form['updateUsername']
        new_password = request.form['updatePassword']

        cursor.execute('SELECT * FROM Users WHERE ID = %s', (user_id_to_update,))
        
        user_data = cursor.fetchall()
        if not user_data:
            return jsonify({'message': f'Error: User with ID {user_id_to_update} not found'})

        cursor.execute('UPDATE Users SET username = %s, password = %s WHERE ID = %s',
                       (new_username, new_password, user_id_to_update))
        conn.commit()

        return jsonify({'message': 'Successfully updated'})
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'})

    finally:
        cursor.close()
        conn.close()


@app.route('/delete_user', methods=['POST'])
def delete_user():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        user_id_to_delete = request.form['deleteUserId']

        cursor.execute('DELETE FROM Users WHERE ID = %s', (user_id_to_delete,))
        if cursor.rowcount == 0:
            return jsonify({'message': f'Error: User with ID {user_id_to_delete} not found'})

        cursor.fetchall()  

        conn.commit()

        return jsonify({'message': 'Successfully deleted'})
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'})

    finally:
        cursor.close()
        conn.close()


@app.route('/general', methods=['GET','POST'])
def general():

    if request.method == 'POST':
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            batter_input_year = request.form.get('batterinputYear')
            bowler_input_year = request.form.get('bowlerinputYear')

            cursor.execute('UPDATE BatterInputYear SET Season = %s', (batter_input_year,))
            conn.commit()
            cursor.execute('UPDATE BowlerInputYear SET Season = %s', (bowler_input_year,))
            conn.commit()

            cursor.execute("""SELECT BATSMAN, SUM(BATSMAN_RUNS) FROM BALL_BY_BALL
                              GROUP BY BATSMAN ORDER BY SUM(BATSMAN_RUNS) DESC LIMIT 10""")
            runs_results = cursor.fetchall()

            cursor.execute("""SELECT BOWLER, SUM(IS_WICKET) FROM BALL_BY_BALL 
                              GROUP BY BOWLER ORDER BY SUM(IS_WICKET) DESC LIMIT 10""")
            wickets_results = cursor.fetchall()

            cursor.execute('SELECT YEAR(DATE), COUNT(*) FROM MATCHES GROUP BY YEAR(DATE)')
            matches_results = cursor.fetchall()

            cursor.execute("""SELECT DISMISSAL_KIND, COUNT(*) FROM BALL_BY_BALL 
                              WHERE DISMISSAL_KIND != 'NA' GROUP BY DISMISSAL_KIND""")
            dismissals_results = cursor.fetchall()

            # Transform data into appropriate format
            runs_data = [f'{name}: {runs}' for name, runs in runs_results]
            wickets_data = [f'{name}: {wickets}' for name, wickets in wickets_results]
            matches_data = [f'{year}: {matches}' for year, matches in matches_results]
            dismissals_data = [f'{dismissal_mode}: {count}' for dismissal_mode, count in dismissals_results]


            return render_template('general.html',data1=runs_data, data2=wickets_data, data3=matches_data, data4=dismissals_data)

        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'})

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Query 1: Leading Run Scorers
    cursor.execute("""SELECT BATSMAN, SUM(BATSMAN_RUNS) FROM BALL_BY_BALL
                    GROUP BY BATSMAN ORDER BY SUM(BATSMAN_RUNS) DESC LIMIT 10""")
    runs_results = cursor.fetchall()

    # Query 2: Leading Wicket Takers
    cursor.execute("""SELECT BOWLER, SUM(IS_WICKET) FROM BALL_BY_BALL 
                    GROUP BY BOWLER ORDER BY SUM(IS_WICKET) DESC LIMIT 10""")
    wickets_results = cursor.fetchall()

    # Query 3: Matches Per Season
    cursor.execute('SELECT YEAR(DATE), COUNT(*) FROM MATCHES GROUP BY YEAR(DATE)')
    matches_results = cursor.fetchall()

    # Query 4: Number of Dismissals per Dismissal Mode
    cursor.execute("""SELECT DISMISSAL_KIND, COUNT(*) FROM BALL_BY_BALL 
                    WHERE DISMISSAL_KIND != 'NA' GROUP BY DISMISSAL_KIND""")
    
    dismissals_results = cursor.fetchall()

    cursor.close()
    conn.close()

    runs_data = [f'{name}: {runs}' for name, runs in runs_results]
    wickets_data = [f'{name}: {wickets}' for name, wickets in wickets_results]
    matches_data = [f'{year}: {matches}' for year, matches in matches_results]
    dismissals_data = [f'{dismissal_mode}: {count}' for dismissal_mode, count in dismissals_results]

    return check_authentication('general.html',data1=runs_data, data2=wickets_data, data3=matches_data, data4=dismissals_data)

    
@app.route('/individual', methods=['GET'])
def individual():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Query 1: Highest Run-Scorer Each Season
    cursor.execute("""SELECT PlayerName, RunsScored
FROM (
    SELECT YEAR(M.DATE) AS Year, BB.BATSMAN AS PlayerName, SUM(BB.BATSMAN_RUNS) AS RunsScored,
           RANK() OVER(PARTITION BY YEAR(M.DATE) ORDER BY SUM(BB.BATSMAN_RUNS) DESC) AS RunRank
    FROM BALL_BY_BALL BB
    JOIN MATCHES M ON BB.MATCH_ID = M.MATCH_ID
    WHERE YEAR(M.DATE) BETWEEN 2008 AND 2020
    GROUP BY Year, PlayerName
) AS SeasonLeaders
WHERE RunRank = 1
ORDER BY Year""")
    runs_results = cursor.fetchall()

    # Query 2: Highest Wicket-Taker Each Season
    cursor.execute("""SELECT PlayerName, WicketsTaken
FROM (
    SELECT YEAR(M.DATE) AS Year, BB.BOWLER AS PlayerName, COUNT(*) AS WicketsTaken,
           RANK() OVER(PARTITION BY YEAR(M.DATE) ORDER BY COUNT(*) DESC) AS WicketRank
    FROM BALL_BY_BALL BB
    JOIN MATCHES M ON BB.MATCH_ID = M.MATCH_ID
    WHERE YEAR(M.DATE) BETWEEN 2008 AND 2020
    AND BB.IS_WICKET = 1
    GROUP BY Year, PlayerName
) AS SeasonLeaders
WHERE WicketRank = 1
ORDER BY Year
""")
    wickets_results = cursor.fetchall()

    # Query 3: Most Runs in Winning Cause
    cursor.execute("""SELECT BB.BATSMAN, SUM(BB.BATSMAN_RUNS) AS TotalRuns
FROM BALL_BY_BALL BB
JOIN MATCHES M ON BB.MATCH_ID = M.MATCH_ID
WHERE BB.BATSMAN_RUNS > 0
AND YEAR(M.DATE) BETWEEN 2008 AND 2020
AND M.WINNER = BB.BATTING_TEAM
GROUP BY BB.BATSMAN
ORDER BY TotalRuns DESC
LIMIT 10""")
    winning_runs_results = cursor.fetchall()

    # Query 4: Most Wickets in Winning Cause 
    cursor.execute("""SELECT BB.BOWLER, COUNT(*) AS WicketsInMatchesWon
FROM BALL_BY_BALL BB
JOIN MATCHES M ON BB.MATCH_ID = M.MATCH_ID
WHERE BB.IS_WICKET = 1
AND YEAR(M.DATE) BETWEEN 2008 AND 2020
AND M.WINNER = BB.BOWLING_TEAM
GROUP BY BB.BOWLER
ORDER BY WicketsInMatchesWon DESC
LIMIT 10
""")
    
    dismissals_results = cursor.fetchall()

    cursor.close()
    conn.close()

    runs_data = [f'{name}: {runs}' for name, runs in runs_results]
    wickets_data = [f'{name}: {wickets}' for name, wickets in wickets_results]
    matches_data = [f'{name}: {runs}' for name, runs in winning_runs_results]
    dismissals_data = [f'{dismissal_mode}: {count}' for dismissal_mode, count in dismissals_results]


    return check_authentication('individual.html',data1=runs_data, data2=wickets_data, data3=matches_data, data4=dismissals_data)


@app.route('/team', methods=['GET'])
def team():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Query 1: Total Matches Played By Each Team
    cursor.execute("""SELECT TEAM, COUNT(*) AS TOTAL_MATCHES_PLAYED
FROM (
    SELECT TEAM1 AS TEAM FROM MATCHES
    UNION ALL
    SELECT TEAM2 AS TEAM FROM MATCHES
) AS Teams
GROUP BY TEAM
ORDER BY TOTAL_MATCHES_PLAYED DESC""")
    count_matches_results = cursor.fetchall()

    # Query 2: Teams with Most Wins
    cursor.execute("""SELECT WINNER, COUNT(*) AS TOTAL_WINS FROM MATCHES
GROUP BY WINNER ORDER BY TOTAL_WINS DESC""")
    wins_results = cursor.fetchall()

    # Query 3: Teams with the Most Matches Played at Neutral Venues
    cursor.execute("""SELECT TEAM, COUNT(*) AS MATCHES_AT_NEUTRAL_VENUES
FROM (
    SELECT TEAM1 AS TEAM FROM MATCHES WHERE NEUTRAL_VENUE = 1
    UNION ALL
    SELECT TEAM2 AS TEAM FROM MATCHES WHERE NEUTRAL_VENUE = 1
) AS NeutralVenueTeams
GROUP BY TEAM
ORDER BY MATCHES_AT_NEUTRAL_VENUES DESC""")
    neutral_matches_results = cursor.fetchall()

    # Query 4: Total Boundaries (4s and 6s) Hit by Each Team
    cursor.execute("""SELECT BATTING_TEAM AS Team, 
       SUM(CASE WHEN NON_BOUNDARY = 0 THEN 1 ELSE 0 END) AS TOTAL_BOUNDARIES
FROM BALL_BY_BALL
GROUP BY Team
ORDER BY TOTAL_BOUNDARIES DESC""")
    
    boundaries_results = cursor.fetchall()

    #Query 5: Teams Win Percentage 

    cursor.callproc('CalculateTeamWinPercentage')
    result_cursor = conn.cursor()
    result_cursor.execute("SELECT * FROM result_of_calculate_team_win_percentage")

    team_win_results = result_cursor.fetchall()

    cursor.close()
    conn.close()

    runs_data = [f'{team}: {matches}' for team, matches in count_matches_results]
    wickets_data = [f'{team}: {wins}' for team, wins in wins_results]
    matches_data = [f'{team}: {matches}' for team, matches in neutral_matches_results]
    dismissals_data = [f'{team}: {boundaries}' for team, boundaries in boundaries_results]
    team_win_data = [f'{row[0]}: {row[1]}' for row in team_win_results]

    return check_authentication('team.html',data1=runs_data, data2=wickets_data, data3=matches_data, data4=dismissals_data,data5=team_win_data)



if __name__ == '__main__':
    app.run(debug=True)


"""
CREATE TRIGGER after_insert_user
AFTER INSERT ON Users
FOR EACH ROW
BEGIN
    UPDATE UserCount SET Count = Count + 1;
END; //


CREATE TRIGGER after_delete_user
AFTER DELETE ON Users
FOR EACH ROW
BEGIN
    UPDATE UserCount SET Count = Count - 1;
END; //
"""