CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    email character varying UNIQUE NOT NULL,
    created_at timestamp(6) without time zone DEFAULT now() NOT NULL,
    updated_at timestamp(6) without time zone DEFAULT now() NOT NULL,
    name text,
    default_graph character varying,
    target_profile_id integer
);


CREATE TABLE public.courses (
    id SERIAL PRIMARY KEY,
    name character varying,
    certificate character varying,
    type character varying,
    provider character varying,
    platform character varying,
    duration character varying,
    url character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_at timestamp without time zone DEFAULT now() NOT NULL,
    duration_code character varying,
    free character varying,
    specialisation character varying,
    start character varying,
    type2 character varying,
    alt_id text,
    description text,
    short_description text,
    tag text,
    weekly_effort double precision
);


CREATE TABLE public.organisations (
    id SERIAL PRIMARY KEY,
    created_at timestamp(6) without time zone DEFAULT now() NOT NULL,
    updated_at timestamp(6) without time zone DEFAULT now() NOT NULL,
    name text,
    tag text,
    graph character varying
);


CREATE TABLE public.skills (
    id SERIAL PRIMARY KEY,
    name character varying,
    adder character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_at timestamp without time zone DEFAULT now() NOT NULL,
    description character varying,
    tag character varying,
    alt_id text,
    to_tag boolean,
    path_from_root jsonb,
    depth integer,
    text_path text,
    search_tag text,
    depths json,
    to_delete boolean,
    dataset character varying,
    graph character varying,
    ml_description character varying,
    n_below integer,
    personal boolean DEFAULT false,
    user_id integer,
    path_text jsonb
);


CREATE TABLE public.graphs (
    id SERIAL PRIMARY KEY,
    created_at timestamp(6) without time zone DEFAULT now() NOT NULL,
    updated_at timestamp(6) without time zone DEFAULT now() NOT NULL,
    graph_tag character varying,
    name character varying,
    description character varying,
    root_id integer,
    FOREIGN KEY (root_id) REFERENCES skills (id)
);


CREATE TABLE public.course_scores (
    id SERIAL PRIMARY KEY,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now()NOT NULL,
    course_id integer,
    skill_id integer,
    score double precision,
    score_type text,
    FOREIGN KEY (course_id) REFERENCES courses (id),
    FOREIGN KEY (skill_id) REFERENCES skills (id)
);


CREATE TABLE public.profiles (
    id SERIAL PRIMARY KEY,
    name character varying,
    user_id integer,
    tag character varying,
    dataset character varying,
    graph character varying,
    kind character varying,
    FOREIGN KEY (user_id) REFERENCES users (id)
);


CREATE TABLE public.competences (
    id SERIAL PRIMARY KEY,
    level character varying,
    code integer,
    skill_id integer,
    profile_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_at timestamp without time zone DEFAULT now() NOT NULL,
    focused boolean DEFAULT false,
    FOREIGN KEY (skill_id) REFERENCES skills (id),
    FOREIGN KEY (profile_id) REFERENCES profiles (id)
);



CREATE TABLE public.members (
    id SERIAL PRIMARY KEY,
    created_at timestamp(6) without time zone DEFAULT now() NOT NULL,
    updated_at timestamp(6) without time zone DEFAULT now() NOT NULL,
    user_id bigint,
    organisation_id bigint,
    role text,
    target_profile integer,
    budget integer,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (organisation_id) REFERENCES organisations (id)
);


CREATE TABLE public.skill_includes (
    id SERIAL PRIMARY KEY,
    subject_id integer,
    object_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    modified_at timestamp without time zone DEFAULT now() NOT NULL,
    tag text,
    user_id integer,
    stage character varying,
    personal boolean DEFAULT false,
    FOREIGN KEY (subject_id) REFERENCES skills (id),
    FOREIGN KEY (object_id) REFERENCES skills (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE INDEX index_course_scores_on_course_id ON public.course_scores USING btree (course_id);

CREATE INDEX index_course_scores_on_skill_id ON public.course_scores USING btree (skill_id);
