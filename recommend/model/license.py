from recommend import db

class License(db.Model):
    __tablename__ = 'license'
    licenseid = db.Column(db.Integer, primary_key=True)
    licensename = db.Column(db.String(500))
    licenseurl = db.Column(db.String(500))

    def __repr__(self):
        return '<License %r>' % self.licensename