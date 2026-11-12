"""Generate database/schema.sql directly from SQLAlchemy models using MySQL dialect.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import mysql
from app.config import Config
from app import create_app
from app.extensions import db
import app.models # register all models

app = create_app(Config)

def generate():
    out_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with app.app_context():
        tables = db.metadata.sorted_tables
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write("-- =========================================================\n")
            f.write("-- AI-POWERED CUSTOMER SUPPORT & HELPDESK PLATFORM\n")
            f.write("-- MYSQL RELATIONAL DATABASE ARCHITECTURE DDL\n")
            f.write("-- Generated automatically from SQLAlchemy ORM Metadata\n")
            f.write("-- Target Database: customer_support_db (utf8mb4 / InnoDB)\n")
            f.write("-- =========================================================\n\n")
            f.write("CREATE DATABASE IF NOT EXISTS customer_support_db\n")
            f.write("  CHARACTER SET utf8mb4\n")
            f.write("  COLLATE utf8mb4_unicode_ci;\n\n")
            f.write("USE customer_support_db;\n\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
            
            for table in tables:
                ddl = str(CreateTable(table).compile(dialect=mysql.dialect())).strip()
                f.write(f"-- Table structure for `{table.name}`\n")
                f.write(f"DROP TABLE IF EXISTS `{table.name}`;\n")
                f.write(ddl + ";\n\n")
            
            f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
    print(f"Generated {out_file} successfully.")

if __name__ == '__main__':
    generate()
