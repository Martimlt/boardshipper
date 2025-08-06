import django
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boardshipper_project.settings')
django.setup()

from django.db import connection

# Check if migrations table exists
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Existing tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check migrations
    if any('django_migrations' in table for table in tables):
        cursor.execute("SELECT app, name FROM django_migrations WHERE app='boardshipper';")
        migrations = cursor.fetchall()
        print("\nBoardshipper migrations applied:")
        for migration in migrations:
            print(f"  - {migration[0]}: {migration[1]}")
    else:
        print("\nNo django_migrations table found!")