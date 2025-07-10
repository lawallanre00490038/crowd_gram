-- 1. Create a user (you can change 'lanre' and password if you like)
CREATE USER lawal WITH PASSWORD 'lawal';

-- 2. Create a database for your chatbot
CREATE DATABASE dkt_chatbot;

-- 3. Grant all access to the new user
GRANT ALL PRIVILEGES ON DATABASE dkt_chatbot TO lawal;



-- Grant usage and create privileges on the public schema to the user
GRANT USAGE ON SCHEMA public TO lawal;
GRANT CREATE ON SCHEMA public TO lawal;

-- Optional: Make sure lawal can also read/write tables in the schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO lawal;





-- psql -U postgres -h localhost -f init_db.sql