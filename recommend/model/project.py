from recommend import db

class Project(db.Model):
    __tablename__ = 'project'
    projectid = db.Column(db.Integer, primary_key=True)
    projectname = db.Column(db.String(50))
    projectintroduce = db.Column(db.String(500))
    projecturl = db.Column(db.String(500))
    projectimg = db.Column(db.String(500))

    def __repr__(self):
        return '<Project %r>' % self.projectname