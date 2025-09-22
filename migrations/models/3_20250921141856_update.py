from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` DROP INDEX `phone_number`;
        ALTER TABLE `users` DROP COLUMN `phone_number`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `phone_number` VARCHAR(100) NOT NULL UNIQUE;
        ALTER TABLE `users` ADD UNIQUE INDEX `phone_number` (`phone_number`);"""
