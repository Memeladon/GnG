-- +goose Up
-- +goose StatementBegin

-- Populate cells table with game board data
INSERT INTO cells (name, description, cell_type, image_path, position, created_at, updated_at) VALUES
-- СТАРТ
('СТАРТ', '{"event": "+ 5 Победных очков"}', 'Старт', 'public/storage/cells/start.png', 0, NOW(), NOW()),

-- Kalawar (Alawar)
('Kalawar (Alawar)', '{"duration": "1-4", "price": "0-6"}', 'Игровая', 'public/storage/cells/kalawar.png', 1, NOW(), NOW()),

-- Подлянка/Кайфарик 1
('Подлянка/Кайфарик 1', '{}', 'Подлянка', 'public/storage/cells/podlyanka.png', 2, NOW(), NOW()),

-- THREE-DP (FIVE-BN)
('THREE-DP (FIVE-BN)', '{"duration": "2-5", "price": "5-12"}', 'Игровая', 'public/storage/cells/three-dp.png', 3, NOW(), NOW()),

-- YEA GAMES (EA GAMES)
('YEA GAMES (EA GAMES)', '{"duration": "1-5", "price": "7-15"}', 'Игровая', 'public/storage/cells/yea-games.png', 4, NOW(), NOW()),

-- Вопросик 1
('Вопросик 1', '{}', 'Вопрос', 'public/storage/cells/question-cell-ka.png', 5, NOW(), NOW()),

-- DYDOCE (DICE)
('DYDOCE (DICE)', '{"duration": "2-7", "price": "0-8"}', 'Игровая', 'public/storage/cells/dydoce.png', 6, NOW(), NOW()),

-- BIG DISH (BIG FISH)
('BIG DISH (BIG FISH)', '{"duration": "3-7", "price": "0-10"}', 'Игровая', 'public/storage/cells/big-cock-dish-lmao-----hyyyyyyyyyype.png', 7, NOW(), NOW()),

-- Deactivision (Activision)
('Deactivision (Activision)', '{"duration": "3-8", "price": "10-20"}', 'Игровая', 'public/storage/cells/deactivisionXXX.png', 8, NOW(), NOW()),

-- Pornstar Games (Rockstar Games)
('Pornstar Games (Rockstar Games)', '{"duration": "4-10", "price": "15-30"}', 'Игровая', 'public/storage/cells/rock.png', 9, NOW(), NOW()),

-- ТЮРЯГА
('ТЮРЯГА', '{"duration": "6-16"}', 'Тюрьма', 'public/storage/cells/.png', 10, NOW(), NOW()),

-- Naughty boy (Naughty dog)
('Naughty boy (Naughty dog)', '{"duration": "3-7", "rating": "40-80"}', 'Игровая', 'public/storage/cells/naughtyboy.png', 11, NOW(), NOW()),

-- Подлянка/Кайфарик 2
('Подлянка/Кайфарик 2', '{}', 'Подлянка', 'public/storage/cells/podlyanka.png', 12, NOW(), NOW()),

-- PoroSad Studio (SadSquare Studio)
('PoroSad Studio (SadSquare Studio)', '{"duration": "4-8", "price": "7-15"}', 'Игровая', 'public/storage/cells/porosad.png', 13, NOW(), NOW()),

-- SIGA (SEGA)
('SIGA (SEGA)', '{"duration": "4-8", "price": "0-7"}', 'Игровая', 'public/storage/cells/siga.png', 14, NOW(), NOW()),

-- Вопросик 2
('Вопросик 2', '{}', 'Вопрос', 'public/storage/cells/question-cell-ka.png', 15, NOW(), NOW()),

-- CUMCOM (CAPCOM)
('CUMCOM (CAPCOM)', '{"duration": "5-10", "price": "0-15"}', 'Игровая', 'public/storage/cells/cumcom.png', 16, NOW(), NOW()),

-- Team Plum (Team Cherry)
('Team Plum (Team Cherry)', '{"duration": "5-10"}', 'Игровая', 'public/storage/cells/team-plum.png', 17, NOW(), NOW()),

-- Team Vegan (Team Meat)
('Team Vegan (Team Meat)', '{"duration": "7-15", "price": "15-30"}', 'Игровая', 'public/storage/cells/green-meat-boy-with-fork.png', 18, NOW(), NOW()),

