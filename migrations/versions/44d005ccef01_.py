"""empty message

Revision ID: 44d005ccef01
Revises: 9a57a4580dab
Create Date: 2017-11-20 19:28:54.845786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44d005ccef01'
down_revision = '9a57a4580dab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('video_comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('videoid', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('comment', sa.String(length=3000), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('video_likes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('videoid', sa.Integer(), nullable=True),
    sa.Column('likes', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('videoid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sqlite_sequence',
    sa.Column('name', sa.NullType(), nullable=True),
    sa.Column('seq', sa.NullType(), nullable=True)
    )
    op.drop_table('video_likes')
    op.drop_table('video_comment')
    # ### end Alembic commands ###