-- this is for clouds which don't support db-specific users in terraform
-- set password manually too with \password using $prod_POSTGRES_PASSWORD
create user taskinbox;
grant connect on database taskinbox to taskinbox;
\c taskinbox
grant all privileges on all tables in schema public to taskinbox;
