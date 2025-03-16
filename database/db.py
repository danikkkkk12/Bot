import aiosqlite

class DB:
    DEFAULT_VERIFIED = "0"
    VERIFIED_STATUS = "verifed"

    def __init__(self):
        self.con = None  # Инициализируем атрибут con

    async def ensure_connection(self):
        """Убедимся, что соединение с базой данных установлено."""
        if self.con is None:
            self.con = await aiosqlite.connect("database/user.db")
            await self.con.execute("PRAGMA journal_mode=WAL")  # Оптимизация для многопоточности

    async def on_startup(self):
        """Инициализация базы данных при запуске."""
        await self.ensure_connection()
        await self.con.execute(
            "CREATE TABLE IF NOT EXISTS users(verifed TEXT, user_id BIGINT PRIMARY KEY, lang TEXT)"
        )
        await self.con.execute("CREATE TABLE IF NOT EXISTS desc(ref TEXT)")
        await self.con.commit()

    async def on_shutdown(self):
        """Закрытие соединения с базой данных при завершении работы."""
        if self.con:
            await self.con.close()

    async def get_ref(self) -> str:
        await self.ensure_connection()
        query = 'SELECT * FROM desc'
        result = await self.con.execute(query)
        row = await result.fetchone()
        if row is not None:
            return row[0]
        return None

    async def edit_ref(self, url: str) -> None:
        await self.ensure_connection()
        async with self.con.execute("UPDATE desc SET ref = ? WHERE ref = ?", (url, await self.get_ref())):
            await self.con.commit()

    async def get_users_count(self) -> int:
        await self.ensure_connection()
        query = "SELECT COUNT(*) FROM users"
        result = await self.con.execute(query)
        return (await result.fetchone())[0]

    async def get_verified_users_count(self) -> int:
        await self.ensure_connection()
        query = "SELECT COUNT(*) FROM users WHERE verifed = ?"
        result = await self.con.execute(query, (self.VERIFIED_STATUS,))
        return (await result.fetchone())[0]

    async def register(self, user_id, language: str, verifed=DEFAULT_VERIFIED):
        await self.ensure_connection()
        try:
            query = "INSERT INTO users(verifed, user_id, lang) VALUES(?, ?, ?)"
            await self.con.execute(query, (verifed, user_id, language))
            await self.con.commit()
        except aiosqlite.IntegrityError as e:
            print(f"Ошибка при регистрации пользователя {user_id}: {e}")

    async def update_verifed(self, user_id, verifed=VERIFIED_STATUS):
        await self.ensure_connection()
        query = "UPDATE users SET verifed = ? WHERE user_id = ?"
        await self.con.execute(query, (verifed, user_id))
        await self.con.commit()

    async def get_user(self, user_id):
        await self.ensure_connection()
        query = 'SELECT * FROM users WHERE user_id = ? AND verifed = ?'
        result = await self.con.execute(query, (user_id, self.VERIFIED_STATUS))
        return await result.fetchone()

    async def get_user_info(self, user_id):
        await self.ensure_connection()
        query = 'SELECT * FROM users WHERE user_id = ?'
        result = await self.con.execute(query, (user_id,))
        return await result.fetchone()

    async def get_users(self):
        await self.ensure_connection()
        query = "SELECT * FROM users"
        result = await self.con.execute(query)
        return await result.fetchall()

    async def update_lang(self, user_id, language: str):
        await self.ensure_connection()
        query = "UPDATE users SET lang = ? WHERE user_id = ?"
        await self.con.execute(query, (language, user_id))
        await self.con.commit()

    async def get_lang(self, user_id):
        await self.ensure_connection()
        query = "SELECT lang FROM users WHERE user_id = ?"
        result = await self.con.execute(query, (user_id,))
        row = await result.fetchone()
        if row is not None:
            return row[0]
        else:
            return "en"  # Значение по умолчанию

DataBase = DB()