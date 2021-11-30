use iho_db;

drop table if exists uses;
drop table if exists ingredient;
drop table if exists recipe;
drop table if exists user;

create table user (
    uid int auto_increment not null primary key,
    name varchar(50) not null,
    email varchar(50) not null,
    username varchar(50) not null,
    hashed char(60) not null,
    unique(username),
    index(username)
)
ENGINE = InnoDB;

create table recipe (
    rid int auto_increment not null primary key,
    title varchar(30) not null,
    instructions text,
    image_path varchar(50),
    tag set('breakfast', 'lunch', 'dinner', 'snack', 'vegan', 
            'vegetarian', 'pescatarian', 'quick meals', 'bake', 
            'one-pan meal', 'stovetop', 'grill', 'dessert', 
            'gluten-free', 'microwave', 'keto', 'raw', 'comfort food', 
            'drinks', 'alcoholic', 'non-alcoholic'), /* set of recipe tag options */
    post_date date,
    last_updated_date date,
    uid int not null,
    INDEX (uid),
    foreign key (uid) references user(uid) 
        on update restrict 
        on delete restrict
)
ENGINE = InnoDB;

create table ingredient (
    iid int auto_increment not null primary key,
    name varchar(30) not null
)
ENGINE = InnoDB;

create table uses (
    rid int not null,
    iid int not null,
    amount float not null,
    measurement_unit enum('pinch', 'teaspoon (tsp)', 'tablespoon (tbsp)', 
                          'fluid ounce (fl oz)', 'cup (c)', 'pint (pt)', 
                          'quart (qt)', 'gallon (gal)', 'stick', 'piece', 
                          'milliliter (mL)', 'liter (L)', 'gram (g)', 
                          'kilogram (kg)', 'ounce (oz)', 'pound (lb)', 
                          'whole', 'slice', 'each'), /* set of measurement options */
    primary key (rid, iid),
    INDEX (rid),
    INDEX (iid),
    foreign key (rid) references recipe(rid)
        on update restrict 
        on delete restrict,
    foreign key (iid) references ingredient(iid)
        on update restrict 
        on delete restrict
)
ENGINE = InnoDB;

/* TESTING CODE */

insert into user(name, username, email, hashed) values ('Alex Chin', 'ac5', 'ac5@wellesley.edu', '$2b$12$/zFygzhTGnQNe786GD0Tw.U49x7Qmdoqnxwofp/sMPKNS21OaRl0S');
insert into user(name, username, email, hashed) values ('Cherie Wang', 'cw1', 'cw1@wellesley.edu', '$2b$12$/zFygzhTGnQNe786GD0Tw.U49x7Qmdoqnxwofp/sMPKNS21OaRl0S');
insert into user(name, username, email, hashed) values ('Olivia Giandrea', 'og102', 'og102@wellesley.edu', '$2b$12$/zFygzhTGnQNe786GD0Tw.U49x7Qmdoqnxwofp/sMPKNS21OaRl0S');
insert into user(name, username, email, hashed) values ('Ivy Ho', 'iho', 'iho@wellesley.edu', '$2b$12$/zFygzhTGnQNe786GD0Tw.U49x7Qmdoqnxwofp/sMPKNS21OaRl0S');
insert into user(name, username, email, hashed) values ('Scott Anderson', 'scott', 'scott.anderson@wellesley.edu', '$2b$12$/zFygzhTGnQNe786GD0Tw.U49x7Qmdoqnxwofp/sMPKNS21OaRl0S');

insert into ingredient(name) values ('tomato');
insert into ingredient(name) values ('bread');
insert into ingredient(name) values ('basil');
insert into ingredient(name) values ('mozzarella');
insert into ingredient(name) values ('olive oil');

insert into recipe(title, uid, instructions, tag) values ('Caprese', 5, 
'Gather the ingredients. Using a serrated knife, slice an Italian sub roll in half lengthwise. Drizzle the inside with Italian extra-virgin olive oil and balsamic glaze. Add basil and tomato to one side and sprinkle with salt and pepper. Top with fresh mozzarella and close sandwich. Eat now or wrap tightly to enjoy later.',
'lunch, quick meals, vegetarian');

