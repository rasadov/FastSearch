"""
This script provides a command-line interface for controlling the database.
It allows the user to execute SQL statements, create tables, create an owner account,
grant privileges, create extensions, and perform various scraping functions.

Usage:
    - Run the script to start the command-line interface.
    - Enter the corresponding number for the desired action.
    - Follow the prompts to provide additional information if required.

Note:
    - The script assumes that the necessary modules and functions are imported from the 'utils' module.
    - The 'clear' function is assumed to be defined elsewhere in the code.

Example:
    $ python __main__.py
    Enter your choice: 1
    Tables created successfully.

    Enter your choice: 2
    Owner account created successfully.

    Enter your choice: 5
    Update records [0]
    Google search [1]
    Url search [2]
    Exit [3]
    Enter your choice: 1
    Performing Google search...

    Enter your choice: 3
    Exiting...

"""

from utils import (execute_sql_statement, create_tables,
                   create_owner_account, grant_privileges,
                   create_extension, clear, update_records,
                   google_search, url_search)

def print_options():
    """
    Print the available options for the user.
    """
    print("Execute sql statement [0]")
    print("Create tables [1]")
    print("Create owner account [2]")
    print("Grant privileges [3]")
    print("Create extension [4]")
    print("Scrape Functions [5]")
    print("Exit [6]")

def print_scrape_options():
    """
    Print the available scrape options for the user.
    """
    print("Update records [0]")
    print("Google search [1]")
    print("Url search [2]")
    print("Exit [3]")


def main():
    print_options()
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
            print_scrape_options()
            ans = input("Enter your choice: ")
            while True:
                if ans == "0":
                    update_records()
                elif ans == "1":
                    google_search()
                elif ans == "2":
                    url_search()
                elif ans == "3":
                    break
                else:
                    print("Invalid choice. Please try again.")
                clear()
                print_scrape_options()
                ans = input("Enter your choice: ")
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")
        clear()

if __name__ == "__main__":
    main()
