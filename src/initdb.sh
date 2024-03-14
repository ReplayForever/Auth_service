#!/bin/bash -e

echo "ADDING pg_partman_bgw TO postgresql.conf"
echo "shared_preload_libraries = 'pg_partman_bgw'" >> /var/lib/postgresql/data/postgresql.conf
# echo "pg_partman_bgw.interval = 3600" >> /var/lib/postgresql/data/postgresql.conf
# echo "pg_partman_bgw.role = 'app'" >> /var/lib/postgresql/data/postgresql.conf
# echo "pg_partman_bgw.dbname = 'auth_database'" >> /var/lib/postgresql/data/postgresql.conf

# Перезагрузка PostgreSQL
echo "Restarting PostgreSQL..."
pg_ctl -D /var/lib/postgresql/data restart

echo "Creating partman extension"
psql -v ON_ERROR_STOP=1 --username "app" --dbname "auth_database" <<-EOSQL
    CREATE SCHEMA partman;
    CREATE EXTENSION pg_partman;
EOSQL
