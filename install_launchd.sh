#!/bin/bash

# Skrypt instalacyjny dla launchd

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "=========================================="
echo "Instalacja automatycznej synchronizacji"
echo "=========================================="
echo ""

# Utwórz katalog na logi
echo "1. Tworzenie katalogu na logi..."
mkdir -p "$SCRIPT_DIR/logs"
echo "   ✓ Katalog utworzony: $SCRIPT_DIR/logs"
echo ""

# Skopiuj pliki .plist
echo "2. Kopiowanie plików konfiguracyjnych..."
cp "$SCRIPT_DIR/com.footballpredictions.sync.plist" "$LAUNCH_AGENTS_DIR/"
cp "$SCRIPT_DIR/com.footballpredictions.update.plist" "$LAUNCH_AGENTS_DIR/"
echo "   ✓ Pliki skopiowane do $LAUNCH_AGENTS_DIR"
echo ""

# Zaktualizuj ścieżki w plikach .plist (na wypadek gdyby były różne)
echo "3. Aktualizowanie ścieżek w plikach .plist..."
sed -i '' "s|/Users/aleksanderdrozdowicz/Documents/licencjat|$SCRIPT_DIR|g" "$LAUNCH_AGENTS_DIR/com.footballpredictions.sync.plist"
sed -i '' "s|/Users/aleksanderdrozdowicz/Documents/licencjat|$SCRIPT_DIR|g" "$LAUNCH_AGENTS_DIR/com.footballpredictions.update.plist"
echo "   ✓ Ścieżki zaktualizowane"
echo ""

# Załaduj zadania
echo "4. Ładowanie zadań do launchd..."
launchctl load "$LAUNCH_AGENTS_DIR/com.footballpredictions.sync.plist" 2>/dev/null || launchctl load -w "$LAUNCH_AGENTS_DIR/com.footballpredictions.sync.plist"
launchctl load "$LAUNCH_AGENTS_DIR/com.footballpredictions.update.plist" 2>/dev/null || launchctl load -w "$LAUNCH_AGENTS_DIR/com.footballpredictions.update.plist"
echo "   ✓ Zadania załadowane"
echo ""

# Sprawdź status
echo "5. Sprawdzanie statusu..."
if launchctl list | grep -q "com.footballpredictions"; then
    echo "   ✓ Zadania są aktywne:"
    launchctl list | grep "com.footballpredictions"
else
    echo "   ⚠️  Zadania nie są widoczne (może być normalne przy pierwszej instalacji)"
fi
echo ""

echo "=========================================="
echo "Instalacja zakończona!"
echo "=========================================="
echo ""
echo "Harmonogram:"
echo "  • Pełna synchronizacja: Codziennie o 00:00"
echo "  • Szybka aktualizacja: Co godzinę"
echo ""
echo "Logi:"
echo "  • $SCRIPT_DIR/logs/sync_full.log"
echo "  • $SCRIPT_DIR/logs/sync_update.log"
echo ""
echo "Aby sprawdzić status:"
echo "  launchctl list | grep footballpredictions"
echo ""
echo "Aby odinstalować:"
echo "  ./uninstall_launchd.sh"





