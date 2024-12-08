from flask import Flask, render_template, request

app = Flask(__name__, template_folder='frontend')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # Get form data
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    
    # Here you can add logic to validate or process the form data
    print(f"Username: {username}, Password: {password}, Email: {email}")
    
    # For now, just return a simple response with the username
    return f"Welcome, {username}!"

if __name__ == "__main__":
    app.run(debug=True)
