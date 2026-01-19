"""
Skrypt do czyszczenia bazy danych - usuwa wszystkie dane, zachowuje strukturę tabel
"""

import sqlite3
import os

DATABASE = 'football_predictions.db'


def clear_database():
    """Czyści wszystkie dane z bazy, zachowując strukturę tabel"""
    
    if not os.path.exists(DATABASE):
        print(f"Baza danych {DATABASE} nie istnieje.")
        return
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Sprawdź ile rekordów jest w każdej tabeli
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches")
        matches_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM predictions")
        predictions_count = cursor.fetchone()[0]
        
        print(f"Przed czyszczeniem:")
        print(f"  Users: {users_count}")
        print(f"  Matches: {matches_count}")
        print(f"  Predictions: {predictions_count}")
        
        # Usuń wszystkie dane z tabel (w odpowiedniej kolejności ze względu na foreign keys)
        print("\nCzyszczenie bazy danych...")
        
        cursor.execute("DELETE FROM predictions")
        print(f"  ✓ Usunięto {cursor.rowcount} typów")
        
        cursor.execute("DELETE FROM matches")
        print(f"  ✓ Usunięto {cursor.rowcount} meczów")
        
        cursor.execute("DELETE FROM users")
        print(f"  ✓ Usunięto {cursor.rowcount} użytkowników")
        
        # Resetuj AUTOINCREMENT
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'matches', 'predictions')")
        
        conn.commit()
        
        # Sprawdź czy tabele są puste
        cursor.execute("SELECT COUNT(*) FROM users")
        users_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches")
        matches_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM predictions")
        predictions_after = cursor.fetchone()[0]
        
        print(f"\nPo czyszczeniu:")
        print(f"  Users: {users_after}")
        print(f"  Matches: {matches_after}")
        print(f"  Predictions: {predictions_after}")
        
        print("\n✓ Baza danych została wyczyszczona!")
        print("  Struktura tabel została zachowana.")
        
    except sqlite3.Error as e:
        print(f"Błąd podczas czyszczenia bazy: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Czyszczenie bazy danych")
    print("=" * 50)
    
    response = input("\nCzy na pewno chcesz usunąć wszystkie dane? (tak/nie): ")
    
    if response.lower() in ['tak', 'yes', 'y', 't']:
        clear_database()
        print("\nMożesz teraz uruchomić aplikację, aby utworzyć nowe dane seed.")
    else:
        print("Anulowano.")





