"""org AI features and user credits

Revision ID: 0003_ai_features
Revises: 0002_multi_tenant
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_ai_features"
down_revision = "0002_multi_tenant"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    org_cols = {c["name"] for c in inspector.get_columns("organizations")}
    with op.batch_alter_table("organizations") as batch_op:
        if "genre" not in org_cols:
            batch_op.add_column(sa.Column("genre", sa.String(length=60), nullable=True))
        if "ai_drawing_enabled" not in org_cols:
            batch_op.add_column(sa.Column("ai_drawing_enabled", sa.Boolean(), server_default=sa.false(), nullable=False))
        if "ai_coding_enabled" not in org_cols:
            batch_op.add_column(sa.Column("ai_coding_enabled", sa.Boolean(), server_default=sa.false(), nullable=False))
        if "ai_general_enabled" not in org_cols:
            batch_op.add_column(sa.Column("ai_general_enabled", sa.Boolean(), server_default=sa.true(), nullable=False))

    tables = inspector.get_table_names()
    if "user_credits" not in tables:
        op.create_table(
            "user_credits",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
            sa.Column("balance", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )

    if "credit_ledger" not in tables:
        op.create_table(
            "credit_ledger",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("amount", sa.Integer(), nullable=False),
            sa.Column("reason", sa.String(length=120), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )


def downgrade() -> None:
    op.drop_table("credit_ledger")
    op.drop_table("user_credits")
    with op.batch_alter_table("organizations") as batch_op:
        if "ai_general_enabled" in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("organizations")}:
            batch_op.drop_column("ai_general_enabled")
        if "ai_coding_enabled" in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("organizations")}:
            batch_op.drop_column("ai_coding_enabled")
        if "ai_drawing_enabled" in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("organizations")}:
            batch_op.drop_column("ai_drawing_enabled")
        if "genre" in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("organizations")}:
            batch_op.drop_column("genre")
