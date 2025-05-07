from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    __tablename__='users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    # relacion con Profiles. el uselist=False es para forzar a que NO devuelva una lista
    profile: Mapped["Profiles"] = relationship(back_populates="user", uselist=False)
    
    
    #el serialize nos va a pasar de <Object at 0x5687321A5F> a {"id": 1, "email":"pepe@pepe.pe"} 

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            #como es un objeto que viene de la tabla Profiles, puedo realizar serialize o acceder a una de sus columnas
            "profile": self.profile.serialize()
            #"profile": self.profile.bio 
 
            # do not serialize the password, its a security breach
        }
#relacion de uno a uno entre users y profiles
class Profiles(db.Model):
    __tablename__='profiles'
    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[str] = mapped_column(String(250))
    # conexion a traves de la clave foranea (foreignkey)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # relacion con Users
    user: Mapped["Users"] = relationship(back_populates="profile")

    def serialize(self):
        return {
            "id": self.id,
            "bio": self.bio,
            "user_id": self.user_id   
        }
    
#relacion de uno a muchos entre profesores y cursos

class Teachers(db.Model):
    __tablename__='teachers'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    #relacion con courses, usa list[] porque va a recibir una coleccion de cursos (un profe - muchos cursos)
    courses: Mapped[list["Courses"]] = relationship(back_populates="teacher")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            #si recibimos una lista, tenemos que hacer un loop y serializar cada uno de los elementos dentro de la lista
            "courses": [course.serialize() for course in self.courses]
        }

class Courses(db.Model):
    __tablename__='courses'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    # conexion a traves de la clave foranea (foreignkey)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    # relacion con Teachers
    teacher: Mapped["Teachers"] = relationship(back_populates="courses")

    #relacion con students a partir de Enrollments
    enrollments: Mapped[list['Enrollments']] = relationship(back_populates='courses')


    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "teacher_id": self.teacher_id,
            #podemos acceder al name del teacher o podemos hacer el serialize()
            "teacher": self.teacher.name,
            "enrollments": [enrollment.serialize() for enrollment in self.enrollments]
        }
    

#relacion muchos a muchos entre courses y students MEDIANTE enrrollments

class Students(db.Model):
    __tablename__='students'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)

    enrollments: Mapped[list['Enrollments']] = relationship(back_populates='students')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            #enrollment (singular) es el objeto dentro de la lista de self.enrollments (plural)
            "enrollments": [enrollment.serialize() for enrollment in self.enrollments]
            
        }
    #las tablas de asociacion NO tiene id, pero TIENEN DOS o MAS PK
class Enrollments(db.Model):
    __tablename__='enrollments'

    date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now())

    #tabla de asociacion para relacion muchos a muchos lleva tantas PK como tablas este relacionando
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), primary_key=True)
    courses_id: Mapped[int] = mapped_column(ForeignKey('courses.id'), primary_key=True)
    students: Mapped['Students'] = relationship(back_populates='enrollments')
    courses: Mapped['Courses'] = relationship(back_populates='enrollments')

    def serialize(self):
        return {
            "student_id": self.student_id,
            "courses": self.courses_id,
            "date": self.date.isoformat()

        }