from database import Database

if __name__ == "__main__":
    db = Database()
    print("База данных успешно инициализирована!")
    db.close()