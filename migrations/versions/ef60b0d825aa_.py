"""empty message

Revision ID: ef60b0d825aa
Revises: None
Create Date: 2019-06-16 22:17:41.694706

"""

# revision identifiers, used by Alembic.
revision = 'ef60b0d825aa'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card', sa.String(), nullable=True),
    sa.Column('flags', sa.Integer(), nullable=True),
    sa.Column('tz', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('controllers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serial', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('fw', sa.String(), nullable=True),
    sa.Column('conn_fw', sa.String(), nullable=True),
    sa.Column('active', sa.Integer(), nullable=True),
    sa.Column('mode', sa.Integer(), nullable=True),
    sa.Column('last_conn', sa.Integer(), nullable=True),
    sa.Column('license', sa.String(), nullable=True),
    sa.Column('interval', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.Integer(), nullable=False),
    sa.Column('event', sa.Integer(), nullable=False),
    sa.Column('card', sa.Text(), nullable=False),
    sa.Column('flags', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serial', sa.Integer(), nullable=True),
    sa.Column('type', sa.Text(), nullable=True),
    sa.Column('json', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tasks')
    op.drop_table('events')
    op.drop_table('controllers')
    op.drop_table('cards')
    # ### end Alembic commands ###
