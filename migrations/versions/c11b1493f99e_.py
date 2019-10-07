"""empty message

Revision ID: c11b1493f99e
Revises: b09a400ed2c6
Create Date: 2019-10-07 11:42:27.428438

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

revision = 'c11b1493f99e'
down_revision = 'b09a400ed2c6'
branch_labels = None
depends_on = None

from application.data.pdf_filenames import filenames


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column('compulsory_purchase_order', sa.Column('pdf_filename', sa.String(), nullable=True))

    for filename in filenames:
        key = '/'.join(filename.split('_')[:-1])
        update = f"UPDATE compulsory_purchase_order cpo SET pdf_filename='{filename}' WHERE cpo.compulsory_purchase_order='{key}'"
        op.execute(update)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('compulsory_purchase_order', 'pdf_filename')
    # ### end Alembic commands ###
