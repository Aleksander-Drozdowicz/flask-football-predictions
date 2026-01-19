"""
Aplikacja do typowania meczów i statystyk drużyn
MVP - Flask + SQLite + Jinja2
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Zmień w produkcji!

DATABASE = 'football_predictions.db'


def get_db():
    """Pobiera połączenie z bazą danych"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicjalizuje bazę danych i tworzy tabele"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabela users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'USER',
            created_at TEXT NOT NULL
        )
    ''')
    
    # Tabela matches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            match_date TEXT NOT NULL,
            home_score INTEGER NULL,
            away_score INTEGER NULL,
            created_at TEXT NOT NULL,
            api_match_id INTEGER NULL UNIQUE
        )
    ''')
    
    # Dodaj kolumnę api_match_id jeśli tabela już istnieje (migracja)
    try:
        cursor.execute('ALTER TABLE matches ADD COLUMN api_match_id INTEGER NULL UNIQUE')
    except sqlite3.OperationalError:
        pass  # Kolumna już istnieje
    
    # Tabela predictions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            match_id INTEGER NOT NULL,
            predicted_home INTEGER NOT NULL,
            predicted_away INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (match_id) REFERENCES matches(id),
            UNIQUE(user_id, match_id)
        )
    ''')
    
    conn.commit()
    conn.close()


def seed_db():
    """Dodaje przykładowe dane do bazy"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Sprawdź czy admin już istnieje
    cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        # Utwórz konto admina
        admin_password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, created_at)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_password_hash, 'ADMIN', datetime.now().isoformat()))
    
    # Sprawdź czy mecze już istnieją
    cursor.execute('SELECT COUNT(*) FROM matches')
    match_count = cursor.fetchone()[0]
    
    if match_count == 0:
        # Dodaj przykładowe mecze (daty w przyszłości i przeszłości dla demonstracji)
        from datetime import timedelta
        now = datetime.now()
        
        # Mecze w przyszłości (do typowania)
        future_date1 = (now + timedelta(days=7)).strftime('%Y-%m-%dT20:00:00')
        future_date2 = (now + timedelta(days=8)).strftime('%Y-%m-%dT15:00:00')
        future_date3 = (now + timedelta(days=9)).strftime('%Y-%m-%dT18:00:00')
        future_date4 = (now + timedelta(days=10)).strftime('%Y-%m-%dT17:00:00')
        future_date5 = (now + timedelta(days=11)).strftime('%Y-%m-%dT20:00:00')
        future_date6 = (now + timedelta(days=12)).strftime('%Y-%m-%dT19:00:00')
        future_date7 = (now + timedelta(days=13)).strftime('%Y-%m-%dT20:30:00')
        
        # Mecze w przeszłości (zakończone, z wynikami)
        past_date1 = (now - timedelta(days=5)).strftime('%Y-%m-%dT19:00:00')
        past_date2 = (now - timedelta(days=4)).strftime('%Y-%m-%dT20:30:00')
        past_date3 = (now - timedelta(days=3)).strftime('%Y-%m-%dT16:00:00')
        past_date4 = (now - timedelta(days=2)).strftime('%Y-%m-%dT18:00:00')
        past_date5 = (now - timedelta(days=1)).strftime('%Y-%m-%dT15:30:00')
        
        sample_matches = [
            ('FC Barcelona', 'Real Madrid', future_date1, None, None),
            ('Manchester United', 'Liverpool', future_date2, None, None),
            ('Bayern Munich', 'Borussia Dortmund', future_date3, None, None),
            ('PSG', 'Marseille', past_date1, 2, 1),
            ('Juventus', 'AC Milan', past_date2, 1, 1),
            ('Chelsea', 'Arsenal', past_date3, 3, 0),
            ('Atletico Madrid', 'Sevilla', future_date4, None, None),
            ('Inter Milan', 'Napoli', past_date4, 2, 2),
            ('Manchester City', 'Tottenham', past_date5, 1, 0),
            ('Roma', 'Lazio', future_date5, None, None),
            ('Ajax', 'PSV Eindhoven', past_date3, 0, 2),
            ('Benfica', 'Porto', future_date6, None, None),
            ('AC Milan', 'Inter Milan', future_date7, None, None),
        ]
        
        current_time = datetime.now().isoformat()
        for home, away, match_date, home_score, away_score in sample_matches:
            cursor.execute('''
                INSERT INTO matches (home_team, away_team, match_date, home_score, away_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (home, away, match_date, home_score, away_score, current_time))
    
    conn.commit()
    conn.close()


