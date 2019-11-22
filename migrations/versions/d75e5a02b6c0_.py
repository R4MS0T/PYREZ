"""empty message

Revision ID: d75e5a02b6c0
Revises: 
Create Date: 2019-11-21 21:41:36.065929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd75e5a02b6c0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('paladins_champ',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('champ_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('name_english', sa.String(length=50), nullable=True),
    sa.Column('free_rotation', sa.Boolean(), nullable=True),
    sa.Column('weekly_rotation', sa.Boolean(), nullable=True),
    sa.Column('health', sa.Integer(), nullable=True),
    sa.Column('is_latest', sa.Boolean(), nullable=True),
    sa.Column('patreon', sa.String(length=20), nullable=True),
    sa.Column('lore', sa.Text(), nullable=True),
    sa.Column('title', sa.String(length=20), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.Column('__lang__', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paladins_item',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('icon_id', sa.Integer(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('item_type', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('__lang__', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paladins_patch_note',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('author', sa.String(length=40), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('image_header', sa.Text(), nullable=True),
    sa.Column('image_thumb', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.String(length=40), nullable=True),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('lang', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paladins_platform',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=10), nullable=True),
    sa.Column('limited_access', sa.Boolean(), nullable=True),
    sa.Column('online', sa.Boolean(), nullable=True),
    sa.Column('version', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paladins_player',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('platform', sa.String(length=4), nullable=False),
    sa.Column('discord_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paladins_server',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('game', sa.String(length=20), nullable=True),
    sa.Column('version', sa.String(length=20), nullable=True),
    sa.Column('api_version', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paladins_skin',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_2', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('rarity', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('session',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('smite_patch_note',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('author', sa.String(length=40), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('image_header', sa.Text(), nullable=True),
    sa.Column('image_thumb', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.String(length=40), nullable=True),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('lang', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('smite_platform',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=10), nullable=True),
    sa.Column('limited_access', sa.Boolean(), nullable=True),
    sa.Column('online', sa.Boolean(), nullable=True),
    sa.Column('version', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('smite_player',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('platform', sa.String(length=4), nullable=False),
    sa.Column('discord_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('smite_server',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('game', sa.String(length=20), nullable=True),
    sa.Column('version', sa.String(length=20), nullable=True),
    sa.Column('api_version', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paladins_ability',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ability_id', sa.Integer(), nullable=True),
    sa.Column('ability', sa.Text(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('damage_type', sa.Integer(), nullable=True),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('cooldown', sa.Integer(), nullable=True),
    sa.Column('__lang__', sa.Integer(), nullable=True),
    sa.Column('champ_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['champ_id'], ['paladins_champ.champ_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paladins_card',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('icon_id', sa.Integer(), nullable=True),
    sa.Column('card_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('name_english', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('short_description', sa.Text(), nullable=True),
    sa.Column('activation_schedule', sa.Boolean(), nullable=True),
    sa.Column('lti', sa.Boolean(), nullable=True),
    sa.Column('cooldown', sa.Integer(), nullable=True),
    sa.Column('is_talent', sa.Boolean(), nullable=True),
    sa.Column('scale', sa.Float(), nullable=True),
    sa.Column('ability', sa.String(length=50), nullable=True),
    sa.Column('__lang__', sa.Integer(), nullable=True),
    sa.Column('champ_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['champ_id'], ['paladins_champ.champ_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('paladins_card')
    op.drop_table('paladins_ability')
    op.drop_table('smite_server')
    op.drop_table('smite_player')
    op.drop_table('smite_platform')
    op.drop_table('smite_patch_note')
    op.drop_table('session')
    op.drop_table('paladins_skin')
    op.drop_table('paladins_server')
    op.drop_table('paladins_player')
    op.drop_table('paladins_platform')
    op.drop_table('paladins_patch_note')
    op.drop_table('paladins_item')
    op.drop_table('paladins_champ')
    # ### end Alembic commands ###