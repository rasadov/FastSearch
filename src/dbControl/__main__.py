from utils import (execute_sql_statement, create_tables,
                   create_owner_account, grant_privileges,
                   create_extension, clear)

def print_options():
    print("Execute sql statement [0]")
    print("Create tables [1]")
    print("Create owner account [2]")
    print("Grant privileges [3]")
    print("Create extension [4]")
    print("Exit [5]")

choice = input("Enter your choice: ")

while True:
    if choice == "0":
        print("Enter your SQL statement:")
        ans = input()
        execute_sql_statement(ans)
    elif choice == "1":
        create_tables()
    elif choice == "2":
        create_owner_account()
    elif choice == "3":
        grant_privileges()
    elif choice == "4":
        print("Enter the extension name (blank for pg_trgm):")
        ans = input()
        if ans:
            create_extension(ans)
        else:
            create_extension()
    elif choice == "5":
        break
    clear()
    print_options()
    choice = input("Enter your choice: ")
