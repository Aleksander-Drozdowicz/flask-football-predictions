"""
Skrypt do synchronizacji meczów z football-data.org API
Pobiera mecze z ligi Premier League (PL) i aktualizuje wyniki w bazie danych
"""

import requests
import sqlite3
from datetime import datetime, timedelta
import os
import sys

# Konfiguracja
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "80f5c894cc4b4471bec41c92b091d96e")  # Ustaw zmienną środowiskową lub wpisz klucz
COMPETITION_CODE = "PL"  # Premier League (kod ligi)
DATABASE = "football_predictions.db"
BASE_URL = "https://api.football-data.org/v4"

headers = {
    "X-Auth-Token": API_KEY
}


def get_db():
    """Pobiera połączenie z bazą danych"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_fixtures_from_api(competition_code="PL", date_from=None, date_to=None):
    """
    Pobiera mecze z football-data.org API
    
    Args:
        competition_code: Kod ligi (domyślnie PL - Premier League)
        date_from: Data początkowa w formacie YYYY-MM-DD
        date_to: Data końcowa w formacie YYYY-MM-DD
    """
    url = f"{BASE_URL}/competitions/{competition_code}/matches"
    
    params = {}
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Sprawdź czy są błędy w odpowiedzi
        if "error" in data or "message" in data:
            print(f"Błąd API: {data.get('message', data.get('error', 'Unknown error'))}")
            return []
        
        return data.get("matches", [])
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania danych z API: {e}")
        if hasattr(e.response, 'text'):
            print(f"Odpowiedź serwera: {e.response.text}")
        return []


def sync_matches_from_api(competition_code="PL", days_back=30, days_ahead=30):
    """
    Synchronizuje mecze z football-data.org do bazy danych
    
    Args:
        competition_code: Kod ligi (domyślnie PL - Premier League)
        days_back: Liczba dni wstecz, dla których pobierać mecze (domyślnie 30 - miesiąc)
        days_ahead: Liczba dni do przodu, dla których pobierać mecze (domyślnie 30 - miesiąc)
    """
    conn = get_db()
    cursor = conn.cursor()
    
    print(f"Pobieranie meczów z ligi {competition_code} (Premier League)...")
    
    # Pobierz mecze z zakresu dat (miesiąc wstecz do miesiąc do przodu)
    today = datetime.now().date()
    date_from = today - timedelta(days=days_back)
    date_to = today + timedelta(days=days_ahead)
    
    date_from_str = date_from.strftime("%Y-%m-%d")
    date_to_str = date_to.strftime("%Y-%m-%d")
    
    print(f"Pobieranie meczów z zakresu: {date_from_str} - {date_to_str}")
    print(f"  (miesiąc wstecz: {days_back} dni, miesiąc do przodu: {days_ahead} dni)")
    
    fixtures = fetch_fixtures_from_api(
        competition_code=competition_code,
        date_from=date_from_str,
        date_to=date_to_str
    )
    
    if not fixtures:
        print("Nie znaleziono żadnych meczów. Sprawdź klucz API i dostępność danych.")
        conn.close()
        return
    
    print(f"\nPrzetwarzanie {len(fixtures)} meczów...")
    
    added_count = 0
    updated_count = 0
    
    for match in fixtures:
        api_match_id = match["id"]
        home_team = match["homeTeam"]["name"]
        away_team = match["awayTeam"]["name"]
        
        # Konwersja daty z UTC ISO format na lokalny format
        match_date_utc = match["utcDate"]
        # Konwertuj z formatu "2024-03-15T20:00:00Z" na "2024-03-15T20:00:00"
        match_date = match_date_utc.replace("Z", "").replace("+00:00", "")
        
        # Wyniki (może być None jeśli mecz się nie zakończył)
        score = match.get("score", {})
        full_time = score.get("fullTime", {})
        home_score = full_time.get("home")
        away_score = full_time.get("away")
        
        # Sprawdź czy mecz już istnieje w bazie
        cursor.execute("SELECT id, home_score, away_score FROM matches WHERE api_match_id = ?", 
                      (api_match_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Aktualizuj tylko jeśli wynik się zmienił lub nie był ustawiony
            if (existing["home_score"] != home_score or 
                existing["away_score"] != away_score or
                (existing["home_score"] is None and home_score is not None)):
                
                cursor.execute("""
                    UPDATE matches
                    SET home_team = ?, away_team = ?, match_date = ?, 
                        home_score = ?, away_score = ?
                    WHERE api_match_id = ?
                """, (home_team, away_team, match_date, home_score, away_score, api_match_id))
                updated_count += 1
                print(f"  ✓ Zaktualizowano: {home_team} vs {away_team} ({home_score or '-'}:{away_score or '-'})")
        else:
            # Dodaj nowy mecz
            cursor.execute("""
                INSERT INTO matches (home_team, away_team, match_date, home_score, away_score, 
                                   created_at, api_match_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (home_team, away_team, match_date, home_score, away_score, 
                  datetime.now().isoformat(), api_match_id))
            added_count += 1
            print(f"  + Dodano: {home_team} vs {away_team} ({match_date})")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Synchronizacja zakończona!")
    print(f"  Dodano: {added_count} meczów")
    print(f"  Zaktualizowano: {updated_count} meczów")


