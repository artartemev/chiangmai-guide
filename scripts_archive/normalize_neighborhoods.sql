-- Normalization of neighborhood column in chiangmai_guide.db
BEGIN TRANSACTION;

-- 1. Old City
UPDATE items SET neighborhood = 'Old City' WHERE neighborhood IN (
    'Old City / Chaiyapoom',
    'Old City / Chang Moi',
    'Old City / Haiya',
    'Old City / Intrawarorot',
    'Old City / Kotchasarn',
    'Old City / Manee Nopparat',
    'Old City / Moat',
    'Old City / Moon Muang',
    'Old City / Moon Muang Soi 9',
    'Old City / Phra Sing',
    'Old City / Prapokklao',
    'Old City / Rajvithi',
    'Old City / Ratchadamnoen',
    'Old City / Ratchadamnoen Soi 7',
    'Old City / Ratchamanka',
    'Old City / Ratchapakhinai',
    'Old City / Ratwithi',
    'Old City / Samlarn',
    'Old City / Si Phum',
    'Old City / Sithiwongse',
    'Old City / Sri Phum',
    'Old City / Sri Phum Soi 7',
    'Old City / Sri Poom',
    'Old City / Thapae'
);

-- 2. Nimman
UPDATE items SET neighborhood = 'Nimman' WHERE neighborhood IN (
    'Huay Kaew / Nimman',
    'Nimman / MAYA Mall',
    'Nimman / Siri Mangkalajarn',
    'Nimman / Soi 11',
    'Nimman / Soi 2',
    'Nimman / Soi 3',
    'Nimman / Soi 5',
    'Nimman / Soi 8',
    'Nimman / Soi 9',
    'Suthep / Nimman'
);

-- 3. Suthep / CMU
UPDATE items SET neighborhood = 'Suthep / CMU' WHERE neighborhood IN (
    'Suthep',
    'Suthep / Airport',
    'Suthep / Baan Kang Wat',
    'Suthep / CMU',
    'Suthep / CMU Back Gate',
    'Suthep / CMU Lake',
    'Suthep / Canal Rd',
    'Suthep / Chang Phueak foothills',
    'Suthep / Huay Kaew',
    'Suthep / Old Airport Rd',
    'Suthep / Wat Suan Dok',
    'Suthep / Wing 41'
);

-- 4. Chang Phueak
UPDATE items SET neighborhood = 'Chang Phueak' WHERE neighborhood IN (
    'Chang Phueak / Canal Rd',
    'Chang Phueak / Jed Yod',
    'Chang Phueak / Jing Jai',
    'Chang Phueak / Maya',
    'Chang Phueak / Suthep'
);

-- 5. Santitham
UPDATE items SET neighborhood = 'Santitham' WHERE neighborhood IN (
    'Chang Phueak / Santisuk',
    'Chang Phueak / Santitham'
);

-- 6. Hang Dong
UPDATE items SET neighborhood = 'Hang Dong' WHERE neighborhood IN (
    'Hang Dong / Ban Pong',
    'Hang Dong / Kad Farang',
    'Hang Dong / Mae Hia',
    'Hang Dong / Nam Phrae',
    'Hang Dong / Nong Kaeo',
    'Hang Dong / Nong Kwai',
    'Hang Dong / Samoeng',
    'Hang Dong / San Phak Wan'
);

-- 7. Mae Rim
UPDATE items SET neighborhood = 'Mae Rim' WHERE neighborhood IN (
    'Mae Rim / Chonprathan',
    'Mae Rim / Don Kaeo',
    'Mae Rim / Mae Raem',
    'Mae Rim / Mon Cham',
    'Mae Rim / Pong Yaeng'
);

-- 8. Riverside / Wat Ket
UPDATE items SET neighborhood = 'Riverside / Wat Ket' WHERE neighborhood IN (
    'Chang Khlan / Ping River',
    'Pa Daet / Ping River',
    'Pa Tan / Ping River',
    'San Phi Suea / Ping River',
    'Wat Ket',
    'Wat Ket / Arcade',
    'Wat Ket / Kaew Nawarat',
    'Wat Ket / Riverside'
);

-- 9. Night Bazaar / Chang Khlan
UPDATE items SET neighborhood = 'Night Bazaar / Chang Khlan' WHERE neighborhood IN (
    'Chang Khlan',
    'Chang Khlan / Night Bazaar',
    'Chang Khlan / Sridonchai',
    'Chang Moi',
    'Chang Moi / Warorot',
    'Pa Daet',
    'Pa Daet / Chang Khlan',
    'Pa Daet / Hang Dong Rd'
);

-- 10. Haiya / South Gate
UPDATE items SET neighborhood = 'Haiya / South Gate' WHERE neighborhood IN (
    'Haiya',
    'Haiya / Kad Kom',
    'Haiya / Nantaram',
    'Haiya / South Gate',
    'Haiya / Suriyawong',
    'Haiya / Thipanet',
    'Haiya / Wua Lai'
);

