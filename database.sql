create table category(
    codename varchar(255) primary key,
    name varchar(255),
    aliases text
);

create table expense(
    id integer primary key,
    amount integer,
    created datetime,
    category_codename integer,
    raw_text text,
    user_id text,
    paying_type text,
    FOREIGN KEY(category_codename) REFERENCES category(codename),
    FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);

create table income(
    id INTEGER primary key,
	amount INTEGER,
	paying_type	TEXT,
	user_id	TEXT,
	created	datetime,
  	FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);

CREATE TABLE "users" (
	"user_id"	TEXT UNIQUE,
	"active"	INTEGER,
	PRIMARY KEY("user_id")
);

insert into category (codename, name, aliases)
values
    ("products", "cупермаркеты", "продукты, еда, хозтовары, супермаркет, маркет, маркетплейс, напитки, вода, магазин, продуктовый"),
    ("transport", "транспорт", "метро, автобус, metro, bus, трамвай, маршрутка, такси, taxi, каршеринг, бензин, автостоянка, парковка"),
    ("communal", "коммунальные платежи", "жкх, квартплата, коммуналка, интернет, электричество, отопление"),
    ("phone", "мобильная связь", "мобильный, связь, телефон"),
    ("subscriptions", "подписки", "подписка, нетфликс, netflix, youtube, ютуб, музыка, music, spotify"),
    ("coffee", "кофе", "капучинно, латте, американо, старбакс, кофехаус"),
    ("cafe", "общепит", "столовая, ланч, бизнес-ланч, 'бизнес ланч', кафе, ресторан, рест, мак, макдональдс, макдак, kfc, кфс"),
    ("books", "книги", "учебник, литература, литра, лит-ра, книга, книжка, book"),
    ("pharmacy", "аптека", "таблетки, лекарство, лекарства"),
    ("education", "образование", "курс, обучение, институт, подготовительный курс"),
    ("shopping", "одежда и обувь", "брюки, рубашка, футболка, кофта, худи, одежда, обувь, шоппинг, кроссовки, туфли, кеды, джинсы"),
    ("health", "здоровье", "лечение, больница, клиника, стоматолог, врач, доктор"),
    ("bank", "банковские операции", "банк, онлайн-банк, онлайн банк, перевод, переводы, оплата счета, счет на оплату, страховой взнос, страховые взносы, страховка"),
    ("other", "другое", "прочее");
