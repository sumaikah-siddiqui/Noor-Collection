

DROP DATABASE IF EXISTS noor_collections;
CREATE DATABASE noor_collections;
USE noor_collections;

-- Disable key checks temporarily for clean, order-independent table builds
SET FOREIGN_KEY_CHECKS = 0;

-- --------------------------------------------------------------------
-- 1. BASE DDL: TABLE CREATION
-- --------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    phone       VARCHAR(20)  NOT NULL,
    address     TEXT         NOT NULL
);

CREATE TABLE IF NOT EXISTS Products (
    product_id     INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(100)  NOT NULL,
    material       VARCHAR(50)   NOT NULL,
    price          DECIMAL(10,2) NOT NULL,
    stock_quantity INT           NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Orders (
    order_id     INT AUTO_INCREMENT PRIMARY KEY,
    customer_id  INT           NOT NULL,
    order_date   DATE          NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status       ENUM('Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    notes        VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Order_Items (
    item_id    INT AUTO_INCREMENT PRIMARY KEY,
    order_id   INT           NOT NULL,
    product_id INT           NOT NULL,
    quantity   INT           NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS Payments (
    payment_id     INT AUTO_INCREMENT PRIMARY KEY,
    order_id       INT           NOT NULL,
    payment_date   DATE          NOT NULL,
    amount_paid    DECIMAL(10,2) NOT NULL,
    payment_method ENUM('Cash on Delivery', 'Bank Transfer', 'Credit Card') DEFAULT 'Cash on Delivery'
);

CREATE TABLE IF NOT EXISTS Shipping (
    shipping_id      INT AUTO_INCREMENT PRIMARY KEY,
    order_id         INT          NOT NULL,
    tracking_number  VARCHAR(100) UNIQUE,
    courier_company VARCHAR(50)  DEFAULT 'TCS',
    shipping_status  ENUM('Preparing', 'Dispatched', 'In Transit', 'Delivered') DEFAULT 'Preparing',
    dispatch_date    DATE
);

SET FOREIGN_KEY_CHECKS = 1;


-- --------------------------------------------------------------------
-- 2. DML: COMPLETE MOCK DATA INSERTS
-- --------------------------------------------------------------------

-- Customers
INSERT INTO Customers (customer_id, name, email, phone, address) VALUES
(1, 'Ayesha Khan', 'ayesha.khan@email.com', '03001234567', 'House 12, Street 4, F-7/2, Islamabad'),
(2, 'Bilal Ahmed', 'bilal.ahmed@email.com', '03219876543', 'Flat 402, Pearl Heights, Clifton, Karachi'),
(3, 'Zainab Ali', 'zainab.ali@email.com', '03335554433', 'Plot 88, Phase 5, DHA, Lahore'),
(4, 'Hamza Malik', 'hamza.malik@email.com', '03451122334', 'House 5, Canal Bank Scheme, Lahore'),
(5, 'Sana Tariq', 'sana.tariq@email.com', '03129988776', 'Street 9, Sector G-11/3, Islamabad')
AS new_data
ON DUPLICATE KEY UPDATE name = new_data.name;

-- Products
INSERT INTO Products (product_id, name, material, price, stock_quantity) VALUES
(1, 'Royal Kundan Jhumkas', 'Gold Plated', 4500.00, 12),
(2, 'Zircon Tennis Bracelet', 'Sterling Silver', 8500.00, 4),
(3, 'Emerald Choker Set', 'Gold Plated', 15000.00, 2),
(4, 'Minimalist Pearl Ring', 'Sterling Silver', 2500.00, 0),
(5, 'Antique Bridal Mala', 'Brass/Gold Leaf', 22000.00, 5),
(6, 'Ruby Pendant Chain', 'Sterling Silver', 6200.00, 1)
AS new_data
ON DUPLICATE KEY UPDATE stock_quantity = new_data.stock_quantity;

-- Orders
INSERT INTO Orders (order_id, customer_id, order_date, total_amount, status, notes) VALUES
(101, 1, '2026-08-20', 4500.00, 'Delivered', 'Fragile packing requested'),
(102, 2, '2026-08-22', 17500.00, 'Shipped', 'Express dispatch'),
(103, 3, '2026-08-28', 2500.00, 'Pending', 'Call before delivery'),
(104, 4, '2026-08-30', 22000.00, 'Confirmed', 'Gift box requested'),
(105, 5, '2026-09-01', 6200.00, 'Pending', 'Urgent delivery')
AS new_data
ON DUPLICATE KEY UPDATE status = new_data.status;

-- Order Items
INSERT INTO Order_Items (item_id, order_id, product_id, quantity, unit_price) VALUES
(1, 101, 1, 1, 4500.00),
(2, 102, 2, 1, 8500.00),
(3, 102, 1, 2, 4500.00),
(4, 103, 4, 1, 2500.00),
(5, 104, 5, 1, 22000.00),
(6, 105, 6, 1, 6200.00)
AS new_data
ON DUPLICATE KEY UPDATE quantity = new_data.quantity;

-- Payments
INSERT INTO Payments (payment_id, order_id, payment_date, amount_paid, payment_method) VALUES
(1, 101, '2026-08-20', 4500.00, 'Bank Transfer'),
(2, 102, '2026-08-22', 17500.00, 'Credit Card'),
(3, 104, '2026-08-30', 22000.00, 'Bank Transfer')
AS new_data
ON DUPLICATE KEY UPDATE amount_paid = new_data.amount_paid;

-- Shipping
INSERT INTO Shipping (shipping_id, order_id, tracking_number, courier_company, shipping_status, dispatch_date) VALUES
(1, 101, 'TCS-9928311', 'TCS', 'Delivered', '2026-08-21'),
(2, 102, 'TCS-9928405', 'TCS', 'In Transit', '2026-08-23'),
(3, 104, 'M&P-441029', 'M&P', 'Preparing', NULL)
AS new_data
ON DUPLICATE KEY UPDATE shipping_status = new_data.shipping_status;

-- --------------------------------------------------------------------
-- 3. ADVANCED RELATIONAL CONSTRAINTS & INTEGRITY (CASCADE / RESTRICT / CHECK)
-- --------------------------------------------------------------------

-- Orders FK Rules (Protect profile deletions, sync ID updates)
ALTER TABLE Orders 
ADD CONSTRAINT fk_orders_customer 
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
    ON DELETE RESTRICT 
    ON UPDATE CASCADE;

-- Order Items FK Rules (Cascade on order deletion, block deletion of sold items)
ALTER TABLE Order_Items 
ADD CONSTRAINT fk_items_order 
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
    ON DELETE CASCADE,
ADD CONSTRAINT fk_items_product 
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
    ON DELETE RESTRICT;

-- Payments Constraints (Cascade on order deletion + non-negative amount check)
ALTER TABLE Payments 
ADD CONSTRAINT fk_payments_order 
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
    ON DELETE CASCADE,
ADD CONSTRAINT chk_positive_payment 
    CHECK (amount_paid >= 0);

-- Shipping FK Rules (Cascade shipping records on master order removal)
ALTER TABLE Shipping 
ADD CONSTRAINT fk_shipping_order 
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
    ON DELETE CASCADE;

-- Product Domain Safety Checks
ALTER TABLE Products
ADD CONSTRAINT chk_positive_price CHECK (price > 0),
ADD CONSTRAINT chk_non_negative_stock CHECK (stock_quantity >= 0);


-- --------------------------------------------------------------------
-- 4. PERFORMANCE INDEXING FOR STREAMLIT QUERY OPTIMIZATION
-- --------------------------------------------------------------------

CREATE INDEX idx_orders_status ON Orders(status);
CREATE INDEX idx_orders_date ON Orders(order_date);
CREATE INDEX idx_products_material ON Products(material);


-- --------------------------------------------------------------------
-- 5. OPERATIONAL MONITORING VIEW (REAL-TIME STREAMLIT ALERTS)
-- --------------------------------------------------------------------

CREATE OR REPLACE VIEW v_low_stock_alerts AS
SELECT 
    product_id, 
    name, 
    material, 
    stock_quantity,
    CASE 
        WHEN stock_quantity = 0 THEN 'SOLD OUT'
        ELSE 'LOW STOCK'
    END AS operational_status
FROM Products 
WHERE stock_quantity <= 5 
ORDER BY stock_quantity ASC;


-- --------------------------------------------------------------------
-- 6. AUTOMATION & BUSINESS LOGIC (TRIGGERS & PROCEDURES)
-- --------------------------------------------------------------------

-- TRIGGER: Guard inventory from dropping below zero during manual updates
DROP TRIGGER IF EXISTS trg_prevent_negative_stock_update;
DELIMITER $$
CREATE TRIGGER trg_prevent_negative_stock_update
BEFORE UPDATE ON Products FOR EACH ROW
BEGIN
    IF NEW.stock_quantity < 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Operation Denied: Stock level cannot drop below zero.';
    END IF;
END$$
DELIMITER ;

-- PROCEDURE: Secure, Atomic Order Checkout Engine
DROP PROCEDURE IF EXISTS sp_process_secure_checkout;
DELIMITER $$
CREATE PROCEDURE sp_process_secure_checkout(
    IN p_customer_id INT, 
    IN p_total_amount DECIMAL(10,2), 
    IN p_product_id INT, 
    IN p_quantity INT, 
    IN p_unit_price DECIMAL(10,2)
)
proc_label: BEGIN
    DECLARE v_current_stock INT; 
    DECLARE v_new_order_id INT;

    -- Exit Handler for unexpected SQL exceptions
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN 
        ROLLBACK; 
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transaction Aborted: DB Error Engine Triggers Rollback.'; 
    END;

    START TRANSACTION;

    -- Lock row for concurrency safety and fetch current stock
    SELECT stock_quantity INTO v_current_stock 
    FROM Products 
    WHERE product_id = p_product_id FOR UPDATE;

    -- Validate stock availability
    IF v_current_stock < p_quantity THEN 
        ROLLBACK; 
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transaction Denied: Insufficient stock.'; 
        LEAVE proc_label; 
    END IF;

    -- 1. Insert Master Order Record
    INSERT INTO Orders (customer_id, order_date, total_amount, status) 
    VALUES (p_customer_id, CURDATE(), p_total_amount, 'Pending');
    
    SET v_new_order_id = LAST_INSERT_ID();

    -- 2. Insert Order Item Breakout
    INSERT INTO Order_Items (order_id, product_id, quantity, unit_price) 
    VALUES (v_new_order_id, p_product_id, p_quantity, p_unit_price);

    -- 3. Atomic Inventory Deduction
    UPDATE Products 
    SET stock_quantity = stock_quantity - p_quantity 
    WHERE product_id = p_product_id;

    COMMIT;
END$$
DELIMITER ;



-- 7. EMPLOYEES / SYSTEM USERS (for login + role-based access in Streamlit)
-- --------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Employees (
    employee_id   INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('Admin', 'Sales', 'Inventory Manager') NOT NULL DEFAULT 'Sales',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Sample employees (passwords are placeholders — you'll hash real ones in Python, not store plain text)
INSERT INTO Employees (employee_id, name, username, password_hash, role) VALUES
(1, 'Fatima Noor', 'fatima.noor', 'PLACEHOLDER_HASH_1', 'Admin'),
(2, 'Ahmed Raza', 'ahmed.raza', 'PLACEHOLDER_HASH_2', 'Sales'),
(3, 'Mehak Siddiqui', 'mehak.siddiqui', 'PLACEHOLDER_HASH_3', 'Inventory Manager')
AS new_data
ON DUPLICATE KEY UPDATE role = new_data.role;


-- --------------------------------------------------------------------
-- 8. AUDIT LOG (tracks every stock change, and who/what caused it)
-- --------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Stock_Change_Log (
    log_id        INT AUTO_INCREMENT PRIMARY KEY,
    product_id    INT NOT NULL,
    old_quantity  INT NOT NULL,
    new_quantity  INT NOT NULL,
    change_reason VARCHAR(100),
    changed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS trg_log_stock_change;
DELIMITER $$
CREATE TRIGGER trg_log_stock_change
AFTER UPDATE ON Products FOR EACH ROW
BEGIN
    IF OLD.stock_quantity <> NEW.stock_quantity THEN
        INSERT INTO Stock_Change_Log (product_id, old_quantity, new_quantity, change_reason)
        VALUES (
            NEW.product_id,
            OLD.stock_quantity,
            NEW.stock_quantity,
            CASE
                WHEN NEW.stock_quantity < OLD.stock_quantity THEN 'Sale/Deduction'
                ELSE 'Restock'
            END
        );
    END IF;
END$$
DELIMITER ;
-- --------------------------------------------------------------------
-- 9. SMALL FIX: enforce positive quantity on Order_Items
-- --------------------------------------------------------------------
ALTER TABLE Order_Items
ADD CONSTRAINT chk_positive_quantity CHECK (quantity > 0);

-- --------------------------------------------------------------------
-- 10. TIMESTAMPS ON KEY TABLES (nice-to-have, shows "last updated")
-- --------------------------------------------------------------------

ALTER TABLE Orders
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

ALTER TABLE Products
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;


-- --------------------------------------------------------------------
-- 11. PRODUCT CATEGORY (better filtering + browsing in Streamlit)
-- --------------------------------------------------------------------

ALTER TABLE Products
ADD COLUMN category ENUM('Earrings', 'Bracelet', 'Choker', 'Ring', 'Chain', 'Bangles', 'Bridal Set', 'Necklace', 'Anklet')
    NOT NULL DEFAULT 'Earrings' AFTER name;

-- Backfill category for your existing 6 products
UPDATE Products SET category = 'Earrings'   WHERE product_id = 1;  -- Royal Kundan Jhumkas
UPDATE Products SET category = 'Bracelet'   WHERE product_id = 2;  -- Zircon Tennis Bracelet
UPDATE Products SET category = 'Choker'     WHERE product_id = 3;  -- Emerald Choker Set
UPDATE Products SET category = 'Ring'       WHERE product_id = 4;  -- Minimalist Pearl Ring
UPDATE Products SET category = 'Bridal Set' WHERE product_id = 5;  -- Antique Bridal Mala
UPDATE Products SET category = 'Chain'      WHERE product_id = 6;  -- Ruby Pendant Chain


-- --------------------------------------------------------------------
-- 12. EXPANDED PRODUCT CATALOG (realistic range for a jewellery shop)
-- --------------------------------------------------------------------

INSERT INTO Products (product_id, name, category, material, price, stock_quantity) VALUES
(7,  'Silver Hoop Earrings',        'Earrings',   'Sterling Silver', 1200.00, 30),
(8,  'Studded Cocktail Ring',       'Ring',       'Gold Plated',     3200.00, 18),
(9,  'Delicate Chain Bracelet',     'Bracelet',   'Sterling Silver', 1800.00, 25),
(10, 'Layered Pearl Necklace',      'Necklace',   'Gold Plated',     9500.00, 6),
(11, 'Kundan Bridal Choker Set',    'Bridal Set', 'Gold Plated',     28000.00, 3),
(12, 'Classic Gold Bangles (Set of 2)', 'Bangles','Gold Plated',    7400.00, 10),
(13, 'Minimalist Anklet',           'Anklet',     'Sterling Silver', 950.00,  40),
(14, 'Statement Jhumka Earrings',   'Earrings',   'Brass/Gold Leaf', 3800.00, 14),
(15, 'CZ Tennis Chain',             'Chain',      'Sterling Silver', 5600.00, 8),
(16, 'Everyday Stud Earrings',      'Earrings',   'Sterling Silver', 800.00,  50),
(17, 'Polki Choker Set',            'Choker',     'Gold Plated',     19500.00, 2),
(18, 'Charm Bracelet',              'Bracelet',   'Sterling Silver', 2100.00, 20),
(19, 'Solitaire Ring (CZ)',         'Ring',       'Sterling Silver', 4200.00, 0),
(20, 'Traditional Jhumar Set',      'Bridal Set', 'Gold Plated',     32000.00, 1),
(21, 'Rose Gold Bangles (Set of 4)','Bangles',    'Gold Plated',     11200.00, 7),
(22, 'Simple Pearl Studs',          'Earrings',   'Sterling Silver', 1100.00, 35),
(23, 'Long Chain with Pendant',     'Chain',      'Gold Plated',     6800.00, 5),
(24, 'Beaded Anklet',               'Anklet',     'Brass/Gold Leaf', 750.00,  22),
(25, 'Party Wear Necklace Set',     'Necklace',   'Gold Plated',     13500.00, 4),
(26, 'Stackable Rings (Set of 3)',  'Ring',       'Sterling Silver', 2600.00, 16)
AS new_data
ON DUPLICATE KEY UPDATE stock_quantity = new_data.stock_quantity, category = new_data.category;

-- ----------------------------------------------------------------------------------
-- Quesries for dashboard
-- ----------------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_revenue_summary AS
SELECT
    (SELECT SUM(amount_paid) FROM Payments) AS total_revenue,
    (SELECT COUNT(*) FROM Orders) AS total_orders,
    (SELECT COUNT(*) FROM Orders WHERE status = 'Pending') AS pending_orders,
    (SELECT COUNT(*) FROM Products WHERE stock_quantity = 0) AS sold_out_products,
    (SELECT COUNT(*) FROM Products WHERE stock_quantity BETWEEN 1 AND 5) AS low_stock_products;

-- Monthly revenue
CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT
    DATE_FORMAT(payment_date, '%Y-%m') AS month,
    SUM(amount_paid) AS revenue
FROM Payments
GROUP BY DATE_FORMAT(payment_date, '%Y-%m')
ORDER BY month;

-- Top products
CREATE OR REPLACE VIEW v_top_products AS
SELECT
    p.product_id,
    p.name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.unit_price) AS revenue_generated
FROM Order_Items oi
JOIN Products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY revenue_generated DESC;

-- Indexes for searching
CREATE INDEX idx_customers_name ON Customers(name);
CREATE INDEX idx_products_name ON Products(name);
CREATE INDEX idx_customers_email ON Customers(email);


