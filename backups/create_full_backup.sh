#!/bin/bash

# Full Backup Script for CarScraping Project
# Date: $(date +%Y%m%d_%H%M%S)

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
BACKUP_NAME="backup_full_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "🔄 Starting full backup..."

# Create backup directory structure
mkdir -p "${BACKUP_PATH}"
mkdir -p "${BACKUP_PATH}/database"
mkdir -p "${BACKUP_PATH}/code"
mkdir -p "${BACKUP_PATH}/static"
mkdir -p "${BACKUP_PATH}/templates"

# 1. Backup PostgreSQL database from Railway
echo "📦 Backing up PostgreSQL database..."
if [ ! -z "$DATABASE_URL" ]; then
    pg_dump "$DATABASE_URL" > "${BACKUP_PATH}/database/postgres_dump_${TIMESTAMP}.sql"
    echo "✅ Database backup completed"
else
    echo "⚠️  DATABASE_URL not set, skipping PostgreSQL backup"
fi

# 2. Backup all Python code
echo "📝 Backing up Python code..."
cp *.py "${BACKUP_PATH}/code/" 2>/dev/null || true

# 3. Backup static files (images, PDFs, etc)
echo "🖼️  Backing up static files..."
cp -r static/* "${BACKUP_PATH}/static/" 2>/dev/null || true

# 4. Backup templates
echo "📄 Backing up templates..."
cp -r templates/* "${BACKUP_PATH}/templates/" 2>/dev/null || true

# 5. Backup configuration files
echo "⚙️  Backing up configuration files..."
cp requirements.txt "${BACKUP_PATH}/" 2>/dev/null || true
cp railway.json "${BACKUP_PATH}/" 2>/dev/null || true
cp .gitignore "${BACKUP_PATH}/" 2>/dev/null || true
cp README.md "${BACKUP_PATH}/" 2>/dev/null || true

# 6. Create metadata file
echo "📋 Creating backup metadata..."
cat > "${BACKUP_PATH}/backup_info.txt" << EOF
Backup Information
==================
Date: $(date)
Timestamp: ${TIMESTAMP}
Host: $(hostname)
User: $(whoami)
Project: CarScraping - Auto Prudente Rent a Car

Contents:
- PostgreSQL database dump
- All Python source code
- Static files (images, PDFs, T&C)
- Email templates (PT, EN, FR)
- Configuration files

Git Info:
Branch: $(git branch --show-current 2>/dev/null || echo "N/A")
Commit: $(git rev-parse HEAD 2>/dev/null || echo "N/A")
Status: $(git status --short 2>/dev/null | wc -l) modified files
EOF

# 7. Compress backup
echo "🗜️  Compressing backup..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"
cd ..

echo "✅ Full backup completed: ${BACKUP_PATH}.tar.gz"
echo "📊 Backup size: $(du -h ${BACKUP_PATH}.tar.gz | cut -f1)"
