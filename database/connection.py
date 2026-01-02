from PyQt6.QtSql import QSqlDatabase

CONNECTION_NAME = "inventory_connection"

def connect_db() -> bool:
    if QSqlDatabase.contains(CONNECTION_NAME):
        return True

    db = QSqlDatabase.addDatabase("QPSQL", CONNECTION_NAME)
    db.setHostName("localhost")
    db.setDatabaseName("inventory_production_db")
    db.setUserName("postgres")
    db.setPassword("root")

    return db.open()
