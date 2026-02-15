"""multi-tenant orgs + superadmin

Revision ID: 0002_multi_tenant
Revises: 0001_initial
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_multi_tenant"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "organizations" not in tables:
        op.create_table(
            "organizations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=180), nullable=False, unique=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )

    if "organization_subscriptions" not in tables:
        op.create_table(
            "organization_subscriptions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
            sa.Column("plan", sa.String(length=40), nullable=False),
            sa.Column("max_admins", sa.Integer(), nullable=False),
            sa.Column("starts_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        )

    user_cols = {c["name"] for c in inspector.get_columns("users")}
    if "organization_id" not in user_cols:
        with op.batch_alter_table("users") as batch_op:
            batch_op.add_column(sa.Column("organization_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key("fk_users_org", "organizations", ["organization_id"], ["id"])

    course_cols = {c["name"] for c in inspector.get_columns("courses")}
    if "organization_id" not in course_cols:
        with op.batch_alter_table("courses") as batch_op:
            batch_op.add_column(sa.Column("organization_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key("fk_courses_org", "organizations", ["organization_id"], ["id"])

    enrollment_cols = {c["name"] for c in inspector.get_columns("enrollments")}
    if "organization_id" not in enrollment_cols:
        with op.batch_alter_table("enrollments") as batch_op:
            batch_op.add_column(sa.Column("organization_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key("fk_enrollments_org", "organizations", ["organization_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("enrollments") as batch_op:
        batch_op.drop_constraint("fk_enrollments_org", type_="foreignkey")
        batch_op.drop_column("organization_id")

    with op.batch_alter_table("courses") as batch_op:
        batch_op.drop_constraint("fk_courses_org", type_="foreignkey")
        batch_op.drop_column("organization_id")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("fk_users_org", type_="foreignkey")
        batch_op.drop_column("organization_id")
    op.drop_table("organization_subscriptions")
    op.drop_table("organizations")
