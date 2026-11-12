#!/bin/bash
# ==============================================================================
# Automated Daily MySQL Backup Script
# Place in /usr/local/bin/mysql_backup.sh
# Crontab: 0 2 * * * /usr/local/bin/mysql_backup.sh > /var/log/db_backup.log 2>&1
# ==============================================================================
set -e

BACKUP_DIR="/var/backups/mysql"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="customer_support_db"
DB_USER="helpdesk_user"
# Prefer reading password from ~/.my.cnf instead of plaintext arguments

mkdir -p $BACKUP_DIR

echo "Starting backup of $DB_NAME at $(date)..."
mysqldump --single-transaction --quick --lock-tables=false -u $DB_USER $DB_NAME | gzip > "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

# Retain only last 14 days of backups
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +14 -delete

echo "Backup complete: ${DB_NAME}_${TIMESTAMP}.sql.gz"
