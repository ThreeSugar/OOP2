"""empty message

Revision ID: f63bffdd5f98
Revises: f6c62ed2d385
Create Date: 2017-12-23 20:27:25.891368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f63bffdd5f98'
down_revision = 'f6c62ed2d385'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fitness_gen',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('genid', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('workout', sa.String(), nullable=True),
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
    op.drop_table('fitness_gen')
    # ### end Alembic commands ###
