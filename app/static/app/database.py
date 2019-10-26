import sqlite3

#Open database
conn = sqlite3.connect('/Users/raj.burad7/Documents/APproject1/project/app/site.db')

#Create table
c=conn.cursor()


conn.execute('''CREATE TABLE cart
		(userId INTEGER,
		productId INTEGER,
		FOREIGN KEY(userId) REFERENCES user(id),
		FOREIGN KEY(productId) REFERENCES products(productId)
		)''')

conn.execute('''CREATE TABLE categories
		(categoryId INTEGER PRIMARY KEY,
		name TEXT
		)''')

conn.execute('''CREATE TABLE orders
                (orderId INTEGER PRIMARY KEY,
                userId INTEGER,
                productId INTEGER,
                price INTEGER,
                quantity INTEGER,
                total INTEGER,
                FOREIGN KEY(productId) REFERENCES products(productId),
                FOREIGN KEY(userId) REFERENCES user(id)
                )''')
                
                

conn.close()


