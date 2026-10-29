"""devices, telemetry_events, audit_events

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision = "0001"
down_revision = None
JSON_T = sa.JSON().with_variant(JSONB(), "postgresql")
TS = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("device_id", sa.String(64), nullable=False),
        sa.Column("api_key_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", TS, nullable=False),
        sa.Column("updated_at", TS, nullable=False),
    )
    op.create_index("ix_devices_device_id", "devices", ["device_id"], unique=True)
    op.create_table(
        "telemetry_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(36), nullable=False, unique=True),
        sa.Column("device_pk", sa.String(36), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("sequence", sa.Integer, nullable=False),
        sa.Column("captured_at", TS, nullable=False),
        sa.Column("received_at", TS, nullable=False),
        sa.Column("schema_version", sa.Integer, nullable=False),
        sa.Column("firmware_version", sa.String(32), nullable=False),
        sa.Column("calibration_version", sa.Integer, nullable=False),
        sa.Column("clock_synchronized", sa.Boolean, nullable=False),
        sa.Column("volume_total_liters", sa.Numeric(14, 3), nullable=False),
        sa.Column("flow_liters_per_minute", sa.Numeric(10, 3), nullable=False),
        sa.Column("sensor_status", sa.String(16), nullable=False),
        sa.Column("measurement_kind", sa.String(16), nullable=False),
        sa.Column("payload", JSON_T, nullable=False),
        sa.UniqueConstraint("device_pk", "sequence", name="uq_telemetry_device_sequence"),
        sa.CheckConstraint("volume_total_liters >= 0", name="ck_volume_non_negative"),
    )
    op.create_index(
        "ix_telemetry_device_captured", "telemetry_events", ["device_pk", "captured_at"]
    )
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", TS, nullable=False),
        sa.Column("actor", sa.String(80), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource", sa.String(80), nullable=False),
        sa.Column("result", sa.String(16), nullable=False),
        sa.Column("context", JSON_T, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("telemetry_events")
    op.drop_table("devices")
