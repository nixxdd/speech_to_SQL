CREATE TABLE games(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(255) NOT NULL,
    release_date DATE NOT NULL,
    genre VARCHAR(255) NOT NULL,
    publisher VARCHAR(255) NOT NULL,
    developer VARCHAR(255) NOT NULL
    -- metacritic_score INT NOT NULL
);

CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    registeration_date DATE NOT NULL,
    country VARCHAR(255) NOT NULL
);


CREATE TABLE reviews(
    user_id INT NOT NULL,
    game_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 10),
    review_text TEXT,
    review_date DATE NOT NULL,
    PRIMARY KEY (user_id, game_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);


INSERT INTO games (name, platform, release_date, genre, publisher, developer) VALUES
('The Legend of Zelda: Breath of the Wild', 'Nintendo Switch', '2017-03-03', 'Action-adventure', 'Nintendo', 'Nintendo EPD'),
('God of War', 'PlayStation 4', '2018-04-20', 'Action-adventure', 'Sony Interactive Entertainment', 'Santa Monica Studio'),
('Red Dead Redemption 2', 'PlayStation 4', '2018-10-26', 'Action-adventure', 'Rockstar Games', 'Rockstar Studios'),
('Red Dead Redemption 2', 'Xbox One', '2018-10-26', 'Action-adventure', 'Rockstar Games', 'Rockstar Studios'),
('Red Dead Redemption 2', 'PC', '2018-10-26', 'Action-adventure', 'Rockstar Games', 'Rockstar Studios'),
('The Witcher 3: Wild Hunt', 'PlayStation 4', '2015-05-19', 'Action RPG', 'CD Projekt Red', 'CD Projekt Red'),
('The Witcher 3: Wild Hunt', 'Xbox One', '2015-05-19', 'Action RPG', 'CD Projekt Red', 'CD Projekt Red'),
('The Witcher 3: Wild Hunt', 'PC', '2015-05-19', 'Action RPG', 'CD Projekt Red', 'CD Projekt Red'),
('Hades', 'PC', '2020-09-17', 'Rogue-like dungeon crawler', 'Supergiant Games', 'Supergiant Games'),
('Hades', 'Nintendo Switch', '2020-09-17', 'Rogue-like dungeon crawler', 'Supergiant Games', 'Supergiant Games'),
('Cyberpunk 2077', 'PlayStation 4', '2020-12-10', 'Action RPG', 'CD Projekt Red', 'CD Projekt Red'),
('Cyberpunk 2077', 'Xbox One', '2020-12-10', 'Action RPG', 'CD Projekt Red', 'CD Projekt Red'),
('Cyberpunk 2077', 'PC', '2020-12-10', 'Action RPG', 'CD Projekt Red', 'CD Projekt Red'),
('Animal Crossing: New Horizons', 'Nintendo Switch', '2020-03-20', 'Social simulation', 'Nintendo', 'Nintendo EPD'),
('Doom Eternal', 'PlayStation 4', '2020-03-20', 'First-person shooter', 'Bethesda Softworks', 'id Software'),
('Doom Eternal', 'Xbox One', '2020-03-20', 'First-person shooter', 'Bethesda Softworks', 'id Software'),
('Doom Eternal', 'PC', '2020-03-20', 'First-person shooter', 'Bethesda Softworks', 'id Software'),
('Final Fantasy VII Remake', 'PlayStation 4', '2020-04-10', 'Action RPG', 'Square Enix', 'Square Enix Creative Business Unit III'),
('Ghost of Tsushima', 'PlayStation 4', '2020-07-17', 'Action-adventure', 'Sony Interactive Entertainment', 'Sucker Punch Productions');


INSERT INTO users (username, registeration_date, country) VALUES
('gamer123', '2020-01-15', 'USA'),
('proplayer', '2019-11-20', 'UK'),
('casualgamer', '2021-05-10', 'Canada'),
('retrofan', '2018-08-30', 'Australia'),
('indiegaymer', '2020-03-25', 'Germany');

INSERT INTO reviews (user_id, game_id, rating, review_text, review_date) VALUES
(1, 1, 10, 'An absolute masterpiece! The open world is breathtaking and the gameplay is incredibly satisfying.', '2017-03-05'),
(2, 1, 9, 'A fantastic game with a beautiful world to explore. The story could have been stronger though.', '2017-03-10'),
(3, 2, 10, 'One of the best games I have ever played. The story and characters are amazing.', '2018-04-22'),
(4, 3, 9, 'A great game with an immersive world and engaging story. The gameplay is also very enjoyable.', '2018-10-28'),
(5, 4, 9, 'The PC version runs smoothly and looks fantastic. A must-play for fans of open-world games.', '2018-11-01'),
(1, 5, 8, 'The PC version is good, but it had some performance issues at launch. Still a great game though.', '2018-11-05'),
(2, 6, 10, 'An incredible RPG with a rich story and deep gameplay. The world is also stunning.', '2015-05-20'),
(3, 7, 9, 'A fantastic port of the game. The gameplay and story are just as good as the console versions.', '2015-06-01'),
(4, 8, 9, 'The PC version looks amazing and runs well. A must-play for fans of RPGs.', '2015-06-10'),
(5, 9, 10, 'Hades is an absolute gem! The gameplay is addictive and the story is surprisingly deep for a rogue-like.', '2020-09-20'),
(1, 10, 9, 'The Switch version is great for playing on the go. The gameplay is just as good as the PC version.', '2020-09-25'),
(2, 11, 7, 'Cyberpunk had a lot of potential but was marred by bugs and performance issues at launch.', '2020-12-15'),
(3, 12, 7, 'The Xbox One version had similar issues to the PlayStation version. Still a good game though.', '2020-12-20'),
(4, 13, 8, 'The PC version runs better than the console versions but still had some issues at launch.', '2020-12-25'),
(5, 14, 10, 'Animal Crossing is such a charming and relaxing game. Perfect for unwinding after a long day.', '2020-03-22'),
(1, 15, 9, 'Doom Eternal is an intense and satisfying shooter. The gameplay is fast-paced and fun.', '2020-03-25'),
(2, 16, 9, 'The Xbox One version of Doom Eternal runs well and looks great. A must-play for fans of shooters.', '2020-03-30'),
(3, 17, 9, 'The PC version of Doom Eternal is fantastic. The graphics are stunning and the gameplay is smooth.', '2020-04-05'),
(4, 18, 8, 'Final Fantasy VII Remake is a great reimagining of the classic game. The combat is fun but can be a bit repetitive.', '2020-04-15'),
(5, 19, 9, 'Ghost of Tsushima is a beautiful and engaging game. The story and characters are compelling.', '2020-07-20'),
(1, 19, 10, 'An absolute masterpiece! The open world is breathtaking and the gameplay is incredibly satisfying.', '2020-07-25');