insert into uses(rid, iid, amount, measurement_unit) values (1,1,2,'whole');
insert into uses(rid, iid, amount, measurement_unit) values (1,2,1,'whole');
insert into uses(rid, iid, amount, measurement_unit) values (1,3,5,'piece');
insert into uses(rid, iid, amount, measurement_unit) values (1,4,3,'slice');
insert into uses(rid, iid, amount, measurement_unit) values (1,5,0.5,'tablespoon (tbsp)');

insert into ingredient(name) values ('salt');
insert into uses(rid, iid, amount, measurement_unit) values (1,6,1,'pinch');

update uses set amount = 6 where rid = 1 and iid = 3; /* more basil */

/* ivy's recipe */
insert into ingredient(name) values ('green scallion');
insert into ingredient(name) values ('flour');
insert into ingredient(name) values ('water');
insert into ingredient(name) values ('oil');
insert into recipe(title, uid, instructions, tag) values ('Scallion Pancake', 4,
"Slowly add the hot water to the flour and mix it at the same time. Mix until the hot water is fully absorbed. Slowly add the cold water and continue mixing. Dough flakes should form once all the water is added. Start to press everything together with your hand. You can add a bit more water if there's too much dry flour left. Or you can slightly add a bit more flour if the dough is very sticky. Once you've pressed all the dough flakes together, you should have little or no dry flour left. Knead about 5 mins until a tough dough is formed. Let rest for 20 mins, then knead for 1 minute to form a smooth dough. Make flour oil paste. Cut the dough into 6 pieces and work on the pieces one at a time. Use your hands to shape the dough into a rectangular shape. Roll the dough. The dough should form a very thin rectangle. Add the flour oil paste. Spread out the paste, leaving about 1” (2.5 cm) on both a long and a short end without the filling (your top and left). Add the green onion, concentrating most of it towards a long and short end with the filling. Gently roll up the dough, as tightly as possible. Press the air bubbles out of the dough strip. Further roll up the long dough strip. Tuck the end on the bottom. Gently press the tall pancake. Let rest and roll out the pancakes when you're ready to cook. Heat up a pan with a layer of oil on the bottom, add the pancake, and wiggle the pancake a few times so it won't stick. Let the pancake cook covered first. Flip the pancake and cook covered again. Then cook uncovered, until both sides of the pancake are browned.", 
'breakfast, one-pan meal, quick meals, vegetarian');

insert into uses(rid, iid, amount, measurement_unit) values (2,6,8,'whole');
insert into uses(rid, iid, amount, measurement_unit) values (2,7,2,'cup (c)');
insert into uses(rid, iid, amount, measurement_unit) values (2,8,0.75,'cup (c)');
insert into uses(rid, iid, amount, measurement_unit) values (2,9,0.25,'cup (c)');

/* olivia's recipe */
insert into ingredient (name) values ('chicken breast');
insert into ingredient (name) values ('italian seasoning');
insert into ingredient (name) values ('minced garlic');
insert into ingredient (name) values ('salt');
insert into ingredient (name) values ('red onion');
insert into ingredient (name) values ('parmesan cheese');
insert into ingredient (name) values ('brown sugar');
insert into recipe (title, uid, instructions, tag) values ('Chicken Bruschetta', 3, '1. Season chicken with Italian seasoning, garlic and salt. Heat oil in a grill pan or skillet, and sear chicken breasts over medium-high heat until browned on both sides and cooked through (about 6 minutes each side). Remove from pan; set aside and allow to rest. 2. Combine the tomatoes, red onion, basil, olive oil in a bowl. Season with salt. 3. For the balsamic glaze, combine sugar and vinegar in a small saucepan over high heat and bring to the boil. Reduce heat to low; allow to simmer for 5-8 minutes or until mixture has thickened. 4. Top each chicken breast with the tomato mixture and parmesan cheese; serve immediately.', 'lunch, dinner, stovetop');
 
