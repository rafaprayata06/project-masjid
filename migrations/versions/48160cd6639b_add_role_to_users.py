from alembic import op
import sqlalchemy as sa


revision = '48160cd6639b'
down_revision = 'cb84c87d7587'
branch_labels = None
depends_on = None


def upgrade():
    # ✅ 1. Buat ENUM dulu di PostgreSQL
    op.execute("CREATE TYPE role_enum AS ENUM ('AS', 'AK', 'AH')")

    # ✅ 2. Baru tambahkan kolom
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('role', sa.Enum('AS', 'AK', 'AH', name='role_enum'), nullable=True)
        )


def downgrade():
    # ❌ 1. Hapus kolom dulu
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('role')

    # ❌ 2. Baru hapus ENUM
    op.execute("DROP TYPE role_enum")