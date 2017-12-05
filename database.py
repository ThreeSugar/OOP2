import sqlite3

#Open database
conn = sqlite3.connect('database.db')

#Create table
conn.execute('''CREATE TABLE Item 
		(id INTEGER PRIMARY KEY, 
		name TEXT,
		info TEXT,
		price TEXT,
		description TEXT,
		calories TEXT,
		category TEXT
		)''')

conn.execute('''CREATE TABLE Cart
		(id INTEGER PRIMARY KEY,
		item_id INTEGER,
		quantity INTEGER,
		FOREIGN KEY(item_id) REFERENCES Item(id)
		)''')



conn.close()

