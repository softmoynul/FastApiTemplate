from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `group` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL UNIQUE
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `item` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL DEFAULT 'Name'
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `permission` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `codename` VARCHAR(100) NOT NULL UNIQUE
) CHARACTER SET utf8mb4;
        CREATE TABLE `group_permissions` (
    `group_id` INT NOT NULL REFERENCES `group` (`id`) ON DELETE CASCADE,
    `permission_id` INT NOT NULL REFERENCES `permission` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        CREATE TABLE `user_groups` (
    `users_id` INT NOT NULL REFERENCES `users` (`id`) ON DELETE CASCADE,
    `group_id` INT NOT NULL REFERENCES `group` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `user_permissions`;
        DROP TABLE IF EXISTS `item`;
        DROP TABLE IF EXISTS `permission`;
        DROP TABLE IF EXISTS `group`;"""
