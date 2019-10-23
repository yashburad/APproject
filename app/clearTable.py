import sqlite3

conn = sqlite3.connect('D:/YVJ/Documents/Ashoka University/Monsoon 2019/Advanced Programming - Anirban Mondal/MiniProject/git-sync/APproject/app/site.db')
c = conn.cursor()

c.execute("SELECT * FROM products")

print(c.fetchall())

c.execute("DELETE from products")
conn.commit()

c.execute("SELECT * FROM products")

print(c.fetchall())
