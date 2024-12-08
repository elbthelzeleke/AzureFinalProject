from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__, template_folder='frontend')

# Set up the SQLAlchemy engine and session
def get_db_connection():
    try:
        # SQLAlchemy engine creation using the credentials from environment variables
        engine = create_engine(f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{1433}/{DB_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server')
        Session = sessionmaker(bind=engine)
        session = Session()
        print("Connection to database successful!")
        return session
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
@app.route('/dashboard/<username>')
def dashboard(username):
    # Connect to the database and fetch the data for HSHD_NUM #10
    session = get_db_connection()

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
        h.Hshd_num = :hshd_num
    ORDER BY
        h.Hshd_num, t.Basket_num, t.Year, t.Product_num, p.Department, p.Commodity;
    '''

    result = session.execute(query, {'hshd_num': 10})  # Pull data for HSHD_NUM 10
    data = result.fetchall()

    session.close()

    # Send the welcome message along with the data to the template
    welcome_message = f"Welcome, {username}!"

    return render_template('dashboard.html', welcome_message=welcome_message, data=data)

if __name__ == "__main__":
    app.run(debug=True)
