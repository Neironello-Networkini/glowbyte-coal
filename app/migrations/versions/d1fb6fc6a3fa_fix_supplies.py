"""fix supplies

Revision ID: d1fb6fc6a3fa
Revises: c0d384c2738c
Create Date: 2025-05-04 18:16:39.671398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1fb6fc6a3fa'
down_revision: Union[str, None] = 'c0d384c2738c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('supplies', sa.Column('stack_id', sa.Integer(), nullable=True))
    op.drop_constraint('supplies_warehouse_id_fkey', 'supplies', type_='foreignkey')
    op.create_foreign_key(None, 'supplies', 'stack', ['stack_id'], ['id'])
    op.drop_column('supplies', 'warehouse_id')
    op.drop_column('supplies', 'stack_number')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('supplies', sa.Column('stack_number', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('supplies', sa.Column('warehouse_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'supplies', type_='foreignkey')
    op.create_foreign_key('supplies_warehouse_id_fkey', 'supplies', 'warehouse', ['warehouse_id'], ['id'])
    op.drop_column('supplies', 'stack_id')
    # ### end Alembic commands ###
