from db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("PRAGMA table_info(users)")
columns = cur.fetchall()

print("\nColumnas de la tabla users:\n")

for col in columns:
    print(col["name"])


print("\n\n---------Usuarios y estructura:  ---------")
cur.execute("PRAGMA table_info(users)")
columns = cur.fetchall()

print("\nEstructura tabla users:\n")

for col in columns:
    print(dict(col))

conn.close()