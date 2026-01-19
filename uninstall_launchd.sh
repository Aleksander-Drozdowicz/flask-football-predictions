#!/bin/bash

# Skrypt odinstalowujący launchd

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "=========================================="
echo "Odinstalowywanie automatycznej synchronizacji"
echo "=========================================="
echo ""

# Zatrzymaj i usuń zadania
echo "1. Zatrzymywanie zadań..."
launchctl unload "$LAUNCH_AGENTS_DIR/com.footballpredictions.sync.plist" 2>/dev/null
launchctl unload "$LAUNCH_AGENTS_DIR/com.footballpredictions.update.plist" 2>/dev/null
echo "   ✓ Zadania zatrzymane"
echo ""

# Usuń pliki
echo "2. Usuwanie plików konfiguracyjnych..."
rm -f "$LAUNCH_AGENTS_DIR/com.footballpredictions.sync.plist"
rm -f "$LAUNCH_AGENTS_DIR/com.footballpredictions.update.plist"
echo "   ✓ Pliki usunięte"
echo ""

echo "=========================================="
echo "Odinstalowanie zakończone!"
echo "=========================================="





