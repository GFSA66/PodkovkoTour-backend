CREATE USER tour_admin WITH PASSWORD 'tour_admin';
CREATE DATABASE tour_agency OWNER tour_admin;
GRANT ALL PRIVILEGES ON DATABASE tour_agency TO tour_admin;