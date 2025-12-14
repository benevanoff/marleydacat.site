DROP DATABASE IF EXISTS `marley_db`;
CREATE DATABASE marley_db;
USE marley_db;

DROP TABLE IF EXISTS `users`;
CREATE TABLE users (
    username VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

DROP TABLE IF EXISTS `user_invites`;
CREATE TABLE user_invites (
    invite_key VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) -- foreign key ?
);

DROP TABLE IF EXISTS `posts`;
CREATE TABLE posts (
    post_id INT PRIMARY KEY AUTO_INCREMENT,
    poster_username VARCHAR(255),
    title VARCHAR(255),
    description VARCHAR(1024),
    image_name VARCHAR(255),
    FOREIGN KEY (poster_username) REFERENCES users(username) ON DELETE SET NULL ON UPDATE CASCADE
);

DROP TABLE IF EXISTS `likes`;
CREATE TABLE likes (
    like_id INT PRIMARY KEY AUTO_INCREMENT,
    liker_username VARCHAR(255),
    liked_post_id INT,
    FOREIGN KEY (liker_username) REFERENCES users(username) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (liked_post_id) REFERENCES posts(post_id) ON DELETE CASCADE ON UPDATE CASCADE
);