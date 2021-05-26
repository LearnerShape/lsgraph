"""Add level mapping table

Revision ID: 416c03e7a685
Revises: 8a458c4ab29f
Create Date: 2021-05-24 14:09:02.194221

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "416c03e7a685"
down_revision = "8a458c4ab29f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "level",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cutoff", sa.Float(), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(
        op.f("ix_level_organization_id"), "level", ["organization_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_level_organization_id"), table_name="level")
    op.drop_table("level")
    # ### end Alembic commands ###
