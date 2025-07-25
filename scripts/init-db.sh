#!/bin/bash
set -e

# Database initialization script for Big Kahuna Burger HR Platform
echo "Initializing Big Kahuna Burger HR Platform database..."

# Create additional databases if needed
# psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
#     CREATE DATABASE bigkahuna_hr_test;
#     GRANT ALL PRIVILEGES ON DATABASE bigkahuna_hr_test TO $POSTGRES_USER;
# EOSQL

# Set up database extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable UUID extension
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Enable case-insensitive text extension
    CREATE EXTENSION IF NOT EXISTS "citext";
    
    -- Create custom types and functions if needed
    -- Example: CREATE TYPE job_status AS ENUM ('active', 'inactive', 'draft');
EOSQL

echo "Database initialization completed successfully!" 