"""add sentinel domain tables

Revision ID: 002_sentinel_domain_tables
Revises: 001_initial_schema
Create Date: 2026-10-05 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002_sentinel_domain_tables"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "biometric_telemetry",
        sa.Column("telemetry_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("encrypted_payload_hash", sa.String(), nullable=False),
        sa.Column("trust_score", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("verified", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("metadata_info", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("telemetry_id"),
    )
    op.create_index(op.f("ix_biometric_telemetry_agent_id"), "biometric_telemetry", ["agent_id"], unique=False)
    op.create_index(op.f("ix_biometric_telemetry_telemetry_id"), "biometric_telemetry", ["telemetry_id"], unique=False)

    op.create_table(
        "spatial_xr_anchors",
        sa.Column("anchor_id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("coordinate_vector", sa.JSON(), nullable=False),
        sa.Column("integrity_status", sa.String(), nullable=True, server_default="unverified"),
        sa.Column("verified", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("anchor_id"),
    )
    op.create_index(op.f("ix_spatial_xr_anchors_anchor_id"), "spatial_xr_anchors", ["anchor_id"], unique=False)
    op.create_index(op.f("ix_spatial_xr_anchors_session_id"), "spatial_xr_anchors", ["session_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_spatial_xr_anchors_session_id"), table_name="spatial_xr_anchors")
    op.drop_index(op.f("ix_spatial_xr_anchors_anchor_id"), table_name="spatial_xr_anchors")
    op.drop_table("spatial_xr_anchors")

    op.drop_index(op.f("ix_biometric_telemetry_telemetry_id"), table_name="biometric_telemetry")
    op.drop_index(op.f("ix_biometric_telemetry_agent_id"), table_name="biometric_telemetry")
    op.drop_table("biometric_telemetry")
