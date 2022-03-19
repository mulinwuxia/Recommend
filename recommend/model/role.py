from recommend import db, user_role

class Role(db.Model):
    __tablename__ = 'role'
    roleid = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(50))
    roledescription = db.Column(db.String(50))
    users = db.relationship("User", secondary=user_role, backref='_roles')

    def __repr__(self):
        return '<Role %r>' % self.rolename