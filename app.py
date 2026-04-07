from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from s3_service import S3Service
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Initialize S3 Service
s3 = S3Service()

@app.route('/')
def index():
    files = s3.list_files()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    
    if file:
        success = s3.upload_file(file, file.filename, file.content_type)
        if success:
            flash(f'File {file.filename} uploaded successfully!', 'success')
        else:
            flash('Error uploading file to S3.', 'error')
    
    return redirect(url_for('index'))

@app.route('/generate-link/<path:filename>')
def generate_link(filename):
    url = s3.get_presigned_url(filename)
    if url:
        return jsonify({'success': True, 'url': url})
    return jsonify({'success': False, 'error': 'Could not generate link'}), 500

if __name__ == '__main__':
    # Local development run
    app.run(debug=True, host='0.0.0.0', port=5000)
