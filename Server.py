from flask import Flask, request, jsonify, send_from_directory, send_file
import os
import zipfile
from io import BytesIO

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # создаём папку для загрузок, если её нет

@app.route("/upload", methods=["POST"])
def upload_file():
    """Эндпоинт для загрузки файла"""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)  # сохраняем файл в папку "uploads"

    return jsonify({"message": f"File {file.filename} uploaded successfully!"}), 200

@app.route("/list_files", methods=["GET"])
def list_files():
    """Эндпоинт для получения списка загруженных файлов"""
    files = os.listdir(UPLOAD_FOLDER)  # Получаем список файлов в папке
    return jsonify({"files": files}), 200

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """Эндпоинт для скачивания конкретного файла"""
    if filename not in os.listdir(UPLOAD_FOLDER):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/download_all", methods=["GET"])
def download_all_files():
    """Эндпоинт для скачивания всех файлов в виде архива"""
    files = os.listdir(UPLOAD_FOLDER)
    if not files:
        return jsonify({"error": "No files to download"}), 404

    # Создаём ZIP-архив в памяти
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, "w") as zipf:
        for file in files:
            file_path = os.path.join(UPLOAD_FOLDER, file)
            zipf.write(file_path, file)
    memory_file.seek(0)

    return send_file(memory_file, mimetype="application/zip", as_attachment=True, download_name="all_files.zip")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
