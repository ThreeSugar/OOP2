"""empty message

Revision ID: 6c7c67903c63
Revises: 116efdbc1667
Create Date: 2017-12-14 22:15:14.561582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c7c67903c63'
down_revision = '116efdbc1667'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipe_post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('time', sa.String(), nullable=True),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('difficulty', sa.String(), nullable=True),
    sa.Column('instruction', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('ingredients', sa.String(), nullable=True),
    sa.Column('nutri', sa.String(), nullable=True),
    sa.Column('date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
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
    op.drop_table('recipe_post')
    # ### end Alembic commands ###
