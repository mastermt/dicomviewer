from sqlalchemy import Column, Integer, String

from app.db.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    patient_code = Column(String(50), nullable=False, unique=True, index=True)
    birth_date = Column(String(20), nullable=True)
    phone = Column(String(30), nullable=True)


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    crm = Column(String(50), nullable=False, unique=True, index=True)
    specialty = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)

