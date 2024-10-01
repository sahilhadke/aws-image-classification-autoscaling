from flask import Flask, request, jsonify
import csv

app = Flask(__name__)

# Load the classification lookup table
classifications = {}
with open('resources/classification.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        classifications[row[0]] = row[1]

@app.route('/health', methods=['GET'])
def hello():
    return "Hello, World!"

@app.route('/', methods=['POST'])
def process_image():
    
    if 'inputFile' not in request.files:
        return "No file part", 400
    
    file = request.files['inputFile']

    if file.filename == '':
        return "No selected file", 400
    
    if file:
        filename = file.filename
        # remove file extension
        filename = filename.split('.')[0]
        # In a real scenario, you'd save the file and process it
        # Here, we're just looking up the result
        result = classifications.get(filename, "Unknown")
        return f"{filename}:{result}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)