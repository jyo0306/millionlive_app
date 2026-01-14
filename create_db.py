import sqlite3
import csv
import os

DB_PATH = 'million_live.db'  # 新しいDB名
csv_folder = 'data'  # CSVファイルが同じフォルダにある場合


conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# --- テーブル作成 ---
cur.execute('''
CREATE TABLE IF NOT EXISTS songs (
    song_id INTEGER PRIMARY KEY,
    title TEXT,
    category TEXT
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS characters (
    character_id INTEGER PRIMARY KEY,
    name TEXT,
    type TEXT
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS characters_songs (
    song_id INTEGER,
    character_id INTEGER,
    PRIMARY KEY (song_id, character_id),
    FOREIGN KEY (song_id) REFERENCES songs(song_id),
    FOREIGN KEY (character_id) REFERENCES characters(character_id)
)
''')

# --- CSVからデータを読み込む ---
def load_csv(table_name, filename, columns):
    path = os.path.join(csv_folder, filename)
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            values = tuple(row[col] for col in columns)
            placeholders = ','.join('?' for _ in columns)
            cur.execute(f'INSERT INTO {table_name} ({",".join(columns)}) VALUES ({placeholders})', values)

# songs.csv
load_csv('songs', 'songs.csv', ['song_id', 'title', 'category'])

# characters.csv
load_csv('characters', 'characters.csv', ['character_id', 'name', 'type'])

# characters_songs.csv
load_csv('characters_songs', 'characters_songs.csv', ['song_id', 'character_id'])

conn.commit()
conn.close()

print("million_live.db の作成とデータ挿入が完了しました。")
