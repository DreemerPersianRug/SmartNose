import sqlite3
from . import auxiliary_modules as am

class DataBase:
    def __init__(self, logger, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.__logger = logger

    def open(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            self.__logger.error(f"Error opening database: {e}")

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error as e:
                self.__logger.error(f"Error closing database: {e}")
            finally:
                self.conn = None
                self.cursor = None

    def create_table(self, table_name, num_sensor_fields):
        """
        Creates a default table with a 'timestamp' field and the specified number of sensor fields.
        """
        try:
            fields = ', '.join([f'sensor_{i} REAL' for i in range(num_sensor_fields)])
            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                {fields}
            )
            """
            self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            self.__logger.error(f"Error creating table: {e}")

    def write_data(self, table_name, sensor_values):
        """
        Writes data to the specified table.
        sensor_values should be a list of numerical values corresponding to the sensor fields.
        """
        try:
            timestamp = am.timestamp()
            placeholders = ', '.join(['?'] * (len(sensor_values) + 1))
            query = f"""
            INSERT INTO {table_name} (timestamp, {', '.join([f'sensor_{i}' for i in range(len(sensor_values))])})
            VALUES ({placeholders})
            """
            self.cursor.execute(query, [timestamp] + sensor_values)
            self.conn.commit()
        except sqlite3.Error as e:
            self.__logger.error(f"Error writing data: {e}")

    def read_data(self, table_name):
        """
        Reads data from the specified table.
        """
        try:
            query = f"SELECT * FROM {table_name}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self.__logger.error(f"Error reading data: {e}")
            return []

    def delete_data(self, table_name, record_id):
        """
        Deletes data from the specified table by record ID.
        """
        try:
            query = f"DELETE FROM {table_name} WHERE id = ?"
            self.cursor.execute(query, (record_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.__logger.error(f"Error deleting data: {e}")

    def ensure_database(self):
        if not am.check_file_in_folder(self.db_name):
            self.__logger.warning(f'Database file not found {self.db_name}. It will be created.')
            self.open()
            self.close()

# Example usage
#if __name__ == "__main__":
#    db = DataBase()
#    db.open()

#    try:
#        db.create_table('test_table', 3)
#        db.write_data('test_table', [1.1, 2.2, 3.3])
#        data = db.read_data('test_table')
#        print(data)
#        db.delete_data('test_table', 1)
#    finally:
#        db.close()
