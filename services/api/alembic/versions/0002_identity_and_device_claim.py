"""users, organizations, memberships, properties; device claim columns

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001"
TS = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(200), nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_table(
        "memberships",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.UniqueConstraint("user_id", "org_id", name="uq_membership_user_org"),
    )
    op.create_table(
        "properties",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_properties_org_id", "properties", ["org_id"])
    with op.batch_alter_table("devices") as b:
        b.add_column(sa.Column("property_id", sa.String(36), nullable=True))
        b.add_column(sa.Column("activation_code_hash", sa.String(64), nullable=True))
        b.add_column(sa.Column("claimed_at", TS, nullable=True))
        b.create_foreign_key("fk_devices_property", "properties", ["property_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("devices") as b:
        b.drop_constraint("fk_devices_property", type_="foreignkey")
        b.drop_column("claimed_at")
        b.drop_column("activation_code_hash")
        b.drop_column("property_id")
    op.drop_index("ix_properties_org_id", "properties")
    op.drop_table("properties")
    op.drop_table("memberships")
    op.drop_table("organizations")
    op.drop_index("ix_users_email", "users")
    op.drop_table("users")
