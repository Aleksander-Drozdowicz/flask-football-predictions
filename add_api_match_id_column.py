"""
Skrypt do dodania kolumny api_match_id do tabeli matches
"""

import sqlite3
import os

DATABASE = 'football_predictions.db'


def add_api_match_id_column():
    """Dodaje kolumnę api_match_id do tabeli matches jeśli nie istnieje"""
    
    if not os.path.exists(DATABASE):
        print(f"Baza danych {DATABASE} nie istnieje.")
        print("Kolumna zostanie utworzona automatycznie przy pierwszym uruchomieniu aplikacji.")
        return
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Sprawdź czy kolumna już istnieje
        cursor.execute("PRAGMA table_info(matches)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'api_match_id' in columns:
            print("✓ Kolumna api_match_id już istnieje w tabeli matches.")
            conn.close()
            return
        
        print("Dodawanie kolumny api_match_id do tabeli matches...")
        
        # SQLite nie pozwala dodać UNIQUE constraint od razu, więc najpierw dodajemy kolumnę
        cursor.execute('''
            ALTER TABLE matches 
            ADD COLUMN api_match_id INTEGER NULL
        ''')
        
        conn.commit()
        print("✓ Kolumna api_match_id została dodana.")
        
        # Sprawdź czy są duplikaty przed dodaniem UNIQUE
        cursor.execute('SELECT api_match_id, COUNT(*) FROM matches WHERE api_match_id IS NOT NULL GROUP BY api_match_id HAVING COUNT(*) > 1')
        duplicates = cursor.fetchall()
        
        if duplicates:
            print("⚠️  Uwaga: Znaleziono duplikaty api_match_id. Usuń je przed dodaniem UNIQUE constraint.")
            for dup in duplicates:
                print(f"   api_match_id={dup[0]} występuje {dup[1]} razy")
        else:
            # Dodaj UNIQUE constraint przez utworzenie nowej tabeli
            print("Dodawanie UNIQUE constraint...")
            try:
                # SQLite nie obsługuje ADD CONSTRAINT, więc musimy użyć innego podejścia
                # Sprawdzamy czy możemy dodać index unique
                cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_api_match_id_unique ON matches(api_match_id) WHERE api_match_id IS NOT NULL')
                conn.commit()
                print("✓ UNIQUE constraint został dodany (jako index).")
            except sqlite3.OperationalError as e:
                print(f"⚠️  Nie można dodać UNIQUE constraint: {e}")
                print("   Kolumna została dodana, ale bez UNIQUE constraint.")
        
        # Sprawdź strukturę tabeli
        cursor.execute("PRAGMA table_info(matches)")
        columns_info = cursor.fetchall()
        
        print("\nAktualna struktura tabeli matches:")
        for col in columns_info:
            print(f"  - {col[1]} ({col[2]})")
        
    except sqlite3.Error as e:
        print(f"Błąd podczas dodawania kolumny: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Dodawanie kolumny api_match_id")
    print("=" * 50)
    print()
    
    add_api_match_id_column()

