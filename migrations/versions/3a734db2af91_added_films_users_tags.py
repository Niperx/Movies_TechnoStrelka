"""added Films, Users, Tags

Revision ID: 3a734db2af91
Revises: 
Create Date: 2025-02-23 21:58:06.398189

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a734db2af91'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('film',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('film_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('shortDescription', sa.String(length=300), nullable=True),
    sa.Column('poster_Url', sa.String(length=300), nullable=True),
    sa.Column('poster_Url_preview', sa.String(length=300), nullable=True),
    sa.Column('cover_Url', sa.String(length=300), nullable=True),
    sa.Column('wed_Url', sa.String(length=300), nullable=True),
    sa.Column('genres', sa.String(length=300), nullable=True),
    sa.Column('countries', sa.String(length=300), nullable=True),
    sa.Column('ai_plot', sa.String(length=1000), nullable=True),
    sa.Column('ai_characters', sa.String(length=1000), nullable=True),
    sa.Column('ai_moment', sa.String(length=1000), nullable=True),
    sa.Column('ai_idea', sa.String(length=1000), nullable=True),
    sa.Column('ai_impress', sa.String(length=1000), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('film_id')
    )
    with op.batch_alter_table('film', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_film_title'), ['title'], unique=False)

    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_tag_name'), ['name'], unique=True)

    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('film_tag',
    sa.Column('film_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['film_id'], ['film.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('film_id', 'tag_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('film_tag')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_tag_name'))

    op.drop_table('tag')
    with op.batch_alter_table('film', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_film_title'))

    op.drop_table('film')
    # ### end Alembic commands ###