-- Red Head (Red Barrels)
('Red Head (Red Barrels)', '{"duration": "7-15", "price": "0-15"}', 'Игровая', 'public/storage/cells/read-heads.png', 19, NOW(), NOW()),

-- Аукошная
('Аукошная', '{}', 'Аукошная', 'public/storage/cells/auk.png', 20, NOW(), NOW()),

-- LEGKO (LEGO)
('LEGKO (LEGO)', '{"rating": "45-85", "price": "15-35"}', 'Игровая', 'public/storage/cells/legko.png', 21, NOW(), NOW()),

-- Подлянка/Кайфарик 3
('Подлянка/Кайфарик 3', '{}', 'Подлянка', 'public/storage/cells/podlyanka.png', 22, NOW(), NOW()),

-- Microguy Games (SuperGiant Games)
('Microguy Games (SuperGiant Games)', '{"duration": "7-14"}', 'Игровая', 'public/storage/cells/microguygames.png', 23, NOW(), NOW()),

-- Noproofs Games (Fireproof Games)
('Noproofs Games (Fireproof Games)', '{"duration": "6-12", "rating": "30-70"}', 'Игровая', 'public/storage/cells/noproof-games.png', 24, NOW(), NOW()),

-- Вопросик 3
('Вопросик 3', '{}', 'Вопрос', 'public/storage/cells/question-cell-ka.png', 25, NOW(), NOW()),

-- Bondage Nyamca (Bandai Namco)
('Bondage Nyamca (Bandai Namco)', '{"price": "7-20"}', 'Игровая', 'public/storage/cells/bondage.png', 26, NOW(), NOW()),

-- Leather club door (Cellar Door Games)
('Leather club door (Cellar Door Games)', '{"duration": "8-16", "price": "10-30"}', 'Игровая', 'public/storage/cells/clubdoor.png', 27, NOW(), NOW()),

-- Vlomve (Valve)
('Vlomve (Valve)', '{"duration": "9-17", "price": "20-40"}', 'Игровая', 'public/storage/cells/vlomve.png', 28, NOW(), NOW()),

-- Kawaimi (Konami)
('Kawaimi (Konami)', '{"duration": "12-20", "price": "10-20"}', 'Игровая', 'public/storage/cells/kawaimi.png', 29, NOW(), NOW()),

-- Лотерея
('Лотерея', '{}', 'Лотерея', 'public/storage/cells/topori.png', 30, NOW(), NOW()),

-- Besedka (Bethesda)
('Besedka (Bethesda)', '{"duration": "8-14", "rating": "25-65"}', 'Игровая', 'public/storage/cells/besedka.png', 31, NOW(), NOW()),

-- Подлянка/Кайфарик 4
('Подлянка/Кайфарик 4', '{}', 'Подлянка', 'public/storage/cells/podlyanka.png', 32, NOW(), NOW()),

-- Squidwardix (SquareEnix)
('Squidwardix (SquareEnix)', '{"rating": "20-70", "price": "20-100"}', 'Игровая', 'public/storage/cells/squidwardix.png', 33, NOW(), NOW()),

-- DVD PROJECT BRED (CD PROJECT RED)
('DVD PROJECT BRED (CD PROJECT RED)', '{"duration": "10-18", "price": "10-25"}', 'Игровая', 'public/storage/cells/bred.png', 34, NOW(), NOW()),

-- Вопросик 4
('Вопросик 4', '{}', 'Вопрос', 'public/storage/cells/question-cell-ka.png', 35, NOW(), NOW()),

-- Chelic Entertainment (Relic Entertainment)
('Chelic Entertainment (Relic Entertainment)', '{"duration": "10-20", "price": "0-25"}', 'Игровая', 'public/storage/cells/chelic.png', 36, NOW(), NOW()),

-- Kunisoft (Ubisoft)
('Kunisoft (Ubisoft)', '{"duration": "10-20", "price": "25-100"}', 'Игровая', 'public/storage/cells/kunisoft.png', 37, NOW(), NOW()),

-- Piratix Games (Firaxis Games)
('Piratix Games (Firaxis Games)', '{"price": "30-100"}', 'Игровая', 'public/storage/cells/piratix.png', 38, NOW(), NOW()),

-- Blazerd (Blizzard)
('Blazerd (Blizzard)', '{"duration": "14-300"}', 'Игровая', 'public/storage/cells/blazerd.png', 39, NOW(), NOW());

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DELETE FROM cells;
-- +goose StatementEnd