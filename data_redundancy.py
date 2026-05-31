import sqlite3
import hashlib
import os
from datetime import datetime

def clear():
    os.system('cls')

def create_database():
    conn = sqlite3.connect("cloud_storage.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cloud_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            data TEXT NOT NULL,
            hash_value TEXT UNIQUE NOT NULL,
            added_by TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

def generate_hash(data):
    return hashlib.sha256(data.strip().lower().encode()).hexdigest()

def banner(username):
    print("=" * 60)
    print("   ☁️  Personal Cloud Data Redundancy Removal System")
    print("=" * 60)
    print(f"   👤 User: {username}  |  🕐 {datetime.now().strftime('%I:%M %p')}")
    print("=" * 60)

def add_record(conn, username):
    print("\n📂 CATEGORIES: 1.Emails  2.Phone Numbers  3.Names  4.Custom")
    choice = input("Choose category (1-4): ").strip()

    categories = {"1": "Email", "2": "Phone", "3": "Name", "4": "Custom"}
    category = categories.get(choice, "Custom")

    data = input(f"Enter {category} data: ").strip()

    if not data:
        print("❌ Empty data not allowed!")
        return

    hash_value = generate_hash(data)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn.execute(
            "INSERT INTO cloud_records (category, data, hash_value, added_by, timestamp) VALUES (?, ?, ?, ?, ?)",
            (category, data, hash_value, username, timestamp)
        )
        conn.commit()
        print(f"\n✅ SUCCESS! '{data}' added as unique {category} record!")
    except sqlite3.IntegrityError:
        print(f"\n🚨 DUPLICATE DETECTED!")
        print(f"   '{data}' already exists in cloud database!")
        print(f"   ❌ Rejected to maintain data integrity!")

def add_bulk(conn, username):
    print("\n📥 BULK DATA ENTRY")
    print("Enter multiple records (one per line)")
    print("Type 'DONE' when finished\n")

    added = 0
    duplicates = 0

    print("\n📂 CATEGORIES: 1.Emails  2.Phone Numbers  3.Names  4.Custom")
    choice = input("Choose category (1-4): ").strip()
    categories = {"1": "Email", "2": "Phone", "3": "Name", "4": "Custom"}
    category = categories.get(choice, "Custom")

    while True:
        data = input(f"Enter {category}: ").strip()
        if data.upper() == "DONE":
            break
        if not data:
            continue

        hash_value = generate_hash(data)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn.execute(
                "INSERT INTO cloud_records (category, data, hash_value, added_by, timestamp) VALUES (?, ?, ?, ?, ?)",
                (category, data, hash_value, username, timestamp)
            )
            conn.commit()
            print(f"  ✅ Added: {data}")
            added += 1
        except sqlite3.IntegrityError:
            print(f"  ❌ Duplicate: {data}")
            duplicates += 1

    print(f"\n📊 Bulk Entry Complete!")
    print(f"   ✅ Added    : {added} records")
    print(f"   ❌ Rejected : {duplicates} duplicates")

def view_records(conn):
    print("\n📂 FILTER BY: 1.All  2.Email  3.Phone  4.Name  5.Custom")
    choice = input("Choose filter (1-5): ").strip()

    filters = {"2": "Email", "3": "Phone", "4": "Name", "5": "Custom"}

    if choice == "1":
        cursor = conn.execute("SELECT id, category, data, added_by, timestamp FROM cloud_records")
    elif choice in filters:
        cursor = conn.execute(
            "SELECT id, category, data, added_by, timestamp FROM cloud_records WHERE category=?",
            (filters[choice],)
        )
    else:
        cursor = conn.execute("SELECT id, category, data, added_by, timestamp FROM cloud_records")

    records = cursor.fetchall()

    print("\n" + "=" * 60)
    print("           📊 CLOUD DATABASE RECORDS")
    print("=" * 60)

    if not records:
        print("   No records found!")
    else:
        for r in records:
            print(f"  ID: {r[0]}  |  [{r[1]}]  |  {r[2]}")
            print(f"       Added by: {r[3]}  |  {r[4]}")
            print("  " + "-" * 56)

    print(f"\n  Total Records: {len(records)}")
    print("=" * 60)

def search_record(conn):
    keyword = input("\n🔍 Enter search keyword: ").strip()
    cursor = conn.execute(
        "SELECT id, category, data, added_by, timestamp FROM cloud_records WHERE data LIKE ?",
        (f"%{keyword}%",)
    )
    results = cursor.fetchall()

    print(f"\n🔍 Search Results for '{keyword}':")
    print("=" * 60)
    if not results:
        print("  No matching records found!")
    else:
        for r in results:
            print(f"  ID: {r[0]}  |  [{r[1]}]  |  {r[2]}")
            print(f"       Added by: {r[3]}  |  {r[4]}")
    print("=" * 60)

def generate_report(conn):
    print("\n" + "=" * 60)
    print("           📈 CLOUD DATABASE REPORT")
    print("=" * 60)

    total = conn.execute("SELECT COUNT(*) FROM cloud_records").fetchone()[0]
    emails = conn.execute("SELECT COUNT(*) FROM cloud_records WHERE category='Email'").fetchone()[0]
    phones = conn.execute("SELECT COUNT(*) FROM cloud_records WHERE category='Phone'").fetchone()[0]
    names = conn.execute("SELECT COUNT(*) FROM cloud_records WHERE category='Name'").fetchone()[0]
    custom = conn.execute("SELECT COUNT(*) FROM cloud_records WHERE category='Custom'").fetchone()[0]

    print(f"  📊 Total Unique Records : {total}")
    print(f"  📧 Email Records        : {emails}")
    print(f"  📱 Phone Records        : {phones}")
    print(f"  👤 Name Records         : {names}")
    print(f"  📁 Custom Records       : {custom}")
    print(f"\n  🛡️  Duplicate Protection : ACTIVE")
    print(f"  ☁️  Cloud Status         : ONLINE")
    print(f"  🕐 Report Generated     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def delete_record(conn):
    record_id = input("\n🗑️  Enter ID to delete: ").strip()
    cursor = conn.execute("SELECT data FROM cloud_records WHERE id=?", (record_id,))
    record = cursor.fetchone()

    if not record:
        print("❌ Record not found!")
        return

    confirm = input(f"Delete '{record[0]}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        conn.execute("DELETE FROM cloud_records WHERE id=?", (record_id,))
        conn.commit()
        print("✅ Record deleted successfully!")
    else:
        print("❌ Deletion cancelled!")

def main():
    print("=" * 60)
    print("   ☁️  Cloud Data Redundancy Removal System")
    print("=" * 60)
    username = input("Enter your name: ").strip() or "Admin"

    conn = create_database()

    while True:
        clear()
        banner(username)
        print("\n  📋 MAIN MENU")
        print("  1️⃣  Add Single Record")
        print("  2️⃣  Add Bulk Records")
        print("  3️⃣  View All Records")
        print("  4️⃣  Search Records")
        print("  5️⃣  Generate Report")
        print("  6️⃣  Delete Record")
        print("  7️⃣  Exit")
        print("\n" + "=" * 60)

        choice = input("  Choose option (1-7): ").strip()

        if choice == "1":
            add_record(conn, username)
        elif choice == "2":
            add_bulk(conn, username)
        elif choice == "3":
            view_records(conn)
        elif choice == "4":
            search_record(conn)
        elif choice == "5":
            generate_report(conn)
        elif choice == "6":
            delete_record(conn)
        elif choice == "7":
            print(f"\n☁️  Goodbye {username}! Cloud system shutting down... 👋")
            conn.close()
            break
        else:
            print("❌ Invalid choice!")

        input("\n  Press Enter to continue...")

main()