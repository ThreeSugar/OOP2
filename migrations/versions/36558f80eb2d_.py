"""empty message

Revision ID: 36558f80eb2d
Revises: c862d5c31804
Create Date: 2018-01-01 17:08:20.271830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36558f80eb2d'
down_revision = 'c862d5c31804'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fitness_lib',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('desc', sa.String(), nullable=True),
    sa.Column('vidlink', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'video_likes', type_='unique')
    op.create_table('sqlite_sequence',
    sa.Column('name', sa.NullType(), nullable=True),
    sa.Column('seq', sa.NullType(), nullable=True)
    )
    op.drop_table('fitness_lib')
    # ### end Alembic commands ###