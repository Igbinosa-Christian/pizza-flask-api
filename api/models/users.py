from ..utils import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.Text(45), nullable=False)
    is_staff = db.Column(db.Boolean(), default=False)
    is_active = db.Column(db.Boolean(), default=False)
    orders = db.relationship('Order', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


    # Function to add user
    def save(self):
        db.session.add(self)
        db.session.commit()


    
    # Function to get by id or return 404 error
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

