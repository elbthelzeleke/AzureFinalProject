import pyodbc
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder='frontend')

def get_db_connection():
    try:
        DB_USER = os.environ['DB_USER']
        DB_PASSWORD = os.environ['DB_PASSWORD']
        DB_SERVER = os.environ['DB_SERVER']
        DB_DATABASE = os.environ['DB_DATABASE']
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                              f'SERVER={DB_SERVER};'
                              f'PORT=1433;'
                              f'DATABASE={DB_DATABASE};'
                              f'UID={DB_USER};'
                              f'PWD={DB_PASSWORD};')
        print("Connection to database successful!")
        return conn
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        raise Exception(f"Database connection error: {e}")

# Define the route for the home page
# Define the route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Define the route to display the dashboard with data pull for HSHD_NUM
@app.route('/dashboard/<username>', methods=['GET', 'POST'])
def dashboard(username):
    # Get HSHD_NUM from the query string (default to 10 if not provided)
    hshd_num = request.args.get('hshd_num', default=10, type=int)
    
    # Connect to the database and fetch the data for the requested HSHD_NUM
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT
        h.Hshd_num,
        t.Basket_num,
        t.Year,
        t.Product_num,
        p.Department,
        p.Commodity
    FROM
        Households h
    JOIN
        Transactions t ON h.Hshd_num = t.Hshd_num
    JOIN
        Products p ON t.Product_num = p.Product_num
    WHERE
        h.Hshd_num = ?
    ORDER BY
        h.Hshd_num, t.Basket_num, t.Year, t.Product_num, p.Department, p.Commodity;
    '''

    cursor.execute(query, hshd_num)  # Fetch data for dynamic HSHD_NUM
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    # Send the welcome message along with the data to the template
    welcome_message = f"Welcome, {username}!"
    search_message = "Search Results" if hshd_num else ""

    return render_template('dashboard.html', welcome_message=welcome_message, data=data, hshd_num=hshd_num, search_message=search_message)

# Define the search route
@app.route('/search_dashboard', methods=['GET', 'POST'])
def search_dashboard():
    # Get the search HSHD_NUM from the form
    hshd_num = request.args.get('hshd_num', default=10, type=int)

    # Connect to the database and fetch the data for the requested HSHD_NUM
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT
        h.Hshd_num,
        t.Basket_num,
        t.Year,
        t.Product_num,
        p.Department,
        p.Commodity
    FROM
        Households h
    JOIN
        Transactions t ON h.Hshd_num = t.Hshd_num
    JOIN
        Products p ON t.Product_num = p.Product_num
    WHERE
        h.Hshd_num = ?
    ORDER BY
        h.Hshd_num, t.Basket_num, t.Year, t.Product_num, p.Department, p.Commodity;
    '''
    
    cursor.execute(query, hshd_num)  # Fetch data for dynamic HSHD_NUM
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    search_message = "Search Results" if hshd_num else "No results for empty search."

    return render_template('dashboard.html', welcome_message="Search Results", data=data, hshd_num=hshd_num, search_message=search_message)

if __name__ == "__main__":
    app.run(debug=True)
