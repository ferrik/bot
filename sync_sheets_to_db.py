import os
import gspread
import psycopg2
from psycopg2.extras import execute_values
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Отримуємо credentials з Render Environment Variables
creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
with open("creds.json", "w") as f:
    f.write(creds_json)

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# ⚙️ Назва таблиці Google Sheets
sheet = client.open("Назва_твоєї_таблиці").sheet1  # або client.open_by_key("ID_таблиці")
data = sheet.get_all_records()

# --- PostgreSQL setup ---
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# --- Очистити таблицю перед оновленням (приклад для таблиці "users") ---
cur.execute("DELETE FROM users;")

# --- Вставити оновлені дані ---
rows = [(d["user_id"], d["name"], d["phone"], d["address"], d["order"], d["date"]) for d in data]
execute_values(cur, """
    INSERT INTO users (user_id, name, phone, address, order_text, created_at)
    VALUES %s
""", rows)

conn.commit()
cur.close()
conn.close()

print("✅ Дані синхронізовано з Google Sheets → PostgreSQL")
