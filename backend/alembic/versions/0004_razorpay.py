"""payments, course price, user active

Revision ID: 0004_razorpay
Revises: 0003_ai_features
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_razorpay"
down_revision = "0003_ai_features"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    user_cols = {c["name"] for c in inspector.get_columns("users")}
    with op.batch_alter_table("users") as batch_op:
        if "is_active" not in user_cols:
            batch_op.add_column(sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False))

    course_cols = {c["name"] for c in inspector.get_columns("courses")}
    with op.batch_alter_table("courses") as batch_op:
        if "price_inr" not in course_cols:
            batch_op.add_column(sa.Column("price_inr", sa.Integer(), server_default="0", nullable=False))

    tables = inspector.get_table_names()
    if "payments" not in tables:
        op.create_table(
            "payments",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
            sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True),
            sa.Column("enrollment_id", sa.Integer(), sa.ForeignKey("enrollments.id", ondelete="SET NULL"), nullable=True),
            sa.Column("purpose", sa.String(length=40), nullable=False),
            sa.Column("amount_inr", sa.Integer(), nullable=False),
            sa.Column("commission_inr", sa.Integer(), server_default="0", nullable=False),
            sa.Column("currency", sa.String(length=10), server_default="INR", nullable=False),
            sa.Column("status", sa.String(length=20), server_default="created", nullable=False),
            sa.Column("razorpay_order_id", sa.String(length=120), nullable=True),
            sa.Column("razorpay_payment_id", sa.String(length=120), nullable=True),
            sa.Column("razorpay_signature", sa.String(length=255), nullable=True),
            sa.Column("razorpay_payment_link_id", sa.String(length=120), nullable=True),
            sa.Column("razorpay_payment_link_url", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )


def downgrade() -> None:
    op.drop_table("payments")
    with op.batch_alter_table("courses") as batch_op:
        if "price_inr" in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("courses")}:
            batch_op.drop_column("price_inr")
    with op.batch_alter_table("users") as batch_op:
        if "is_active" in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("users")}:
            batch_op.drop_column("is_active")
