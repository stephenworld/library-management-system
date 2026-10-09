from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/books', methods=['GET'])
def view_all_books():
    with open('database/books.json', 'r') as file:
        library_data = json.load(file)
    
    return jsonify(library_data)

@app.route('/users', methods=['GET'])
def view_all_users():
    with open('database/users.json', 'r') as file:
        users_data = json.load(file)
    
    return jsonify(users_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)