insert into uses(rid, iid, amount, measurement_unit) values (3,10,2,'whole');
insert into uses(rid, iid, amount, measurement_unit) values (3,11,1,'tablespoon (tbsp)');
insert into uses(rid, iid, amount, measurement_unit) values (3,12,2,'teaspoons (tsp)');
insert into uses(rid, iid, amount, measurement_unit) values (3,13,1,'pinch');
insert into uses(rid, iid, amount, measurement_unit) values (3,1,4,'each');
insert into uses(rid, iid, amount, measurement_unit) values (3,14,0.25,'each');
insert into uses(rid, iid, amount, measurement_unit) values (3,3,0.25,'cup (c)');
insert into uses(rid, iid, amount, measurement_unit) values (3,5,2,'tablespoon (tbsp)');
insert into uses(rid, iid, amount, measurement_unit) values (3,15,0.5,'cup (c)');
insert into uses(rid, iid, amount, measurement_unit) values (3,16,2,'teaspoon (tsp)');

/* cherie's recipe */
insert into ingredient(name) values ('shrimp');
insert into ingredient(name) values ('jalapenos');
insert into ingredient(name) values ('garlic');
insert into ingredient(name) values ('green onions');
insert into ingredient(name) values ('flour');
insert into ingredient(name) values ('frying oil');
insert into ingredient(name) values ('butter');
insert into ingredient(name) values ('pepper');

Insert into recipe(title, uid, instructions, tag) values ('Salt and Pepper Shrimp', 2, "1. Rinse and strain shrimp. You can also devein your shrimp. 2. Pat the shrimps dry with a paper towel. 3. Cut 2 jalapenos, mince 4 cloves of garlic and 2 green onions. Set them aside. 4. In a large mixing bowl, coat the shrimps in 2 cups of flour. 5. Heat oil in a pot to 375F. If you don't have a thermometer, you can check the temperature by inserting a wooden chopstick into the oil. If bubbles rise, then your oil is ready. 6. Fry the shrimps for 1.5 - 2 minutes depending on your preferred crunchiness. 7. Melt 2 tbsp of butter in a hot pan (can also use oil if butter is unavailable). 8. Add the jalapenos, garlic and green onions into the pot and cook till they are slightly brown. 9. Add your tsp of salt and pepper. 10. Add your shrimp and mix everything. 11. That's all, enjoy!", 'dinner');

Insert into uses(rid, iid, amount, measurement_unit) values (4, 17, 1.5, 'pound (lb)');
Insert into uses(rid, iid, amount, measurement_unit) values (4, 18, 2, 'piece');
Insert into uses(rid, iid, amount, measurement_unit) values (4, 19, 4, 'piece');
Insert into uses(rid, iid, amount, measurement_unit) values (4, 20, 2, 'piece');
Insert into uses(rid, iid, amount, measurement_unit) values (4, 21, 2, 'cup (c)');
Insert into uses(rid, iid, amount, measurement_unit) values (4, 22, 1, 'cup (c)');
Insert into uses(rid, iid, amount, measurement_unit) values (4, 23, 2, 'tablespoon (tbsp)');
Insert into uses(rid, iid, amount, measurement_unit) values (4, 5, 1, 'teaspoon (tsp)');
Insert into uses(rid, iid, amount, measurement_unit) values (4, 24, 1, 'teaspoon (tsp)');

/* alex's recipe tuna melt */
insert into ingredient(name) values ('canned tuna');
insert into ingredient(name) values ('celery');
insert into ingredient(name) values ('cranberries');

insert into recipe(title,uid,instructions, tag) values ('Tuna Melt', 1, 'Put bread in toaster. Chop celery. Combine canned tuna, celery, cranberries, pepper, and salt in a bowl. Mix until everything is incorporated. Place mixture on toasted bread. Top with mozzarella cheese. Bake in oven for 5-10 minutes or until cheese is melted.', 'lunch, pescatarian, quick meals, bake');

insert into uses(rid, iid, amount, measurement_unit) values (5,25,1, 'cup (c)'); 
insert into uses(rid, iid, amount, measurement_unit) values (5,26,1,'whole'); 
insert into uses(rid, iid, amount, measurement_unit) values (5,27,0.25,'cup (c)'); 
insert into uses(rid, iid, amount, measurement_unit) values (5,24,3, 'pinch'); 
insert into uses(rid, iid, amount, measurement_unit) values (5,2,1, 'slice'); 
insert into uses(rid, iid, amount, measurement_unit) values (5,13,1, 'pinch'); 
insert into uses(rid, iid, amount, measurement_unit) values (5,4,1, 'ounce (oz)'); 
