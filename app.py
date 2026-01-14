from flask import Flask, render_template, request, abort
import sqlite3

app = Flask(__name__)
DB_PATH = 'million_live.db'  # ← 使用するDB名

# DB接続関数
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- トップページ: キャラクター一覧 ---
@app.route('/')
def index():
    attr = request.args.get('type')  # 'Pr', 'Fa', 'An' など
    conn = get_db_connection()
    if attr and attr != 'all':
        characters = conn.execute(
            'SELECT * FROM characters WHERE type = ? ORDER BY name', (attr,)
        ).fetchall()
    else:
        characters = conn.execute(
            'SELECT * FROM characters ORDER BY name'
        ).fetchall()
    conn.close()

    # 属性表示名
    type_names = {'all': 'ALL', 'Pr': 'Princess', 'Fa': 'Fairy', 'An': 'Angel'}
    selected_type_name = type_names.get(attr, 'ALL')

    # 曲カテゴリリンク表示用
    song_categories = ['ALL', '全体曲', 'ユニット曲', 'ソロ曲']

    return render_template('index.html',
                           characters=characters,
                           selected_type_name=selected_type_name,
                           song_categories=song_categories)

# --- キャラクター詳細ページ ---
@app.route('/character/<int:character_id>')
def character_detail(character_id):
    conn = get_db_connection()
    character = conn.execute(
        'SELECT * FROM characters WHERE character_id = ?', (character_id,)
    ).fetchone()
    if character is None:
        conn.close()
        abort(404)

    # キャラクターに紐付く曲をすべて取得
    songs = conn.execute(
        '''
        SELECT s.song_id, s.title, s.category
        FROM songs s
        JOIN characters_songs cs ON s.song_id = cs.song_id
        WHERE cs.character_id = ?
        ORDER BY s.title
        ''', (character_id,)
    ).fetchall()
    conn.close()

    # カテゴリごとに分ける（ソロ→ユニット→全体曲）
    solo_songs = [s for s in songs if s['category'] == 'ソロ曲']
    unit_songs = [s for s in songs if s['category'] == 'ユニット曲']
    all_songs  = [s for s in songs if s['category'] == '全体曲']

    return render_template('character_detail.html',
                           character=character,
                           solo_songs=solo_songs,
                           unit_songs=unit_songs,
                           all_songs=all_songs)

# --- 曲詳細ページ ---
@app.route('/song/<int:song_id>')
def song_detail(song_id):
    conn = get_db_connection()
    song = conn.execute(
        'SELECT * FROM songs WHERE song_id = ?', (song_id,)
    ).fetchone()
    if song is None:
        conn.close()
        abort(404)

    characters = conn.execute(
        '''
        SELECT c.character_id, c.name, c.type
        FROM characters c
        JOIN characters_songs cs ON c.character_id = cs.character_id
        WHERE cs.song_id = ?
        ORDER BY c.name
        ''', (song_id,)
    ).fetchall()
    conn.close()

    # 属性表示名変換
    type_names = {'Pr': 'Princess', 'Fa': 'Fairy', 'An': 'Angel'}

    return render_template('song_detail.html',
                           song=song,
                           characters=characters,
                           type_names=type_names)

# --- 曲一覧ページ ---
@app.route('/songs')
def songs_list():
    category = request.args.get('category')  # 'ALL', '全体曲', 'ユニット曲', 'ソロ曲'
    conn = get_db_connection()

    if category in ('全体曲', 'ユニット曲', 'ソロ曲'):
        songs = conn.execute('SELECT * FROM songs WHERE category = ? ORDER BY title', (category,)).fetchall()
    else:
        # ALL: すべての曲
        songs = conn.execute('SELECT * FROM songs ORDER BY title').fetchall()

    conn.close()

    song_categories = ['ALL', '全体曲', 'ユニット曲', 'ソロ曲']
    selected_category_name = category if category else 'ALL'

    return render_template('songs_list.html',
                           songs=songs,
                           song_categories=song_categories,
                           selected_category_name=selected_category_name)

if __name__ == '__main__':
    app.run(debug=True)
