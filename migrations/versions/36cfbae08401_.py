"""empty message

Revision ID: 36cfbae08401
Revises: b317d84860c9
Create Date: 2018-01-27 20:37:03.190720

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36cfbae08401'
down_revision = 'b317d84860c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('playlist_session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('playlist_id', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('playlist_vid_id', sa.Integer(), nullable=True),
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
    op.drop_table('playlist_session')
    # ### end Alembic commands ###
