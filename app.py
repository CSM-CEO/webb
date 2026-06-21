import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_NAME = 'habits.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                streak INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        ''')
        conn.commit()

# Главная страница (Вывод + Поиск + Фильтр)
@app.route('/')
def index():
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    
    query = "SELECT * FROM habits WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    if status_filter != 'all':
        query += " AND status = ?"
        params.append(status_filter)
        
    with get_db_connection() as conn:
        habits = conn.execute(query, params).fetchall()
        
    return render_template('index.html', habits=habits, search=search_query, current_status=status_filter)

# Добавление новой привычки
@app.route('/habit/add', methods=['POST'])
def add_habit():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        return redirect(url_for('index'))
        
    with get_db_connection() as conn:
        conn.execute('INSERT INTO habits (title, description) VALUES (?, ?)', (title, description))
        conn.commit()
    return redirect(url_for('index'))

# Отметка выполнения (Увеличение счетчика дней подряд)
@app.route('/habit/check/<int:habit_id>', methods=['POST'])
def check_habit():
    with get_db_connection() as conn:
        conn.execute('UPDATE habits SET streak = streak + 1, status = "completed" WHERE id = ?', (habit_id,))
        conn.commit()
    return redirect(url_for('index'))

# Страница редактирования
@app.route('/habit/edit/<int:habit_id>')
def edit_page(habit_id):
    with get_db_connection() as conn:
        habit = conn.execute('SELECT * FROM habits WHERE id = ?', (habit_id,)).fetchone()
    if not habit:
        return "Привычка не найдена", 404
    return render_template('edit.html', habit=habit)

# Сохранение изменений
@app.route('/habit/edit/<int:habit_id>', methods=['POST'])
def update_habit(habit_id):
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    status = request.form.get('status', 'active')
    
    if not title:
        return "Название обязательно", 400
        
    with get_db_connection() as conn:
        conn.execute('UPDATE habits SET title = ?, description = ?, status = ? WHERE id = ?', 
                     (title, description, status, habit_id))
        conn.commit()
    return redirect(url_for('index'))

# Удаление привычки
@app.route('/habit/delete/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
        conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
