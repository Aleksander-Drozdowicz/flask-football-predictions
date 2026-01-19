# Synchronizacja meczów z football-data.org API

## Instalacja

1. Zainstaluj zależności:
```bash
pip install requests
```

lub

```bash
pip install -r requirements.txt
```

## Konfiguracja API Key

### Sposób 1: Zmienna środowiskowa (zalecane)
```bash
export FOOTBALL_DATA_API_KEY='twój_klucz_api'
```

### Sposób 2: Edycja pliku
Edytuj plik `sync_matches.py` i zmień:
```python
API_KEY = "TWÓJ_KLUCZ_API"
```
na:
```python
API_KEY = "twój_rzeczywisty_klucz"
```

## Uzyskanie klucza API

1. Zarejestruj się na: https://www.football-data.org/register
2. Zaloguj się do swojego konta
3. Skopiuj swój API Key
4. Darmowy plan oferuje 100 requestów dziennie (niezarejestrowani) lub 50 requestów/minutę (zarejestrowani)

## Użycie

### Pełna synchronizacja (dodawanie nowych meczów + aktualizacja wyników)
```bash
python sync_matches.py
```

Pobiera mecze z Premier League (kod: PL) z dzisiaj i jutro i:
- Dodaje nowe mecze do bazy
- Aktualizuje wyniki istniejących meczów
- Aktualizuje daty i nazwy drużyn

### Szybka aktualizacja tylko wyników
```bash
python sync_matches.py update
```

Aktualizuje tylko wyniki meczów z ostatnich 7 dni (szybsze, mniej requestów do API).

## Automatyzacja

Możesz uruchamiać skrypt automatycznie:

### Linux/Mac (cron)
```bash
# Edytuj crontab
crontab -e

# Dodaj linię (aktualizacja co godzinę)
0 * * * * cd /ścieżka/do/projektu && python sync_matches.py update
```

### Windows (Task Scheduler)
Utwórz zadanie w Harmonogramie zadań, które uruchamia:
```
python C:\ścieżka\do\projektu\sync_matches.py update
```

## Struktura bazy danych

Skrypt automatycznie dodaje kolumnę `api_match_id` do tabeli `matches` jeśli nie istnieje. Ta kolumna przechowuje ID meczu z football-data.org, co pozwala na:
- Unikalną identyfikację meczów
- Aktualizację wyników bez duplikatów
- Łączenie danych z różnych źródeł

## Premier League (Kod: PL)

Skrypt domyślnie pobiera mecze z Premier League. Aby zmienić ligę, edytuj:
```python
COMPETITION_CODE = "PL"  # Zmień na kod innej ligi
```

Przykładowe kody lig:
- PL: Premier League (Anglia)
- PD: La Liga (Hiszpania)
- BL1: Bundesliga (Niemcy)
- SA: Serie A (Włochy)
- FL1: Ligue 1 (Francja)
- DED: Eredivisie (Holandia)
- PPL: Primeira Liga (Portugalia)

## Uwagi

- Darmowy plan football-data.org: 100 requestów/dzień (niezarejestrowani) lub 50 requestów/minutę (zarejestrowani)
- Pełna synchronizacja używa 1 request (pobiera mecze z zakresu dat)
- Tryb `update` używa 1 request (tylko ostatnie 7 dni)
- Skrypt automatycznie obsługuje błędy API i brakujące dane
- API używa formatu UTC dla dat

## Różnice w stosunku do api-football.com

- **Autoryzacja**: `X-Auth-Token` zamiast `x-apisports-key`
- **Endpoint**: `/competitions/{code}/matches` zamiast `/fixtures`
- **Kody lig**: Używa kodów (PL, PD, etc.) zamiast ID numerycznych
- **Struktura odpowiedzi**: `{"matches": [...]}` zamiast `{"response": [...]}`
- **Wyniki**: `score.fullTime.home/away` zamiast `goals.home/away`
