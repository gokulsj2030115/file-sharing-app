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
    prefix = request.args.get('prefix', '')
    view = request.args.get('view', 'all')
    
    # 1. Connectivity & Stats
    is_connected = s3.check_connection()
    stats = s3.get_bucket_stats()
    recent_files = s3.get_recent_files(7)
    
    # 2. Listing logic based on View
    if view == 'recent':
        files = recent_files
        title = "Recent Files"
    elif view == 'shared':
        files = [] # Placeholder for future implementation
        title = "Shared with me"
    elif view == 'starred':
        files = [] # Placeholder for future implementation
        title = "Starred Files"
    elif view == 'trash':
        files = [] # Placeholder for future implementation
        title = "Trash"
    else:
        files = s3.list_files(prefix)
        title = "All Files"
    
    # 3. Breadcrumbs
    breadcrumbs = []
    parts = prefix.strip('/').split('/')
    if parts == ['']: parts = []
    
    path_acc = ""
    for part in parts:
        path_acc += part + "/"
        breadcrumbs.append({'name': part, 'prefix': path_acc})
        
    return render_template('index.html', 
                          files=files, 
                          current_prefix=prefix, 
                          breadcrumbs=breadcrumbs,
                          is_connected=is_connected,
                          stats=stats,
                          recent_files=recent_files,
                          current_view=view,
                          page_title=title)

@app.route('/upload', methods=['POST'])
def upload():
    prefix = request.form.get('prefix', '')
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index', prefix=prefix))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index', prefix=prefix))
    
    if file:
        success = s3.upload_file(file, file.filename, file.content_type, prefix)
        if success:
            flash(f'File {file.filename} uploaded successfully!', 'success')
        else:
            flash(f'Error uploading {file.filename} to S3.', 'error')
    
    return redirect(url_for('index', prefix=prefix))

@app.route('/create-folder', methods=['POST'])
def create_folder():
    prefix = request.form.get('prefix', '')
    folder_name = request.form.get('folder_name', '').strip()
    
    if not folder_name:
        flash('Folder name is required.', 'error')
        return redirect(url_for('index', prefix=prefix))
    
    success = s3.create_folder(folder_name, prefix)
    if success:
        flash(f'Folder "{folder_name}" created successfully!', 'success')
    else:
        flash(f'Error creating folder "{folder_name}".', 'error')
        
    return redirect(url_for('index', prefix=prefix))

@app.route('/delete/<path:filename>', methods=['POST'])
def delete_file(filename):
    prefix = request.args.get('prefix', '')
    success = s3.delete_file(filename)
    if success:
        flash(f'File {filename} deleted successfully!', 'success')
    else:
        flash(f'Error deleting {filename} from S3.', 'error')
    return redirect(url_for('index', prefix=prefix))

@app.route('/delete-folder', methods=['POST'])
def delete_folder():
    current_prefix = request.form.get('current_prefix', '')
    folder_prefix = request.form.get('folder_prefix', '')
    
    if not folder_prefix:
        flash('No folder specified.', 'error')
        return redirect(url_for('index', prefix=current_prefix))
        
    success = s3.delete_recursive(folder_prefix)
    if success:
        flash(f'Folder deleted successfully!', 'success')
    else:
        flash(f'Error deleting folder.', 'error')
    return redirect(url_for('index', prefix=current_prefix))

@app.route('/share/<path:filename>')
def share_link(filename):
    # This route returns a JSON with the URL for AJAX calls (JS handles copying)
    url = s3.get_presigned_url(filename)
    if url:
        return jsonify({'success': True, 'url': url})
    return jsonify({'success': False, 'error': 'Link generation failed'}), 500

@app.route('/view/<path:filename>')
def view_file(filename):
    # Directly redirects to the presigned URL for viewing
    url = s3.get_presigned_url(filename)
    if url:
        return redirect(url)
    flash("Could not open file.", "error")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
