import sqlite3
import pandas as pd
import os

# Directory containing CSV files
csv_directory = './data'

# Function to get list of CSV files
def get_csv_files(directory):
    csv_files = []
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            csv_files.append(file)
    print(csv_files,"12")
    return csv_files

# Function to create tables from CSV files
def create_tables(connection, csv_files):
    cursor = connection.cursor()
    for csv_file in csv_files:
        try:
            table_name = os.path.splitext(csv_file)[0]
            print("line 21 /////",table_name)
            df = pd.read_csv(os.path.join(csv_directory, csv_file))
            df.to_sql(table_name, connection, index=False)
            print(f"Table '{table_name}' created with {len(df)} rows.")
        except Exception as e:
            print("Error:",str(e))

# Main function
def main():
    # Connect to SQLite database
    conn = sqlite3.connect('perov21.db')

    # Get list of CSV files
    csv_files = get_csv_files(csv_directory)

    # Create tables from CSV files
    create_tables(conn, csv_files)

    # Close connection
    conn.close()

if __name__ == "__main__":
    main()

