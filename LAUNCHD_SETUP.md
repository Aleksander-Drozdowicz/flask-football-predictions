# Konfiguracja automatycznego uruchamiania skryptów synchronizacji

## Pliki launchd

Utworzono dwa pliki konfiguracyjne dla launchd:

1. **com.footballpredictions.sync.plist** - Pełna synchronizacja (raz dziennie o północy)
2. **com.footballpredictions.update.plist** - Szybka aktualizacja wyników (co godzinę)

## Instalacja

### Krok 1: Utwórz katalog na logi

```bash
mkdir -p ~/Documents/licencjat/logs
```

### Krok 2: Skopiuj pliki .plist do katalogu LaunchAgents

```bash
cp ~/Documents/licencjat/com.footballpredictions.sync.plist ~/Library/LaunchAgents/
cp ~/Documents/licencjat/com.footballpredictions.update.plist ~/Library/LaunchAgents/
```

### Krok 3: Załaduj zadania do launchd

```bash
launchctl load ~/Library/LaunchAgents/com.footballpredictions.sync.plist
launchctl load ~/Library/LaunchAgents/com.footballpredictions.update.plist
```

## Sprawdzanie statusu

### Sprawdź czy zadania są załadowane

```bash
launchctl list | grep footballpredictions
```

### Sprawdź logi

```bash
# Logi pełnej synchronizacji
tail -f ~/Documents/licencjat/logs/sync_full.log

# Logi szybkiej aktualizacji
tail -f ~/Documents/licencjat/logs/sync_update.log

# Błędy
tail -f ~/Documents/licencjat/logs/sync_full_error.log
tail -f ~/Documents/licencjat/logs/sync_update_error.log
```

## Ręczne uruchomienie (test)

### Pełna synchronizacja

```bash
launchctl start com.footballpredictions.sync
```

### Szybka aktualizacja

```bash
launchctl start com.footballpredictions.update
```

## Odinstalowanie

### Zatrzymaj zadania

```bash
launchctl unload ~/Library/LaunchAgents/com.footballpredictions.sync.plist
launchctl unload ~/Library/LaunchAgents/com.footballpredictions.update.plist
```

### Usuń pliki

```bash
rm ~/Library/LaunchAgents/com.footballpredictions.sync.plist
rm ~/Library/LaunchAgents/com.footballpredictions.update.plist
```

## Harmonogram

- **Pełna synchronizacja**: Codziennie o 00:00 (północ)
  - Pobiera mecze z miesiąca wstecz i miesiąca do przodu
  - Dodaje nowe mecze i aktualizuje istniejące

- **Szybka aktualizacja**: Co godzinę
  - Aktualizuje tylko wyniki meczów z ostatnich 7 dni
  - Szybsze, używa mniej requestów do API

## Uwagi

- Upewnij się, że klucz API jest ustawiony w pliku `sync_matches.py` lub jako zmienna środowiskowa
- Logi są zapisywane w katalogu `logs/` w projekcie
- Jeśli zmienisz ścieżkę do projektu, zaktualizuj pliki .plist





