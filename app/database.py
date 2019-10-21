import sqlite3

#Open database
conn = sqlite3.connect('/Users/raj.burad7/Desktop/APproject/project/app/site.db')

#Create table
c=conn.cursor()

conn.execute("ALTER TABLE user ADD type TEXT ")
# conn.execute('''CREATE TABLE products
# 		(productId INTEGER PRIMARY KEY,
# 		name TEXT,
# 		price REAL,
# 		image TEXT,
# 		categoryId INTEGER,
# 		FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
# 		)''')

# conn.execute('''CREATE TABLE wishlist
# 		(userId INTEGER,
# 		productId INTEGER
# 		)''')


                
                

conn.close()


