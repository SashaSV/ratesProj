"""empty message

Revision ID: 4aae72adbfd9
Revises: 
Create Date: 2023-01-24 16:54:31.061179

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4aae72adbfd9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('currancy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=3), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('country', sa.String(length=50), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('currancy_rates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_curr', sa.Integer(), nullable=False),
    sa.Column('rate', sa.DECIMAL(precision=15, scale=4), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['id_curr'], ['currancy.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('currancy_rates')
    op.drop_table('currancy')
    # ### end Alembic commands ###
