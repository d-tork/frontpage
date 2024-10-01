/* Create the table for storing the catalog */
CREATE TABLE IF NOT EXISTS gutensearch.catalog (
	id BIGINT PRIMARY KEY
	,issued DATE NOT NULL
	,title VARCHAR(1000)  -- TODO ensure a title never exceeds this when inputting
	,language VARCHAR(20)
	,authors VARCHAR(2700)
	,subjects VARCHAR(1000)
	,locc VARCHAR(25) COMMENT 'Library of Congress classification'
	,bookshelves VARCHAR(300)
	)
;


/* Create the table for storing word frequencies */
CREATE TABLE IF NOT EXISTS gutensearch.freqs (
	word VARCHAR(50) PRIMARY KEY  -- longest word in English is 45 letters
	/* additional columns will be added for each book id requested */
	)
;

