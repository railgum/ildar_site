import sqlite3


def add_content(idblock, short_title, img, altimg, title, contenttext, author, timestampdata):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO content (idblock, short_title, img, altimg, title, contenttext, author, timestampdata) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
              (idblock, short_title, img, altimg, title, contenttext, author, timestampdata))
    conn.commit()
    conn.close()


add_content('carouselExampleIndicators', 'Slider', 'https://via.placeholder.com/1024x500',
            'image 1', 'Title Test 1', 'some text for slider 1', None, None)

add_content('carouselExampleIndicators', 'Slider', 'https://via.placeholder.com/1024x500',
            'image 2', 'Title Test 2', 'some text for slider 2', None, None)

add_content('cards', 'miniCards', 'https://via.placeholder.com/150',
            'mini img 1', 'mini card 1', 'text for mini card 1', None, None)

add_content('cards', 'miniCards', 'https://via.placeholder.com/150',
            'mini img 2', 'mini card 2', 'text for mini card 2', None, None)
