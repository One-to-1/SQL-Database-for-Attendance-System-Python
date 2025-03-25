class DatabaseConnection:
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = None

    def connect(self):
        # Logic to establish a database connection
        if self.connection is None:
            # Example: self.connection = some_database_library.connect(self.db_url)
            print(f"Connecting to database at {self.db_url}")
            self.connection = True  # Simulating a successful connection

    def disconnect(self):
        # Logic to close the database connection
        if self.connection is not None:
            # Example: self.connection.close()
            print("Disconnecting from database")
            self.connection = None

    def is_connected(self):
        return self.connection is not None