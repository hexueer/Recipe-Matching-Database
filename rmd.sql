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
    amount int not null,
    measurement_unit enum('pinch', 'teaspoon (tsp)', 'tablespoon (tbsp)', 
                          'fluid ounce (fl oz)', 'cup (c)', 'pint (pt)', 
                          'quart (qt)', 'gallon (gal)', 'stick', 'piece', 
                          'milliliter (mL)', 'liter (L)', 'gram (g)', 
                          'kilogram (kg)', 'ounce (oz)', 'pound (lb)', 
                          'whole', 'slice'), /* set of measurement options */
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

insert into recipe(title, uid, instructions, tag) values ('Caprese', 1, 
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