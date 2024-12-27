from flask import Flask, request, jsonify
import os
import json
from datetime import datetime
from flask_cors import CORS
import uuid  # Для генерации уникальных ID

app = Flask(__name__)
CORS(app)  # Разрешить кросс-доменные запросы

LEADERBOARD_FILE = "leaderboard.json"

# Инициализируем файл лидеров, если его нет
if not os.path.exists(LEADERBOARD_FILE):
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

@app.route("/submit_score", methods=["POST"])
def submit_score():
    """
    Эндпоинт для приёма результатов игры в формате JSON.
    Если в таблице уже есть запись с таким player_name,
    обновляем её только если новый gifts_collected больше текущего.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    player_name = data.get("player_name")
    gifts_collected = data.get("gifts_collected")
    end_time = data.get("end_time")

    if not all([player_name, isinstance(gifts_collected, int), end_time]):
        return jsonify({"error": "Invalid data format"}), 400

    # Загружаем текущую таблицу лидеров
    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
        leaderboard = json.load(f)

    # Проверяем, есть ли уже запись с таким player_name
    existing_entry = None
    for entry in leaderboard:
        if entry["player_name"] == player_name:
            existing_entry = entry
            break

    if existing_entry:
        # Обновляем запись только если новый результат лучше текущего
        if gifts_collected > existing_entry["gifts_collected"]:
            existing_entry["gifts_collected"] = gifts_collected
            existing_entry["end_time"] = end_time
        else:
            return jsonify({
                "message": "New score is not higher than the current record.",
                "leaderboard": leaderboard
            }), 200
    else:
        # Создаём новую запись
        new_entry = {
            "id": str(uuid.uuid4()),
            "player_name": player_name,
            "gifts_collected": gifts_collected,
            "end_time": end_time
        }
        leaderboard.append(new_entry)

    # Сохраняем обновлённую таблицу лидеров
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=4)

    return jsonify({
        "message": "Score submitted successfully!",
        "leaderboard": leaderboard
    }), 200



@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    """
    Эндпоинт для получения всей таблицы лидеров с ID.
    Сортировка по количеству собранных подарков (gifts_collected).
    """
    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Сортировка по количеству собранных подарков (gifts_collected) в убывающем порядке
    sorted_data = sorted(data, key=lambda x: x['gifts_collected'], reverse=True)
    
    return jsonify({"leaderboard": sorted_data}), 200



@app.route("/delete_score/<score_id>", methods=["DELETE"])
def delete_score(score_id):
    """
    Эндпоинт для удаления записи по ID.
    """
    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
        leaderboard = json.load(f)

    # Проверяем, есть ли запись с данным ID
    new_leaderboard = [entry for entry in leaderboard if entry["id"] != score_id]

    if len(new_leaderboard) == len(leaderboard):
        return jsonify({"error": f"No entry found with ID: {score_id}"}), 404

    # Сохраняем обновлённый список
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(new_leaderboard, f, ensure_ascii=False, indent=4)

    return jsonify({"message": f"Entry with ID {score_id} has been deleted."}), 200


@app.route("/get_entry/<score_id>", methods=["GET"])
def get_entry(score_id):
    """
    Эндпоинт для получения записи по ID.
    """
    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
        leaderboard = json.load(f)

    entry = next((item for item in leaderboard if item["id"] == score_id), None)

    if entry is None:
        return jsonify({"error": f"No entry found with ID: {score_id}"}), 404

    return jsonify({"entry": entry}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
