#!/bin/bash
# Chiang Mai Guide — принудительный запуск сборщика и обновления базы
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PYTHON_BIN="/opt/miniconda3/bin/python3"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

"$PYTHON_BIN" "$DIR/smart_assistant.py" --force
