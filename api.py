from flask import Flask, request, jsonify, send_file
import subprocess
import os
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'API is running', 'service': 'video-expander'})

@app.route('/expand-video', methods=['POST'])
def expand_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video = request.files['video']
        if video.filename == '':
            return jsonify({'error': 'No video selected'}), 400
        
        target_ratio = request.form.get('target_ratio', '9:16')
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_input:
            video.save(tmp_input.name)
            input_path = tmp_input.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output:
            output_path = tmp_output.name
        
        # Run the AI video expansion (adjust based on the actual tool's usage)
        result = subprocess.run([
            'python', 'main.py',  # Adjust to actual main script
            '--input', input_path,
            '--output', output_path,
            '--aspect-ratio', target_ratio,
            '--expand-background'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Video processing failed',
                'details': result.stderr
            }), 500
        
        # Return the processed video
        return send_file(
            output_path, 
            as_attachment=True, 
            download_name=f'expanded_{video.filename}',
            mimetype='video/mp4'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Cleanup temporary files
        try:
            os.unlink(input_path)
            os.unlink(output_path)
        except:
            pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
