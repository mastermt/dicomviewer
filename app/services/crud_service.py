from sqlalchemy.exc import IntegrityError

from app.db.database import SessionLocal
from app.db.models import Doctor, Patient


class CRUDService:
    @staticmethod
    def list_patients(search_text="", page=1, page_size=10):
        with SessionLocal() as session:
            query = session.query(Patient)
            if search_text:
                like = f"%{search_text}%"
                query = query.filter(
                    (Patient.full_name.ilike(like)) | (Patient.patient_code.ilike(like))
                )
            total = query.count()
            items = (
                query.order_by(Patient.id.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
            return items, total

    @staticmethod
    def create_patient(data):
        with SessionLocal() as session:
            patient = Patient(**data)
            session.add(patient)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError("duplicate")

    @staticmethod
    def update_patient(patient_id, data):
        with SessionLocal() as session:
            patient = session.get(Patient, patient_id)
            if patient is None:
                raise ValueError("not_found")
            for key, value in data.items():
                setattr(patient, key, value)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError("duplicate")

    @staticmethod
    def delete_patient(patient_id):
        with SessionLocal() as session:
            patient = session.get(Patient, patient_id)
            if patient is None:
                raise ValueError("not_found")
            session.delete(patient)
            session.commit()

    @staticmethod
    def list_doctors(search_text="", page=1, page_size=10):
        with SessionLocal() as session:
            query = session.query(Doctor)
            if search_text:
                like = f"%{search_text}%"
                query = query.filter((Doctor.full_name.ilike(like)) | (Doctor.crm.ilike(like)))
            total = query.count()
            items = (
                query.order_by(Doctor.id.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
            return items, total

    @staticmethod
    def create_doctor(data):
        with SessionLocal() as session:
            doctor = Doctor(**data)
            session.add(doctor)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError("duplicate")

    @staticmethod
    def update_doctor(doctor_id, data):
        with SessionLocal() as session:
            doctor = session.get(Doctor, doctor_id)
            if doctor is None:
                raise ValueError("not_found")
            for key, value in data.items():
                setattr(doctor, key, value)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError("duplicate")

    @staticmethod
    def delete_doctor(doctor_id):
        with SessionLocal() as session:
            doctor = session.get(Doctor, doctor_id)
            if doctor is None:
                raise ValueError("not_found")
            session.delete(doctor)
            session.commit()

