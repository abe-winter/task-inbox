"""bytes to string pls

Revision ID: e4aaee4e1fd8
Revises: c316ae20eae5
Create Date: 2022-12-30 13:16:19.506277

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e4aaee4e1fd8'
down_revision = 'c316ae20eae5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('api_key', 'key')
    op.add_column('api_key', sa.Column('key', sa.String(), autoincrement=False, nullable=False))
    op.create_primary_key(None, 'api_key', ['key'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('api_key', 'key')
    op.add_column('api_key', sa.Column('key', postgresql.BYTEA(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
