#!/bin/bash
set -e

echo "Creating databases..."

# Create swiyu_verifier database
psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
    CREATE DATABASE swiyu_verifier;
    ALTER DATABASE swiyu_verifier OWNER TO postgres;
EOSQL

# Create prosignum database
psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
    CREATE DATABASE prosignum;
    ALTER DATABASE prosignum OWNER TO postgres;
EOSQL

echo "Databases created successfully!"
