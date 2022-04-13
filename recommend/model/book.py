from recommend import db

class Book(db.Model):
    __tablename__ = 'book'
    bookid = db.Column(db.Integer, primary_key=True)
    bookname = db.Column(db.String(100))
    bookauthor = db.Column(db.String(500))
    bookurl = db.Column(db.String(500))
    bookimg = db.Column(db.String(500))

    def __repr__(self):
        return '<Book %r>' % self.bookname