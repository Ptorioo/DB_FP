CREATE TABLE USERS (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    status CHAR(1) DEFAULT 'P' CHECK (status IN ('P', 'B', 'M'))
);

CREATE TABLE USER_ROLE (
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('User', 'Admin')),
    PRIMARY KEY (user_id, role)
);

CREATE TABLE ARTICLES (
    article_id SERIAL PRIMARY KEY,
    author_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE ARCHIVED_ARTICLES (
    article_id SERIAL PRIMARY KEY,
    author_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE COMMENTS (
    comment_id SERIAL PRIMARY KEY,
    article_id INT NOT NULL REFERENCES articles(article_id) ON DELETE CASCADE,
    author_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    parent_comment_id INT REFERENCES comments(comment_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
	status CHAR(1) DEFAULT 'P' CHECK (status IN ('P', 'A')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE REPORT_C (
    report_c_id SERIAL PRIMARY KEY,
    comment_id INT NOT NULL REFERENCES comments(comment_id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status CHAR(1) DEFAULT 'P' CHECK (status IN ('P', 'R'))
);

CREATE TABLE REPORT_A (
    report_a_id SERIAL PRIMARY KEY,
    article_id INT NOT NULL REFERENCES articles(article_id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status CHAR(1) DEFAULT 'P' CHECK (status IN ('P', 'R'))
);

CREATE TABLE USER_FOLLOWERS (
    follower_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    followee_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (follower_id, followee_id)
);

CREATE TABLE USER_FAVORITES (
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    article_id INT NOT NULL REFERENCES articles(article_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, article_id)
);

CREATE TABLE USER_SHARED (
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    article_id INT NOT NULL REFERENCES articles(article_id) ON DELETE CASCADE,
    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, article_id)
);

