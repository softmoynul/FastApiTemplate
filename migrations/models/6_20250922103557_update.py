from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` RENAME TO `users`;
        ALTER TABLE `users` ADD `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);
        ALTER TABLE `users` ADD `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
        ALTER TABLE `users` ADD `is_active` BOOL NOT NULL DEFAULT 1;
        ALTER TABLE `users` ADD `is_staff` BOOL NOT NULL DEFAULT 0;
        ALTER TABLE `users` ADD `is_superuser` BOOL NOT NULL DEFAULT 0;
        ALTER TABLE `users` DROP COLUMN `phone_number`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` RENAME TO `user`;
        ALTER TABLE `users` ADD `phone_number` VARCHAR(20);
        ALTER TABLE `users` DROP COLUMN `created_at`;
        ALTER TABLE `users` DROP COLUMN `updated_at`;
        ALTER TABLE `users` DROP COLUMN `is_active`;
        ALTER TABLE `users` DROP COLUMN `is_staff`;
        ALTER TABLE `users` DROP COLUMN `is_superuser`;"""
