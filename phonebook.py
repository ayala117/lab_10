import psycopg2
import csv

# PostgreSQL-ге қосылу
def connect_db():
    return psycopg2.connect(
        dbname="postgres",      # Базаның атын өзгертуге болады (мысалы, phonebook)
        user="ayala",
        password="ayala1234",   # Өз пароліңді орнатқаныңды қолданысқа енгіз
        host="localhost",
        port="5432"
    )

# Кестені құру (егер ол жоқ болса)
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            phone VARCHAR(20)
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Деректерді CSV файлдан жүктеу
def load_data_from_csv(filename):
    conn = connect_db()
    cursor = conn.cursor()

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Егер CSV-де баған атаулары болса, бірінші жолды өткізіп жібереміз
        for row in reader:
            cursor.execute("""
                INSERT INTO phonebook (name, phone)
                VALUES (%s, %s);
            """, (row[0], row[1]))
    
    conn.commit()
    cursor.close()
    conn.close()

# Қолданушыдан деректерді алу және оларды енгізу
def insert_data():
    name = input("Enter name: ")
    phone = input("Enter phone number: ")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO phonebook (name, phone)
        VALUES (%s, %s);
    """, (name, phone))
    
    conn.commit()
    cursor.close()
    conn.close()

# Деректерді жаңарту
def update_data():
    name = input("Enter the name of the person to update: ")
    new_name = input("Enter the new name: ")
    new_phone = input("Enter the new phone number: ")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE phonebook
        SET name = %s, phone = %s
        WHERE name = %s;
    """, (new_name, new_phone, name))

    conn.commit()
    cursor.close()
    conn.close()

# Деректерді сұрыптау (фильтрация)
def query_data():
    filter_name = input("Enter a name to filter: ")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM phonebook WHERE name LIKE %s;
    """, (f'%{filter_name}%',))

    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")

    cursor.close()
    conn.close()

# Деректерді жою
def delete_data():
    name = input("Enter the name or phone number to delete: ")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM phonebook
        WHERE name = %s OR phone = %s;
    """, (name, name))

    conn.commit()
    cursor.close()
    conn.close()

# Негізгі бағдарлама
def main():
    create_table()  # Кестені жасау

    while True:
        print("\nPhonebook Menu:")
        print("1. Load data from CSV")
        print("2. Insert new data")
        print("3. Update data")
        print("4. Query data")
        print("5. Delete data")
        print("6. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            filename = input("Enter CSV filename: ")
            load_data_from_csv(filename)
        elif choice == "2":
            insert_data()
        elif choice == "3":
            update_data()
        elif choice == "4":
            query_data()
        elif choice == "5":
            delete_data()
        elif choice == "6":
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()



# Phonebook Menu:
# 1. Load data from CSV
# 2. Insert new data
# 3. Update data
# 4. Query data
# 5. Delete data
# 6. Exit
# Choose an option: 2
# Enter name: john
# Enter phone number: 7778889900

# Phonebook Menu:
# 1. Load data from CSV
# 2. Insert new data
# 3. Update data
# 4. Query data
# 5. Delete data
# 6. Exit
# Choose an option: 4
# Enter a name to filter: john
# ID: 2, Name: john, Phone: 7778889900

# Phonebook Menu:
# 1. Load data from CSV
# 2. Insert new data
# 3. Update data
# 4. Query data
# 5. Delete data
# 6. Exit
# Choose an option: 6