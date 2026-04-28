"""initial tables

Revision ID: 20260428_01
Revises:
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260428_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("patient_code", sa.String(length=50), nullable=False),
        sa.Column("birth_date", sa.String(length=20), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
    )
    op.create_index("ix_patients_id", "patients", ["id"])
    op.create_index("ix_patients_patient_code", "patients", ["patient_code"], unique=True)

    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("crm", sa.String(length=50), nullable=False),
        sa.Column("specialty", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
    )
    op.create_index("ix_doctors_id", "doctors", ["id"])
    op.create_index("ix_doctors_crm", "doctors", ["crm"], unique=True)


def downgrade():
    op.drop_index("ix_doctors_crm", table_name="doctors")
    op.drop_index("ix_doctors_id", table_name="doctors")
    op.drop_table("doctors")
    op.drop_index("ix_patients_patient_code", table_name="patients")
    op.drop_index("ix_patients_id", table_name="patients")
    op.drop_table("patients")

