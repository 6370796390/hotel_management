SELECT * FROM hotel_management.rooms;
DROP TABLE rooms;
DROP TABLE menus;
DROP TABLE reservations;
DROP TABLE housekeeping;
ALTER TABLE reservations DROP PRIMARY KEY;
ALTER TABLE reservations MODIFY COLUMN room_number INT;
ALTER TABLE reservations ADD PRIMARY KEY (id);

INSERT INTO rooms (room_number, room_category, room_feature, current_status)
VALUES (111, 'superdeluxe', 'Sea Facing', 'available');
CREATE TABLE rooms (
    room_number INT PRIMARY KEY, -- Unique identifier for the room
	room_category ENUM('suite', 'deluxe', 'superdelux') NOT NULL,
    room_feature VARCHAR(50) NOT NULL, 
    current_status ENUM('available', 'booked', 'maintenance') NOT NULL 
);
DESCRIBE rooms;
ALTER TABLE rooms MODIFY current_status VARCHAR(50) NOT NULL;
CREATE TABLE reservations (
    id INT AUTO_INCREMENT PRIMARY KEY, -- id is now correctly set as the primary key
    guest_name VARCHAR(255) NOT NULL,
    contact_number VARCHAR(15) NOT NULL,
    email VARCHAR(255) NOT NULL,
    gender ENUM('male', 'female', 'other') NOT NULL,
    id_proof_type ENUM('aadhar', 'passport', 'voter_id') NOT NULL,
    id_proof_number VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    room_category ENUM('suite', 'deluxe', 'superdelux') NOT NULL,
    room_number INT NOT NULL, -- Define the room_number column with INT type and NOT NULL
    special_requests TEXT,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (room_number) REFERENCES rooms(room_number) -- Correctly reference the rooms table
);


CREATE TABLE menus (
    id INT AUTO_INCREMENT PRIMARY KEY,           -- Unique identifier for each menu item
    menu_name VARCHAR(100) NOT NULL,             -- Name of the menu, mandatory
    menu_description TEXT,                       -- Description of the menu
    menu_category ENUM('Veg', 'Non-veg', 'Vegan') NOT NULL, -- Category of the menu
    price DECIMAL(10, 2) NOT NULL,               -- Price of the item
    item_name VARCHAR(100),                      -- Name of the item
    room_number VARCHAR(10),                             -- Room number associated with the order
    ordered_quantity INT NOT NULL,               -- Quantity ordered
    order_total DECIMAL(10, 2) NOT NULL,         -- Total price after applying 12% GST
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp for when the record was created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- Timestamp for last update
    FOREIGN KEY (room_number) REFERENCES reservations(room_number)
        ON DELETE SET NULL ON UPDATE CASCADE
);
CREATE TABLE menus (
    id INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier for each menu item
    menu_name VARCHAR(255) NOT NULL,   -- Name of the menu
    menu_description TEXT,            -- Description of the menu
    menu_category VARCHAR(255) NOT NULL, -- Category of the menu
    price DECIMAL(10, 2) NOT NULL,    -- Price of the item
    item_name VARCHAR(255) NOT NULL,  -- Name of the item
    room_number VARCHAR(50) NOT NULL, -- Room number associated with the order
    ordered_quantity INT NOT NULL,    -- Quantity of the item ordered
    order_total DECIMAL(10, 2) NOT NULL, -- Total price after add    ing 12% GST
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp for record creation
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- Timestamp for last update
);
CREATE TABLE housekeeping (
    room_no INT UNIQUE,
    staff_id VARCHAR(50) PRIMARY KEY,
    task_type VARCHAR(100) NOT NULL,
    current_status VARCHAR(50) NOT NULL,
    last_clean_date DATE,
    FOREIGN KEY (staff_id) REFERENCES staff(employee_id),
    FOREIGN KEY (room_no) REFERENCES rooms(room_number)
);
   CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_email ON admin (email);
