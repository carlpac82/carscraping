#!/usr/bin/env python3
import os
import sys

# Forçar SQLite local
os.environ.pop('DATABASE_URL', None)
os.environ['USE_POSTGRES'] = '0'

# Importar e executar main
sys.path.insert(0, os.path.dirname(__file__))
import main
