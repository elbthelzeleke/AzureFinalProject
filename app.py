import pyodbc
from flask import Flask, render_template, request, redirect, url_for 

app = Flask(__name__, template_folder='frontend')

def get_db_connection():
    try:
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

# Set up your Azure SQL Database connection
""" def get_db_connection():
    try:
        # Attempt to establish a connection to the database
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=krogerretail-server.database.windows.net;'
                              'PORT=1433;'
                              'DATABASE=krogerretail-db;'
                              'UID=DB_USER;'
                              'PWD=DB_PASSWORD;')
        print("Connection to database successful!")
        return conn
    except Exception as e:
        # If the connection fails, print an error message
        print(f"Failed to connect to database: {e}")
        return None """

# Define the route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Define the route for login
@app.route('/login', methods=['POST'])
def login():
    # Get form data
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    
    # Here you can add logic to validate or process the form data
    print(f"Username: {username}, Password: {password}, Email: {email}")
    
    # Redirect to dashboard with user info (this can be more dynamic with session management)
    return redirect(url_for('dashboard', username=username))

# Define the route to display the dashboard with data pull for HSHD_NUM #10
@app.route('/dashboard/<username>')
def dashboard(username):
    # Connect to the database and fetch the data for HSHD_NUM #10
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


    cursor.execute(query, 10)  # Pull data for HSHD_NUM 10
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    # Send the welcome message along with the data to the template
    welcome_message = f"Welcome, {username}!"

    return render_template('dashboard.html', welcome_message=welcome_message, data=data)

if __name__ == "__main__":
    app.run(debug=True)