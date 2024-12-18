CREATE TABLE USERS (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(20) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(15) DEFAULT 'active' NOT NULL CHECK (status IN ('active', 'under_review', 'muted', 'banned')),
    report_count INT DEFAULT 0
);

CREATE TABLE USER_ROLE (
    user_id BIGINT NOT NULL,
    role VARCHAR(10) NOT NULL CHECK (role IN ('User', 'Admin')),
    PRIMARY KEY (user_id, role),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE USER_FOLLOWERS (
    follower_id BIGINT NOT NULL,
    followee_id BIGINT NOT NULL,
    PRIMARY KEY (follower_id, followee_id),
    FOREIGN KEY (follower_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (followee_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE ARTICLES (
    article_id BIGSERIAL PRIMARY KEY,
    author_id BIGINT NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status VARCHAR(15) DEFAULT 'active' NOT NULL CHECK (status IN ('active', 'archived', 'under_review')),
    FOREIGN KEY (author_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE ARCHIVED_ARTICLES (
    article_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (article_id),
    FOREIGN KEY (article_id) REFERENCES ARTICLES(article_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (author_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE USER_FAVORITES (
    user_id BIGINT NOT NULL,
    article_id BIGINT NOT NULL,
    saved_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, article_id),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (article_id) REFERENCES ARTICLES(article_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE USER_SHARED (
    user_id BIGINT NOT NULL,
    article_id BIGINT NOT NULL,
    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, article_id),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (article_id) REFERENCES ARTICLES(article_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE COMMENTS (
    comment_id BIGSERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL,
    article_id BIGINT NOT NULL,
    parent_comment_id BIGINT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status VARCHAR(15) DEFAULT 'active' NOT NULL CHECK (status IN ('active', 'under_review')),
    FOREIGN KEY (owner_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (article_id) REFERENCES ARTICLES(article_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES COMMENTS(comment_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE REPORT_C (
    report_comment_id BIGSERIAL PRIMARY KEY,
    reporter_id BIGINT NOT NULL,
    target_comment_id BIGINT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL CHECK (status IN ('pending', 'reviewed')),
    FOREIGN KEY (reporter_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (target_comment_id) REFERENCES COMMENTS(comment_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE REPORT_A (
    report_article_id BIGSERIAL PRIMARY KEY,
    reporter_id BIGINT NOT NULL,
    target_article_id BIGINT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL CHECK (status IN ('pending', 'reviewed')),
    FOREIGN KEY (reporter_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (target_article_id) REFERENCES ARTICLES(article_id) ON DELETE CASCADE ON UPDATE CASCADE
);