def update_results_only(competition_code="PL", days_back=7):
    """
    Aktualizuje tylko wyniki istniejących meczów (szybsze dla częstych aktualizacji)
    
    Args:
        competition_code: Kod ligi
        days_back: Liczba dni wstecz, dla których sprawdzać wyniki
    """
    conn = get_db()
    cursor = conn.cursor()
    
    print(f"Aktualizowanie wyników meczów z ostatnich {days_back} dni...")
    
    today = datetime.now().date()
    date_from = today - timedelta(days=days_back)
    
    date_from_str = date_from.strftime("%Y-%m-%d")
    date_to_str = today.strftime("%Y-%m-%d")
    
    fixtures = fetch_fixtures_from_api(
        competition_code=competition_code,
        date_from=date_from_str,
        date_to=date_to_str
    )
    
    updated_count = 0
    
    for match in fixtures:
        api_match_id = match["id"]
        score = match.get("score", {})
        full_time = score.get("fullTime", {})
        home_score = full_time.get("home")
        away_score = full_time.get("away")
        
        # Aktualizuj tylko jeśli mecz istnieje w bazie i wynik się zmienił
        cursor.execute("""
            UPDATE matches
            SET home_score = ?, away_score = ?
            WHERE api_match_id = ? 
              AND (home_score IS NULL OR away_score IS NULL 
                   OR home_score != ? OR away_score != ?)
        """, (home_score, away_score, api_match_id, home_score, away_score))
        
        if cursor.rowcount > 0:
            updated_count += 1
            home_team = match["homeTeam"]["name"]
            away_team = match["awayTeam"]["name"]
            print(f"  ✓ {home_team} vs {away_team}: {home_score or '-'}:{away_score or '-'}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Zaktualizowano {updated_count} wyników")


if __name__ == "__main__":
    if API_KEY == "TWÓJ_KLUCZ_API" or not API_KEY:
        print("⚠️  UWAGA: Ustaw klucz API!")
        print("   Sposób 1: Ustaw zmienną środowiskową:")
        print("   export FOOTBALL_DATA_API_KEY='twój_klucz'")
        print("   Sposób 2: Edytuj plik sync_matches.py i wpisz klucz w API_KEY")
        print("\n   Klucz API możesz uzyskać na: https://www.football-data.org/register")
        sys.exit(1)
    
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        # Tryb szybkiej aktualizacji tylko wyników
        update_results_only()
    else:
        # Pełna synchronizacja (dodawanie nowych meczów + aktualizacja wyników)
        # Pobiera mecze z miesiąca wstecz i miesiąca do przodu
        sync_matches_from_api(days_back=30, days_ahead=30)
