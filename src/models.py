from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "last_name": self.last_name
            
            # do not serialize the password, its a security breach
        }
class Planets(db.Model):
    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(120), nullable=False)
    population:Mapped[str] = mapped_column(String(120), nullable=False)
    gravity:Mapped[str] = mapped_column(String(20), nullable=False)
    image: Mapped[str] = mapped_column(String(120), nullable=False)

class People(db.Model):
    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(120), nullable=False)
    height:Mapped[str] = mapped_column(String(120), nullable=False)
    mass:Mapped[str] = mapped_column(String(120), nullable=False)
    hair_color:Mapped[str] = mapped_column(String(120), nullable=False)

class Favorites_Planets(db.Model):
    id:Mapped[int] = mapped_column(primary_key=True)
    user_id:Mapped[int] = mapped_column(db.ForeignKey('user.id'), nullable=False)
    planet_id:Mapped[int] = mapped_column(db.ForeignKey('planets.id'), nullable=False)

class Favorites_People(db.Model):
    id:Mapped[int] = mapped_column(primary_key=True)
    user_id:Mapped[int] = mapped_column(db.ForeignKey('user.id'), nullable=False)
    people_id:Mapped[int] = mapped_column(db.ForeignKey('people.id'), nullable=False)

