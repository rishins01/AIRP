create database airp;
use airp;

create table User(
Id int primary key auto_increment,
type char(1) not null default 1,
username varchar(20) not null unique,
password varchar(20) not null
);

create table Inventory(
VendorId int,
productID int not null unique,
productname varchar(50) not null,
quantity int not null,
category varchar(50) not null,
description varchar(255) not null,
image varchar(255) not null,
price int not null, 
FOREIGN KEY (VendorId) REFERENCES User(Id)
);

create table Orders(
Id int,
productID int not null,
quantity int not null,
status varchar(20) not null,
times timestamp,
FOREIGN KEY (Id) REFERENCES User(Id),
FOREIGN KEY (productID) REFERENCES Inventory(productID)
);

create table Cart(
Id int,
productID int,
quantity int not null,
FOREIGN KEY (Id) REFERENCES User(Id),
FOREIGN KEY (productID) REFERENCES Inventory(productID)
);

create table Recently_Viewed(
Id int,
productID int,
timestamp timestamp,
FOREIGN KEY (Id) REFERENCES User(Id),
FOREIGN KEY (productID) REFERENCES Inventory(productID)
);

create table Recently_Searched(
Id int,
query varchar(20) not null,
timestamp timestamp,
FOREIGN KEY (Id) REFERENCES User(Id)
);



insert into user value(1,'Admin','Admin','Admin');
delete from inventory where	vendorId=1;
select * from user; 	
select * from inventory;
select * from cart;	
select * from recently_searched;
select * from recently_viewed;



insert into inventory values
(2,1,'Laptop X',50,'Electronics','best laptop of 2021','../static/laptop.jpeg',1000),
(2,2,'Laptop Y',50,'Electronics','best laptop of 2022','../static/laptop1.jpeg',1100),
(2,3,'Laptop Z',50,'Electronics','best laptop of 2023','../static/laptop2jpeg',1200),
(2,4,'Laptop XY',50,'Electronics','best laptop of 2024','../static/laptop3.jpeg',1300),	
(2,5,'Laptop XYZ',50,'Electronics','best laptop of 2025','../static/laptop4.jpeg',1400);


DELIMITER //

CREATE PROCEDURE get_cart_items(IN user_id INT)
BEGIN
    SELECT i.productID, i.productname, i.image, i.price, c.quantity
    FROM inventory i
    JOIN cart c ON i.productID = c.productID
    WHERE c.id = user_id;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER check_cart_quantity_before_insert
BEFORE INSERT ON Cart
FOR EACH ROW
BEGIN
    DECLARE available_quantity INT;

    SELECT quantity INTO available_quantity 
    FROM Inventory 
    WHERE productID = NEW.productID;

    IF NEW.quantity > available_quantity THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Quantity in cart cannot exceed available inventory.';
    END IF;
END; //

DELIMITER ;

DELIMITER //

CREATE TRIGGER check_cart_quantity_before_update
BEFORE UPDATE ON Cart
FOR EACH ROW
BEGIN
    DECLARE available_quantity INT;

    -- Get the available quantity from the Inventory for the given productID
    SELECT quantity INTO available_quantity 
    FROM Inventory 
    WHERE productID = NEW.productID;

    -- Check if the cart quantity exceeds the available inventory
    IF NEW.quantity > available_quantity THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Quantity in cart cannot exceed available inventory.';
    END IF;
END; //

DELIMITER ;

DELIMITER //

CREATE PROCEDURE upsert_recently_searched(
    IN user_id INT,
    IN search_query VARCHAR(100),
    IN timestamp_value DATETIME
)
BEGIN
    UPDATE recently_searched
    SET timestamp = timestamp_value
    WHERE id = user_id AND query = search_query;

    IF ROW_COUNT() = 0 THEN
        INSERT INTO recently_searched (id, query, timestamp)
        VALUES (user_id, search_query, timestamp_value);
    END IF;
END //

DELIMITER ;


