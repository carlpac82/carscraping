import os
import sys

# Remove DATABASE_URL para usar SQLite local
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

# Importar e iniciar o servidor
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
