# Aplikacja do typowania meczów i statystyk drużyn

MVP aplikacji webowej stworzonej w Python 3 + Flask + SQLite + Jinja2 templates + CSS.

## Opis

Edukacyjna aplikacja do typowania wyników meczów piłkarskich. Użytkownicy mogą typować wyniki meczów, przeglądać swoje statystyki i śledzić skuteczność swoich przewidywań.

## Wymagania

- Python 3.7+
- pip (menedżer pakietów Pythona)

## Instalacja

1. Sklonuj lub pobierz projekt

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

## Uruchomienie

1. Uruchom aplikację:
```bash
python app.py
```

2. Otwórz przeglądarkę i przejdź do:
```
http://127.0.0.1:5000/
```

## Konto administratora

Aplikacja automatycznie tworzy konto administratora przy pierwszym uruchomieniu:

- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Ważne:** Zmień hasło administratora przed wdrożeniem w produkcji!

## Funkcjonalności

### Użytkownik (USER)

- Rejestracja i logowanie
- Przeglądanie meczów
- Dodawanie/edycja/usuwanie typów wyników
- Przeglądanie swoich typów ze statusem (oczekiwanie/trafiony/nietrafiony)
- Wyświetlanie statystyk (liczba ocenionych typów, trafione, skuteczność %)

### Administrator (ADMIN)

- Wszystkie funkcje użytkownika
- Dodawanie nowych meczów
- Ustawianie wyników zakończonych meczów

## Struktura projektu

```
.
├── app.py                  # Główny plik aplikacji Flask
├── requirements.txt        # Zależności projektu
├── README.md              # Ten plik
├── football_predictions.db # Baza danych SQLite (tworzona automatycznie)
├── templates/             # Szablony Jinja2
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── matches.html
│   ├── my_predictions.html
│   ├── stats.html
│   └── admin.html
└── static/
    └── css/
        └── style.css      # Style CSS
```

## Baza danych

Aplikacja używa SQLite z trzema tabelami:

- **users** - użytkownicy (id, username, password_hash, role, created_at)
- **matches** - mecze (id, home_team, away_team, match_date, home_score, away_score, created_at)
- **predictions** - typy użytkowników (id, user_id, match_id, predicted_home, predicted_away, created_at, updated_at)

Baza danych jest automatycznie tworzona przy pierwszym uruchomieniu. Plik `football_predictions.db` zostanie utworzony w katalogu głównym projektu.

## Bezpieczeństwo

- Hasła są hashowane używając Werkzeug (PBKDF2)
- Sesje używają secret key (zmień w produkcji!)
- Walidacja danych wejściowych
- Ochrona tras administratora (@admin_required)
- Ochrona tras wymagających logowania (@login_required)
- Użytkownicy mogą modyfikować tylko swoje typy

## Uwagi

- Aplikacja zawiera przykładowe mecze (8-12 rekordów) dodawane przy pierwszym uruchomieniu
- Niektóre mecze mają już ustawione wyniki do demonstracji funkcjonalności
- Aplikacja działa w trybie debug - wyłącz w produkcji

## Licencja

Projekt edukacyjny - wersja MVP.

## Autor

Aplikacja stworzona na potrzeby pracy licencjackiej.