def login_required(f):
    """Dekorator wymagający zalogowania"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Musisz się zalogować, aby uzyskać dostęp do tej strony.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Dekorator wymagający roli ADMIN"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Musisz się zalogować.', 'warning')
            return redirect(url_for('login'))
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        if not user or user['role'] != 'ADMIN':
            flash('Brak uprawnień administratora.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# Routes

@app.route('/')
def index():
    """Strona główna"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Rejestracja użytkownika"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Wszystkie pola są wymagane.', 'danger')
            return render_template('register.html')
        
        if len(password) < 3:
            flash('Hasło musi mieć co najmniej 3 znaki.', 'danger')
            return render_template('register.html')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Sprawdź czy użytkownik już istnieje
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            flash('Użytkownik o tej nazwie już istnieje.', 'danger')
            return render_template('register.html')
        
        # Utwórz nowego użytkownika
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, created_at)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, 'USER', datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        flash('Rejestracja zakończona pomyślnie! Możesz się teraz zalogować.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logowanie użytkownika"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Wprowadź nazwę użytkownika i hasło.', 'danger')
            return render_template('login.html')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash, role FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Witaj, {username}!', 'success')
            return redirect(url_for('matches'))
        else:
            flash('Nieprawidłowa nazwa użytkownika lub hasło.', 'danger')
            return render_template('login.html')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Wylogowanie użytkownika"""
    session.clear()
    flash('Zostałeś wylogowany.', 'info')
    return redirect(url_for('index'))


@app.route('/matches')
@login_required
def matches():
    """Lista meczów z możliwością dodania/edycji typów"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Pobierz wszystkie mecze - najpierw bez wyników (nowe), potem zakończone
    cursor.execute('''
        SELECT m.*, 
               p.id as prediction_id, 
               p.predicted_home, 
               p.predicted_away
        FROM matches m
        LEFT JOIN predictions p ON m.id = p.match_id AND p.user_id = ?
        ORDER BY 
            CASE WHEN m.home_score IS NULL AND m.away_score IS NULL THEN 0 ELSE 1 END,
            m.match_date ASC
    ''', (session['user_id'],))
    
    matches = cursor.fetchall()
    
    # Pobierz typy użytkownika dla wszystkich meczów
    cursor.execute('''
        SELECT match_id, predicted_home, predicted_away
        FROM predictions
        WHERE user_id = ?
    ''', (session['user_id'],))
    
    user_predictions = {row['match_id']: (row['predicted_home'], row['predicted_away']) 
                        for row in cursor.fetchall()}
    
    conn.close()
    
    return render_template('matches.html', matches=matches, user_predictions=user_predictions)


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    """Dodaj lub zaktualizuj typ użytkownika"""
    match_id = request.form.get('match_id')
    predicted_home = request.form.get('predicted_home', '').strip()
    predicted_away = request.form.get('predicted_away', '').strip()
    
    if not match_id or not predicted_home or not predicted_away:
        flash('Wszystkie pola są wymagane.', 'danger')
        return redirect(url_for('matches'))
    
    try:
        predicted_home = int(predicted_home)
        predicted_away = int(predicted_away)
        match_id = int(match_id)
        
        if predicted_home < 0 or predicted_away < 0:
            raise ValueError('Wynik nie może być ujemny')
    except ValueError:
        flash('Wprowadź poprawne wartości liczbowe (>= 0).', 'danger')
        return redirect(url_for('matches'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Sprawdź czy mecz istnieje i czy nie ma jeszcze wyniku
    cursor.execute('SELECT home_score, away_score FROM matches WHERE id = ?', (match_id,))
    match = cursor.fetchone()
    
    if not match:
        conn.close()
        flash('Mecz nie istnieje.', 'danger')
        return redirect(url_for('matches'))
    
    if match['home_score'] is not None or match['away_score'] is not None:
        conn.close()
        flash('Nie można zmienić typu dla meczu, który już się zakończył.', 'danger')
        return redirect(url_for('matches'))
    
    # Sprawdź czy typ już istnieje
    cursor.execute('SELECT id FROM predictions WHERE user_id = ? AND match_id = ?', 
                   (session['user_id'], match_id))
    existing = cursor.fetchone()
    
    current_time = datetime.now().isoformat()
    
    if existing:
        # Aktualizuj istniejący typ
        cursor.execute('''
            UPDATE predictions 
            SET predicted_home = ?, predicted_away = ?, updated_at = ?
            WHERE id = ?
        ''', (predicted_home, predicted_away, current_time, existing['id']))
        flash('Typ został zaktualizowany!', 'success')
    else:
        # Dodaj nowy typ
        cursor.execute('''
            INSERT INTO predictions (user_id, match_id, predicted_home, predicted_away, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], match_id, predicted_home, predicted_away, current_time))
        flash('Typ został dodany!', 'success')
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('matches'))


@app.route('/my_predictions')
@login_required
def my_predictions():
    """Lista typów użytkownika"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, 
               m.home_team, 
               m.away_team, 
               m.match_date,
               m.home_score,
               m.away_score
        FROM predictions p
        JOIN matches m ON p.match_id = m.id
        WHERE p.user_id = ?
        ORDER BY m.match_date ASC
    ''', (session['user_id'],))
    
    predictions = cursor.fetchall()
    
    # Oblicz status dla każdego typu
    predictions_with_status = []
    for pred in predictions:
        status = 'oczekiwanie'
        if pred['home_score'] is not None and pred['away_score'] is not None:
            if (pred['predicted_home'] == pred['home_score'] and 
                pred['predicted_away'] == pred['away_score']):
                status = 'trafiony'
            else:
                status = 'nietrafiony'
        
        pred_dict = dict(pred)
        pred_dict['status'] = status
        predictions_with_status.append(pred_dict)
    
    conn.close()
    
    return render_template('my_predictions.html', predictions=predictions_with_status)


@app.route('/delete_prediction/<int:prediction_id>', methods=['POST'])
@login_required
def delete_prediction(prediction_id):
    """Usuń typ użytkownika"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Sprawdź czy typ należy do użytkownika i czy mecz się jeszcze nie zakończył
    cursor.execute('''
        SELECT p.id, m.home_score, m.away_score
        FROM predictions p
        JOIN matches m ON p.match_id = m.id
        WHERE p.id = ? AND p.user_id = ?
    ''', (prediction_id, session['user_id']))
    
    pred = cursor.fetchone()
    
    if not pred:
        conn.close()
        flash('Typ nie istnieje lub nie masz uprawnień do jego usunięcia.', 'danger')
        return redirect(url_for('my_predictions'))
    
    if pred['home_score'] is not None or pred['away_score'] is not None:
        conn.close()
        flash('Nie można usunąć typu dla meczu, który już się zakończył.', 'danger')
        return redirect(url_for('my_predictions'))
    
    cursor.execute('DELETE FROM predictions WHERE id = ?', (prediction_id,))
    conn.commit()
    conn.close()
    
    flash('Typ został usunięty.', 'success')
    return redirect(url_for('my_predictions'))


@app.route('/stats')
@login_required
def stats():
    """Statystyki użytkownika"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Pobierz tylko zakończone mecze z typami użytkownika
    cursor.execute('''
        SELECT p.predicted_home, 
               p.predicted_away,
               m.home_score,
               m.away_score,
               m.home_team,
               m.away_team,
               m.match_date
        FROM predictions p
        JOIN matches m ON p.match_id = m.id
        WHERE p.user_id = ? 
          AND m.home_score IS NOT NULL 
          AND m.away_score IS NOT NULL
        ORDER BY m.match_date ASC
    ''', (session['user_id'],))
    
    finished_predictions = cursor.fetchall()
    
    # Oblicz statystyki
    total = len(finished_predictions)
    correct = 0
    
    for pred in finished_predictions:
        if (pred['predicted_home'] == pred['home_score'] and 
            pred['predicted_away'] == pred['away_score']):
            correct += 1
    
    success_rate = (correct / total * 100) if total > 0 else 0
    
    conn.close()
    
    return render_template('stats.html', 
                         total=total, 
                         correct=correct, 
                         success_rate=round(success_rate, 2),
                         predictions=finished_predictions)


@app.route('/admin')
@admin_required
def admin():
    """Panel administratora"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Pobierz wszystkie mecze
    cursor.execute('SELECT * FROM matches ORDER BY match_date ASC')
    matches = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin.html', matches=matches)


@app.route('/admin/add_match', methods=['POST'])
@admin_required
def add_match():
    """Dodaj nowy mecz"""
    home_team = request.form.get('home_team', '').strip()
    away_team = request.form.get('away_team', '').strip()
    match_date = request.form.get('match_date', '').strip()
    
    if not home_team or not away_team or not match_date:
        flash('Wszystkie pola są wymagane.', 'danger')
        return redirect(url_for('admin'))
    
    # Konwersja datetime-local do formatu ISO
    try:
        # datetime-local zwraca format: YYYY-MM-DDTHH:MM
        # Konwertujemy do ISO: YYYY-MM-DDTHH:MM:SS
        if 'T' in match_date:
            parts = match_date.split('T')
            if len(parts) == 2 and parts[1].count(':') == 1:
                match_date = match_date + ':00'  # Dodaj sekundy jeśli brakuje
        datetime.fromisoformat(match_date)
    except ValueError:
        flash('Nieprawidłowy format daty.', 'danger')
        return redirect(url_for('admin'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO matches (home_team, away_team, match_date, home_score, away_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (home_team, away_team, match_date, None, None, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    flash('Mecz został dodany!', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/set_result/<int:match_id>', methods=['POST'])
@admin_required
def set_result(match_id):
    """Ustaw wynik meczu"""
    home_score = request.form.get('home_score', '').strip()
    away_score = request.form.get('away_score', '').strip()
    
    if home_score == '' or away_score == '':
        flash('Wszystkie pola są wymagane.', 'danger')
        return redirect(url_for('admin'))
    
    try:
        home_score = int(home_score)
        away_score = int(away_score)
        
        if home_score < 0 or away_score < 0:
            raise ValueError('Wynik nie może być ujemny')
    except ValueError:
        flash('Wprowadź poprawne wartości liczbowe (>= 0).', 'danger')
        return redirect(url_for('admin'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Sprawdź czy mecz istnieje
    cursor.execute('SELECT id FROM matches WHERE id = ?', (match_id,))
    if not cursor.fetchone():
        conn.close()
        flash('Mecz nie istnieje.', 'danger')
        return redirect(url_for('admin'))
    
    cursor.execute('''
        UPDATE matches 
        SET home_score = ?, away_score = ?
        WHERE id = ?
    ''', (home_score, away_score, match_id))
    
    conn.commit()
    conn.close()
    
    flash('Wynik meczu został zaktualizowany!', 'success')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    # Inicjalizuj bazę danych przy starcie
    init_db()
    seed_db()
    
    print("=" * 50)
    print("Aplikacja uruchomiona!")
    print("=" * 50)
    print("\nKonto administratora:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nDostępne strony:")
    print("  http://127.0.0.1:5000/")
    print("=" * 50)
    
    app.run(debug=True)

