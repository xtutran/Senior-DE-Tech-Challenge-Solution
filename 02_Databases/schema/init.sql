CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- TABLES --
CREATE TABLE IF NOT EXISTS members (
  id TEXT NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email TEXT NOT NULL UNIQUE,
  mobile INT NOT NULL,
  date_of_birth TIMESTAMPTZ NOT NULL,
  approved BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS items (
  id UUID NOT NULL DEFAULT uuid_generate_v4(),
  item_name VARCHAR(255) NOT NULL,
  manufacture_name VARCHAR(255),
  cost NUMERIC NOT NULL DEFAULT 0,
  weight_kg NUMERIC DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS orders (
  id UUID NOT NULL DEFAULT uuid_generate_v4(),
  member_id TEXT REFERENCES members(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status TEXT,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS order_items (
  id UUID NOT NULL DEFAULT uuid_generate_v4(),
  item_id UUID REFERENCES items(id),
  order_id UUID REFERENCES orders(id),
  total_items_price NUMERIC NOT NULL,
  total_items_weight NUMERIC NOT NULL,
  PRIMARY KEY (id)
);

-- INDEXES --
-- members
CREATE INDEX idx_member_email ON members(email);
-- orders
CREATE INDEX idx_order_member_id ON orders(member_id);
-- order_items
CREATE INDEX idx_item_id_order_item ON order_items(item_id);
CREATE INDEX idx_order_id_order_item ON order_items(order_id);