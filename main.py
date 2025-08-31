import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

app = Flask(__name__, static_folder='public', static_url_path='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB file size limit

# Enable CORS for all routes
CORS(app)

# --- Helper Functions ---

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create the 'uploads' directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
# --- API Routes ---

# Route to serve the main index.html page
@app.route('/')
def index():
    # Serves the index.html from the 'public' folder using the more robust send_from_directory
    return send_from_directory(app.static_folder, 'index.html')

# Route to handle the file upload logic
@app.route('/api/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'myFile' not in request.files:
        return jsonify({'msg': 'Error: No file part in the request'}), 400
    
    file = request.files['myFile']

    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return jsonify({'msg': 'Error: No file selected!'}), 400

    # If the file exists and has an allowed extension
    if file and allowed_file(file.filename):
        # Sanitize the filename to prevent security issues
        filename = secure_filename(file.filename)
        
        # Save the file to the configured upload folder
        try:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({
                'msg': 'File uploaded successfully!',
                'file': f'uploads/{filename}'
            }), 200
        except Exception as e:
            return jsonify({'msg': f'Error saving file: {e}'}), 500
            
    else:
        return jsonify({'msg': 'Error: File type not allowed!'}), 400

# --- Start Server ---
if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible on your network
    app.run(debug=True, port=5000, host='0.0.0.0')