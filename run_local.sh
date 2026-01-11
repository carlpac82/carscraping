#!/bin/bash
# Script para correr servidor local com SQLite

# Remover DATABASE_URL para forçar SQLite
export DATABASE_URL=""
export USE_POSTGRES="false"

# Correr servidor
python3 main.py
