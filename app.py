import plotly
import pyodbc
import os
from flask import Flask, render_template, request, redirect, url_for
import plotly.express as px
import pandas as pd
import json


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

    cursor.execute(query, hshd_num)  # Use dynamic HSHD_NUM from query string
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    # Send the welcome message along with the data to the template
    welcome_message = f"Welcome, {username}!"

    return render_template('dashboard.html', welcome_message=welcome_message, data=data, hshd_num=hshd_num)

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

    return render_template('dashboard.html', welcome_message="Search Results", data=data, hshd_num=hshd_num)

@app.route('/basket_analysis', methods=['GET'])
def basket_analysis():
    department = request.args.get('department', default="Food", type=str)

    # Connect to the database and fetch the data based on selected department
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT
        t.Basket_num,
        t.Product_num,
        p.Department
    FROM
        Transactions t
    JOIN
        Products p ON t.Product_num = p.Product_num
    WHERE
        p.Department = ?
    '''
    cursor.execute(query, department)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Process the data for product combinations in the same basket
    df = pd.DataFrame(data, columns=['Basket_num', 'Product_num', 'Department'])
    basket_combinations = df.groupby('Basket_num')['Product_num'].apply(lambda x: list(x)).reset_index()

    # Create a new DataFrame to track product combinations
    product_combinations = []
    for _, basket in basket_combinations.iterrows():
        products = basket['Product_num']
        for i in range(len(products)):
            for j in range(i + 1, len(products)):
                product_combinations.append((products[i], products[j]))

    combo_df = pd.DataFrame(product_combinations, columns=['Product_1', 'Product_2'])

    # Count occurrences of each combination
    combo_counts = combo_df.groupby(['Product_1', 'Product_2']).size().reset_index(name='Count')

    # Create the bar chart using Plotly
    fig = px.bar(combo_counts, x='Count', y='Product_1', color='Product_2', title=f'Product Combinations in {department} Department')
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('dashboard.html', graph_json=graph_json)

if __name__ == "__main__":
    app.run(debug=True)