-- 11. Fa Ham / Superhighway
UPDATE items SET neighborhood = 'Fa Ham / Superhighway' WHERE neighborhood IN (
    'Fa Ham / Central Festival',
    'Fa Ham / Central Festival 5th Floor',
    'Fa Ham / Charoen Rat',
    'Fa Ham / Meechok',
    'Fa Ham / Ruamchok',
    'Fa Ham / Superhighway',
    'Fa Ham / Wang Sing Kham'
);

-- 12. San Sai
UPDATE items SET neighborhood = 'San Sai' WHERE neighborhood IN (
    'San Sai / Muang Kaeo',
    'San Sai / Pa Phai'
);

-- 13. San Kamphaeng / Doi Saket
UPDATE items SET neighborhood = 'San Kamphaeng / Doi Saket' WHERE neighborhood IN (
    'Ban Thi / San Kamphaeng border',
    'Doi Saket',
    'Doi Saket / Luang Nuea',
    'Doi Saket / Pa Miang',
    'Doi Saket / Talat Khwan',
    'Mae On',
    'Mae On / Huai Kaeo',
    'Mae On / Mae Kampong',
    'Mae On / San Kamphaeng',
    'San Kamphaeng',
    'San Kamphaeng / Ban Sa Ha Khon',
    'San Kamphaeng / San Klang',
    'San Kamphaeng / Ton Pao',
    'Ton Pao / San Kamphaeng'
);

-- 14. Mae Taeng / Chiang Dao
UPDATE items SET neighborhood = 'Mae Taeng / Chiang Dao' WHERE neighborhood IN (
    'Chiang Dao',
    'Chiang Dao / Pha Daeng',
    'Mae Taeng / Huai Nam Dang',
    'Mae Taeng / Sri Lanna',
    'Pai / Chiang Dao'
);

-- 15. Doi Inthanon / Chom Thong
UPDATE items SET neighborhood = 'Doi Inthanon / Chom Thong' WHERE neighborhood IN (
    'Chom Thong / Op Luang',
    'Doi Inthanon',
    'Doi Inthanon / Ban Luang',
    'Doi Inthanon / Chom Thong',
    'Doi Inthanon Summit'
);

-- 16. Doi Suthep-Pui
UPDATE items SET neighborhood = 'Doi Suthep-Pui' WHERE neighborhood IN (
    'Doi Suthep'
);

-- 17. Huay Kaew
UPDATE items SET neighborhood = 'Huay Kaew' WHERE neighborhood IN (
    'Huay Kaew / Malin Plaza'
);

-- 18. Pai / Mae Hong Son
UPDATE items SET neighborhood = 'Pai / Mae Hong Son' WHERE neighborhood IN (
    'Mae Hong Son',
    'Pai / Mae Hong Son',
    'Pai / Mueang Paeng',
    'Pang Mapha / Mae Hong Son'
);

-- 19. Chiang Rai / Golden Triangle
UPDATE items SET neighborhood = 'Chiang Rai / Golden Triangle' WHERE neighborhood IN (
    'Chiang Rai / Doi Chang',
    'Chiang Rai / Golden Triangle',
    'Chiang Rai / Kok River',
    'Chiang Rai Valley',
    'Golden Triangle / Chiang Rai',
    'Wiang Kaen / Phu Chi Fa',
    'Wiang Pa Pao',
    'Wiang Pa Pao / Chiang Rai border'
);

-- 20. Nan Province
UPDATE items SET neighborhood = 'Nan Province' WHERE neighborhood IN (
    'Nan Province / Border'
);

-- 21. Saraphi / Hot
UPDATE items SET neighborhood = 'Saraphi / Hot' WHERE neighborhood IN (
    'Hot District',
    'San Klang',
    'San Pa Tong',
    'Saraphi / Nong Phueng'
);

-- 22. Mae Hia
UPDATE items SET neighborhood = 'Mae Hia' WHERE neighborhood IN (
    'Mae Hia / Canal Rd'
);

-- 23. Tha Sala
UPDATE items SET neighborhood = 'Tha Sala' WHERE neighborhood IN (
    'Tha Sala / Payap'
);

-- 24. Airport Area
UPDATE items SET neighborhood = 'Airport Area' WHERE neighborhood IN (
    'Airport / Haiya',
    'Airport / Mueang'
);

-- 25. Mueang Chiang Mai
-- 'Mueang Chiang Mai' is kept as is

-- 26. San Phi Suea
-- 'San Phi Suea' is kept as is (sub-variant 'San Phi Suea / Ping River' mapped to Riverside)

-- 27. Other
UPDATE items SET neighborhood = 'Other' WHERE neighborhood IN (
    'Mae Wang'
);

COMMIT;
