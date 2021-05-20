"""empty message

Revision ID: 5cdac957440d
Revises: 
Create Date: 2021-05-20 12:16:56.905359

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5cdac957440d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('collection',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.Column('public', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('customer',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.Text(), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('password_hash', sa.Binary(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_customer_email'), 'customer', ['email'], unique=True)
    op.create_table('format',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('logo', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('group',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('platform',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('logo', sa.Text(), nullable=True),
    sa.Column('url', sa.Text(), nullable=True),
    sa.Column('subscription', sa.Numeric(), nullable=True),
    sa.Column('free_trial', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('profile',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('profile_skill',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('provider',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('logo', sa.Text(), nullable=True),
    sa.Column('url', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('quality_attribute',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('min', sa.Float(), nullable=True),
    sa.Column('max', sa.Float(), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.Text(), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('access_key',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('access_key', sa.String(length=128), nullable=True),
    sa.Column('secret_key', sa.String(length=128), nullable=True),
    sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_used', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('collection_member',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('collection_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('edit', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['collection_id'], ['collection.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('group_member',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('organization',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('quality_value',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('quality_attribute_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('value', sa.Float(), nullable=True),
    sa.Column('date_checked', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['quality_attribute_id'], ['provider.id'], ),
    sa.ForeignKeyConstraint(['resource_id'], ['provider.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('resource',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('short_description', sa.Text(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('url', sa.Text(), nullable=True),
    sa.Column('provider_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('platform_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('platform_level', sa.String(length=64), nullable=True),
    sa.Column('alt_id', sa.Text(), nullable=True),
    sa.Column('syllabus', sa.Text(), nullable=True),
    sa.Column('learning_outcomes', sa.Text(), nullable=True),
    sa.Column('prerequisite_knowledge', sa.Text(), nullable=True),
    sa.Column('retired', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['platform_id'], ['platform.id'], ),
    sa.ForeignKeyConstraint(['provider_id'], ['provider.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('skill',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('personal', sa.Boolean(), nullable=True),
    sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('collection_resource',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('collection_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['collection_id'], ['collection.id'], ),
    sa.ForeignKeyConstraint(['resource_id'], ['resource.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('offering',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('format_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('pace_min_hrs_per_week', sa.Float(), nullable=True),
    sa.Column('pace_max_hrs_per_week', sa.Float(), nullable=True),
    sa.Column('pace_num_weeks', sa.Integer(), nullable=True),
    sa.Column('elapsed_duration', sa.Float(), nullable=True),
    sa.Column('min_taught_duration', sa.Float(), nullable=True),
    sa.Column('max_taught_duration', sa.Float(), nullable=True),
    sa.Column('language', sa.String(length=128), nullable=True),
    sa.Column('cc_language', sa.String(length=128), nullable=True),
    sa.Column('free', sa.Boolean(), nullable=True),
    sa.Column('free_audit', sa.Boolean(), nullable=True),
    sa.Column('paid', sa.Boolean(), nullable=True),
    sa.Column('certificate', sa.Boolean(), nullable=True),
    sa.Column('quality', sa.Float(), nullable=True),
    sa.Column('instructors', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['format_id'], ['format.id'], ),
    sa.ForeignKeyConstraint(['resource_id'], ['resource.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('skill_include',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('child_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['child_id'], ['skill.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['skill.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('price',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('offering_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('date_checked', sa.DateTime(), nullable=True),
    sa.Column('price', sa.Numeric(), nullable=True),
    sa.Column('discount', sa.Numeric(), nullable=True),
    sa.Column('restrictions', sa.Text(), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.ForeignKeyConstraint(['offering_id'], ['offering.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('price')
    op.drop_table('skill_include')
    op.drop_table('offering')
    op.drop_table('collection_resource')
    op.drop_table('skill')
    op.drop_table('resource')
    op.drop_table('quality_value')
    op.drop_table('organization')
    op.drop_table('group_member')
    op.drop_table('collection_member')
    op.drop_table('access_key')
    op.drop_table('user')
    op.drop_table('quality_attribute')
    op.drop_table('provider')
    op.drop_table('profile_skill')
    op.drop_table('profile')
    op.drop_table('platform')
    op.drop_table('group')
    op.drop_table('format')
    op.drop_index(op.f('ix_customer_email'), table_name='customer')
    op.drop_table('customer')
    op.drop_table('collection')
    # ### end Alembic commands ###
