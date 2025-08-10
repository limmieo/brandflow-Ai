import os
import uuid
import threading
import time
import subprocess
import random
import shutil
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, jsonify,
    send_from_directory
)

app = Flask(__name__)
app.secret_key = os.urandom(16)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Get absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(SCRIPT_DIR, "assets")
PROCESSED_DIR = os.path.join(SCRIPT_DIR, "processed")

# Ensure directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)

BRANDS = {
    "fitness_plus": {
        "metadata": "brand=fitness_plus",
        "lut": "Cobi_3.CUBE",
        "watermarks": [
            "Thick_asian_watermark.png",
            "Thick_asian_watermark_2.png",
            "Thick_asian_watermark_3.png"
        ]
    },
    "athletic_elite": {
        "metadata": "brand=athletic_elite",
        "lut": "Cobi_3.CUBE",
        "watermarks": [
            "gym_baddie_watermark.png",
            "gym_baddie_watermark_2.png",
            "gym_baddie_watermark_3.png"
        ]
    },
    "premium_fitness": {
        "metadata": "brand=premium_fitness",
        "lut": None,
        "watermarks": [
            "polished_watermark.png",
            "polished_watermark_2.png",
            "polished_watermark_3.png"
        ]
    },
    "travel_premium": {
        "metadata": "brand=travel_premium",
        "lut": None,
        "watermarks": [
            "asian_travel_watermark.png",
            "asian_travel_watermark_2.png",
            "asian_travel_watermark_3.png"
        ]
    }
}

_progress = {}   # task_id -> dict with progress and status
_results   = {}  # task_id -> filename

def cleanup_old_videos():
    """Keep only the 3 most recent processed videos"""
    try:
        # Get all .mp4 files in processed directory
        video_files = []
        for file in os.listdir(PROCESSED_DIR):
            if file.endswith('.mp4'):
                file_path = os.path.join(PROCESSED_DIR, file)
                # Get file creation time
                creation_time = os.path.getctime(file_path)
                video_files.append((file_path, creation_time))
        
        # Sort by creation time (oldest first)
        video_files.sort(key=lambda x: x[1])
        
        # If more than 3 files, delete the oldest ones
        if len(video_files) > 3:
            files_to_delete = video_files[:-3]  # Keep last 3, delete the rest
            for file_path, _ in files_to_delete:
                try:
                    os.remove(file_path)
                    print(f"Cleaned up old video: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    except Exception as e:
        print(f"Error in cleanup: {e}")

def _real_video_process(task_id, url, brand):
    """Process video from URL with watermark and LUT"""
    try:
        _progress[task_id] = {"progress": 0, "status": "Starting download..."}
        
        # Download video
        _progress[task_id] = {"progress": 10, "status": "Downloading video..."}
        temp_video = os.path.join(PROCESSED_DIR, f"temp_{task_id}.mp4")
        
        # Use PowerShell to download
        download_cmd = [
            "powershell", "-Command", 
            f"Invoke-WebRequest -Uri '{url}' -OutFile '{temp_video}'"
        ]
        subprocess.run(download_cmd, check=True, capture_output=True)
        
        _progress[task_id] = {"progress": 30, "status": "Processing video..."}
        
        # Get brand config
        brand_config = BRANDS[brand]
        watermark = random.choice(brand_config["watermarks"])
        watermark_path = os.path.join(ASSETS, watermark)
        
        # Output filename
        output_filename = f"{task_id}_watermarked.mp4"
        output_path = os.path.join(PROCESSED_DIR, output_filename)
        
        # FFmpeg command for watermarking
        ffmpeg_cmd = [
            "ffmpeg", "-i", temp_video,
            "-i", watermark_path,
            "-filter_complex", "overlay=W-w-10:H-h-10",
            "-c:a", "copy",
            "-y", output_path
        ]
        
        _progress[task_id] = {"progress": 50, "status": "Adding watermark..."}
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        
        # Clean up temp file
        os.remove(temp_video)
        
        _progress[task_id] = {"progress": 80, "status": "Finalizing..."}
        
        # Clean up old videos (keep only 3)
        cleanup_old_videos()
        
        _progress[task_id] = {"progress": 100, "status": "Complete!"}
        _results[task_id] = output_filename
        
    except Exception as e:
        _progress[task_id] = {"progress": 0, "status": f"Error: {str(e)}"}
        print(f"Error processing video: {e}")

def _real_video_process_upload(task_id, uploaded_file, brand):
    """Process uploaded video file with watermark and LUT"""
    try:
        _progress[task_id] = {"progress": 0, "status": "Processing uploaded video..."}
        
        # Save uploaded file
        temp_video = os.path.join(PROCESSED_DIR, f"temp_upload_{task_id}.mp4")
        uploaded_file.save(temp_video)
        
        _progress[task_id] = {"progress": 30, "status": "Processing video..."}
        
        # Get brand config
        brand_config = BRANDS[brand]
        watermark = random.choice(brand_config["watermarks"])
        watermark_path = os.path.join(ASSETS, watermark)
        
        # Output filename
        output_filename = f"{task_id}_watermarked.mp4"
        output_path = os.path.join(PROCESSED_DIR, output_filename)
        
        # FFmpeg command for watermarking
        ffmpeg_cmd = [
            "ffmpeg", "-i", temp_video,
            "-i", watermark_path,
            "-filter_complex", "overlay=W-w-10:H-h-10",
            "-c:a", "copy",
            "-y", output_path
        ]
        
        _progress[task_id] = {"progress": 60, "status": "Adding watermark..."}
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        
        # Clean up temp file
        os.remove(temp_video)
        
        _progress[task_id] = {"progress": 80, "status": "Finalizing..."}
        
        # Clean up old videos (keep only 3)
        cleanup_old_videos()
        
        _progress[task_id] = {"progress": 100, "status": "Complete!"}
        _results[task_id] = output_filename
        
    except Exception as e:
        _progress[task_id] = {"progress": 0, "status": f"Error: {str(e)}"}
        print(f"Error processing uploaded video: {e}")

@app.route("/")
def index():
    return render_template("index.html", brands=BRANDS)

@app.route("/process", methods=["POST"])
def process_video():
    video_file = request.files.get("video_file")
    video_url = request.form.get("url", "").strip()
    brand = request.form.get("brand", "")
    
    if not video_file and not video_url:
        flash("Please upload a video file or enter a video URL.", "danger")
        return redirect(url_for("index"))
    
    if brand not in BRANDS:
        flash("Please select a valid brand.", "danger")
        return redirect(url_for("index"))

    task_id = str(uuid.uuid4())
    _progress[task_id] = {"progress": 0, "status": "Starting..."}

    # Prioritize file upload over URL
    if video_file:
        thread = threading.Thread(
            target=_real_video_process_upload,
            args=(task_id, video_file, brand),
            daemon=True
        )
    else:
        thread = threading.Thread(
            target=_real_video_process,
            args=(task_id, video_url, brand),
            daemon=True
        )
    
    thread.start()
    return render_template("processing.html", task_id=task_id)

@app.route("/progress/<task_id>")
def progress(task_id):
    progress_data = _progress.get(task_id, {"progress": 0, "status": "Not found"})
    file = _results.get(task_id)
    return jsonify(progress=progress_data["progress"], status=progress_data["status"], filename=file)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(PROCESSED_DIR, filename, as_attachment=True)

@app.errorhandler(413)
def too_large(e):
    return "File too large. Maximum size is 100MB.", 413

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
