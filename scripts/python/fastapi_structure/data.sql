-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS fastapi_demo
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE fastapi_demo;

-- 2. 用户表
CREATE TABLE IF NOT EXISTS users (
    id          INT UNSIGNED    NOT NULL AUTO_INCREMENT COMMENT '主键',
    username    VARCHAR(50)     NOT NULL                COMMENT '用户名',
    email       VARCHAR(100)    NOT NULL                COMMENT '邮箱',
    hashed_password VARCHAR(255) NOT NULL               COMMENT '加密后的密码',
    is_active   TINYINT(1)      NOT NULL DEFAULT 1      COMMENT '是否激活',
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_users_username (username),
    UNIQUE KEY uk_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 3. 文章表（与用户一对多）
CREATE TABLE IF NOT EXISTS articles (
    id          INT UNSIGNED    NOT NULL AUTO_INCREMENT COMMENT '主键',
    title       VARCHAR(200)    NOT NULL                COMMENT '标题',
    content     TEXT                                    COMMENT '正文',
    published   TINYINT(1)      NOT NULL DEFAULT 0      COMMENT '是否发布',
    author_id   INT UNSIGNED    NOT NULL                COMMENT '作者ID',
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_articles_author_id (author_id),
    CONSTRAINT fk_articles_author
        FOREIGN KEY (author_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章表';

-- 4. 可选：插入几条测试数据
INSERT INTO users (username, email, hashed_password) VALUES
('alice', 'alice@example.com', 'fakehash_alice'),
('bob',   'bob@example.com',   'fakehash_bob');

INSERT INTO articles (title, content, published, author_id) VALUES
('Hello FastAPI', 'FastAPI 是一个现代、快速的 Web 框架……', 1, 1),
('SQLAlchemy 入门', 'SQLAlchemy 是 Python 最流行的 ORM……', 1, 1),
('草稿示例',       '这是一篇尚未发布的草稿', 0, 2);