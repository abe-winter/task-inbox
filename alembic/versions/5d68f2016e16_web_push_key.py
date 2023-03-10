"""web push key

Revision ID: 5d68f2016e16
Revises: 29fb7a700944
Create Date: 2023-01-02 00:16:57.155532

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5d68f2016e16'
down_revision = '29fb7a700944'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('web_push_key',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('session_id', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('subscription_blob', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['ab_user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('session_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('web_push_key')
    # ### end Alembic commands ###
