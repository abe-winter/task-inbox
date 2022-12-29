"""initial

Revision ID: b084e91fa2a0
Revises: 
Create Date: 2022-12-28 23:03:59.978660

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b084e91fa2a0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task_schema',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('api_key',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('key', postgresql.BYTEA(), nullable=False),
    sa.Column('tschema_id', postgresql.UUID(), nullable=True),
    sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['tschema_id'], ['task_schema.id'], ),
    sa.PrimaryKeyConstraint('id', 'key')
    )
    op.create_table('schema_version',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('tschema_id', postgresql.UUID(), nullable=True),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('semver', sa.String(), nullable=True),
    sa.Column('default_hook_url', sa.String(), nullable=True),
    sa.Column('hook_auth', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['tschema_id'], ['task_schema.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('webhook_key',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('tschema_id', postgresql.UUID(), nullable=True),
    sa.Column('key', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['tschema_id'], ['task_schema.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task_type',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('version_id', postgresql.UUID(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('pending_states', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('resolved_states', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['version_id'], ['schema_version.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('ttype_id', postgresql.UUID(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('resolved', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['ttype_id'], ['task_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task_history',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('task_id', postgresql.UUID(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('resolved', sa.Boolean(), nullable=True),
    sa.Column('update_meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_history')
    op.drop_table('task')
    op.drop_table('task_type')
    op.drop_table('webhook_key')
    op.drop_table('schema_version')
    op.drop_table('api_key')
    op.drop_table('task_schema')
    # ### end Alembic commands ###