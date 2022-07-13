--
-- PostgreSQL database dump
--

-- Dumped from database version 14.2
-- Dumped by pg_dump version 14.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: gender; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.gender AS ENUM (
    'MALE',
    'FEMALE'
);


ALTER TYPE public.gender OWNER TO postgres;

--
-- Name: role; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.role AS ENUM (
    'SUPERVISOR',
    'VOLUNTEER'
);


ALTER TYPE public.role OWNER TO postgres;

--
-- Name: status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.status AS ENUM (
    'ACTIVE',
    'INACTIVE'
);


ALTER TYPE public.status OWNER TO postgres;

--
-- Name: add_again_a_softdelted_sub(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.add_again_a_softdelted_sub() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        DECLARE
		rec RECORD;
        BEGIN
		-- Storing new record
                SELECT * FROM subscribers
		INTO rec
		WHERE id = NEW.id;

                IF FOUND THEN
			IF (rec.status = 'INACTIVE') THEN
	 			UPDATE subscribers SET
				first_name = NEW.first_name, second_name=NEW.second_name,
				first_lastname = NEW.first_lastname, second_lastname = NEW.second_lastname,
				adress = NEW.adress, phone_number = NEW.phone_number, gender = NEW.gender,
				status = 'ACTIVE'
				WHERE id = NEW.id;
				--Updating info and setting ACTIVE as status for
				--already seen subscriber

				RETURN NULL; -- Aborting operation
			ELSE
				-- This is NOT an UPDATE statement, will only work
				-- if the user was 'softdeleted'
				RAISE EXCEPTION 
				'Subscriber with id % is already registered and its status is ACTIVE', NEW.id;
			END IF;
                       
                ELSE
                        NEW.status := 'ACTIVE'; -- Ensure new record is added marked as active
                        RETURN NEW;

                END IF;
        END;
$$;


ALTER FUNCTION public.add_again_a_softdelted_sub() OWNER TO postgres;

--
-- Name: add_again_softdeleted_book(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.add_again_softdeleted_book() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        DECLARE 
                rec RECORD;
        BEGIN   
                SELECT * FROM books
                INTO rec
                WHERE book_name ILIKE NEW.book_name;
                -- User tried to add book with same name (already registered book)
                  
                IF FOUND THEN
                        IF (rec.available = FALSE) THEN
				UPDATE books SET
				shelf_row_num = NEW.shelf_row_num,
				category_id = NEW.category_id,
				author_id = NEW.author_id,
				available = TRUE
				WHERE id = rec.id;

				RETURN NULL;
			ELSE
				RAISE EXCEPTION 
				'Book with name % is already registered and is still available.', NEW.book_name;
			END IF;
		ELSE
			NEW.available := TRUE;
			RETURN NEW;
		END IF;

	END;
$$;


ALTER FUNCTION public.add_again_softdeleted_book() OWNER TO postgres;

--
-- Name: set_book_availability_false(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.set_book_availability_false() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
		UPDATE books SET available = FALSE
		WHERE id = OLD.id;

		RETURN NULL;
	END;

$$;


ALTER FUNCTION public.set_book_availability_false() OWNER TO postgres;

--
-- Name: set_loan_returned_true(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.set_loan_returned_true() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 
                BEGIN 
                        UPDATE book_loans 
                        SET already_returned = TRUE 
                        WHERE id = OLD.id; 
                        RETURN NULL; 
                END; 
        $$;


ALTER FUNCTION public.set_loan_returned_true() OWNER TO postgres;

--
-- Name: set_subscriber_to_inactive(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.set_subscriber_to_inactive() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
           BEGIN
                   UPDATE subscribers SET status='INACTIVE'
                   WHERE id=OLD.id;
                   
                   RETURN NULL;
           END;    
$$;


ALTER FUNCTION public.set_subscriber_to_inactive() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: author_countries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.author_countries (
    id integer NOT NULL,
    country_name character varying(20) NOT NULL
);


ALTER TABLE public.author_countries OWNER TO postgres;

--
-- Name: authors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.authors (
    id integer NOT NULL,
    first_name character varying(20) NOT NULL,
    second_name character varying(20),
    first_lastname character varying(20) NOT NULL,
    second_lastname character varying(20) NOT NULL,
    gender public.gender NOT NULL,
    country_id integer NOT NULL
);


ALTER TABLE public.authors OWNER TO postgres;

--
-- Name: all_authors_info; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.all_authors_info AS
 SELECT authors.id,
    authors.first_name,
    authors.second_name,
    authors.first_lastname,
    authors.second_lastname,
    authors.gender,
    author_countries.country_name AS country
   FROM (public.authors
     JOIN public.author_countries ON ((authors.country_id = author_countries.id)));


ALTER TABLE public.all_authors_info OWNER TO postgres;

--
-- Name: books; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.books (
    id integer NOT NULL,
    book_name character varying(20) NOT NULL,
    shelf_row_num integer NOT NULL,
    category_id integer NOT NULL,
    author_id integer NOT NULL,
    available boolean DEFAULT true NOT NULL,
    CONSTRAINT shelf_row_lte_10 CHECK (((shelf_row_num > 0) AND (shelf_row_num <= 10)))
);


ALTER TABLE public.books OWNER TO postgres;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    category_name character varying(20) NOT NULL,
    floor integer NOT NULL,
    shelf_number integer NOT NULL,
    CONSTRAINT floor_lte_2 CHECK (((floor > 0) AND (floor <= 2))),
    CONSTRAINT shelf_lte_10 CHECK (((shelf_number > 0) AND (shelf_number <= 10)))
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- Name: all_books_info; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.all_books_info AS
 SELECT books.id,
    books.book_name,
    categories.category_name AS category,
    books.available,
    authors.id AS author_id,
    authors.first_name AS author_first_name,
    authors.second_name AS author_second_name,
    authors.first_lastname AS author_first_lastname,
    authors.second_lastname AS author_second_lastname,
    authors.gender AS author_gender,
    author_countries.country_name AS author_country,
    categories.floor,
    categories.shelf_number,
    books.shelf_row_num
   FROM (((public.books
     JOIN public.categories ON ((books.category_id = categories.id)))
     JOIN public.authors ON ((books.author_id = authors.id)))
     JOIN public.author_countries ON ((authors.country_id = author_countries.id)));


ALTER TABLE public.all_books_info OWNER TO postgres;

--
-- Name: author_countries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.author_countries ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.author_countries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: authors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.authors ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.authors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: book_loans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.book_loans (
    id integer NOT NULL,
    loan_date date DEFAULT now() NOT NULL,
    loan_exp_date date NOT NULL,
    subscriber_id integer NOT NULL,
    book_id integer NOT NULL,
    already_returned boolean DEFAULT false NOT NULL,
    CONSTRAINT loan_period_lte_month CHECK (((loan_exp_date > loan_date) AND (loan_exp_date <= (loan_date + '1 mon'::interval))))
);


ALTER TABLE public.book_loans OWNER TO postgres;

--
-- Name: book_loans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.book_loans ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.book_loans_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: books_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.books ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.books_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.categories ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: librarians; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.librarians (
    id integer NOT NULL,
    first_name character varying(20) NOT NULL,
    second_name character varying(20),
    first_lastname character varying(20) NOT NULL,
    second_lastname character varying(20) NOT NULL,
    role public.role NOT NULL,
    access_password text NOT NULL
);


ALTER TABLE public.librarians OWNER TO postgres;

--
-- Name: subscribers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscribers (
    id integer NOT NULL,
    first_name character varying(20) NOT NULL,
    second_name character varying(20),
    first_lastname character varying(20) NOT NULL,
    second_lastname character varying(20) NOT NULL,
    adress character varying(50) NOT NULL,
    gender public.gender NOT NULL,
    status public.status DEFAULT 'ACTIVE'::public.status NOT NULL,
    phone_number character(10) NOT NULL
);


ALTER TABLE public.subscribers OWNER TO postgres;

--
-- Name: author_countries author_countries_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.author_countries
    ADD CONSTRAINT author_countries_pk PRIMARY KEY (id);


--
-- Name: authors authors_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.authors
    ADD CONSTRAINT authors_pk PRIMARY KEY (id);


--
-- Name: books books_book_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_book_name_key UNIQUE (book_name);


--
-- Name: books books_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_pk PRIMARY KEY (id);


--
-- Name: categories categories_category_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_category_name_key UNIQUE (category_name);


--
-- Name: categories categories_floor_shelf_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_floor_shelf_number_key UNIQUE (floor, shelf_number);


--
-- Name: categories categories_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pk PRIMARY KEY (id);


--
-- Name: author_countries country_name_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.author_countries
    ADD CONSTRAINT country_name_unique UNIQUE (country_name);


--
-- Name: librarians librarians_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.librarians
    ADD CONSTRAINT librarians_pkey PRIMARY KEY (id);


--
-- Name: book_loans loans_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_loans
    ADD CONSTRAINT loans_pk PRIMARY KEY (id);


--
-- Name: subscribers phone_num_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscribers
    ADD CONSTRAINT phone_num_unique UNIQUE (phone_number);


--
-- Name: subscribers subscribers_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscribers
    ADD CONSTRAINT subscribers_pk PRIMARY KEY (id);


--
-- Name: books books_soft_deletes; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER books_soft_deletes BEFORE DELETE ON public.books FOR EACH ROW EXECUTE FUNCTION public.set_book_availability_false();


--
-- Name: books insert_softdeleted_book; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER insert_softdeleted_book BEFORE INSERT ON public.books FOR EACH ROW EXECUTE FUNCTION public.add_again_softdeleted_book();


--
-- Name: subscribers insert_softdeleted_user; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER insert_softdeleted_user BEFORE INSERT ON public.subscribers FOR EACH ROW EXECUTE FUNCTION public.add_again_a_softdelted_sub();


--
-- Name: book_loans loans_soft_deletes; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER loans_soft_deletes BEFORE DELETE ON public.book_loans FOR EACH ROW EXECUTE FUNCTION public.set_loan_returned_true();


--
-- Name: subscribers subscribers_soft_deletes; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER subscribers_soft_deletes BEFORE DELETE ON public.subscribers FOR EACH ROW EXECUTE FUNCTION public.set_subscriber_to_inactive();


--
-- Name: books authors_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT authors_fk FOREIGN KEY (author_id) REFERENCES public.authors(id) ON DELETE RESTRICT;


--
-- Name: book_loans book_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_loans
    ADD CONSTRAINT book_fk FOREIGN KEY (book_id) REFERENCES public.books(id) ON DELETE CASCADE;


--
-- Name: books category_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT category_fk FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE RESTRICT;


--
-- Name: authors country_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.authors
    ADD CONSTRAINT country_fk FOREIGN KEY (country_id) REFERENCES public.author_countries(id) ON DELETE RESTRICT;


--
-- Name: book_loans subscriber_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book_loans
    ADD CONSTRAINT subscriber_fk FOREIGN KEY (subscriber_id) REFERENCES public.subscribers(id);


--
-- PostgreSQL database dump complete
--

