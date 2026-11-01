
-- The Choice
-- PostgreSQL database schema, version 1

-- ==========================================
-- 1. PROPHECIES
-- ==========================================

CREATE TABLE prophecies (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    title VARCHAR(120) NOT NULL,
    message TEXT NOT NULL
);

-- ==========================================
-- 2. QUESTIONS
-- ==========================================

CREATE TABLE questions (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    question_text TEXT NOT NULL,
    is_start BOOLEAN NOT NULL DEFAULT FALSE
);

-- Only one question can be the starting question.
CREATE UNIQUE INDEX idx_one_starting_question
    ON questions (is_start)
    WHERE is_start = TRUE;

-- ==========================================
-- 3. OPTIONS
-- ==========================================

CREATE TABLE options (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    question_id INTEGER NOT NULL,
    code VARCHAR(10) NOT NULL,
    option_text TEXT NOT NULL,
    next_question_id INTEGER,
    display_order SMALLINT NOT NULL,

    CONSTRAINT fk_option_question
        FOREIGN KEY (question_id)
        REFERENCES questions (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_next_question
        FOREIGN KEY (next_question_id)
        REFERENCES questions (id),

    CONSTRAINT uq_question_option_code
        UNIQUE (question_id, code),

    -- Allows responses to verify that their selected
    -- option belongs to the question they answered.
    CONSTRAINT uq_question_option_id
        UNIQUE (question_id, id),

    CONSTRAINT uq_question_display_order
        UNIQUE (question_id, display_order),

    CONSTRAINT chk_display_order
        CHECK (display_order > 0)
);

-- ==========================================
-- 4. JOURNEYS
-- ==========================================

CREATE TABLE journeys (
    id UUID PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    path_signature VARCHAR(3),
    prophecy_id INTEGER,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    CONSTRAINT fk_journey_prophecy
        FOREIGN KEY (prophecy_id)
        REFERENCES prophecies (id),

    CONSTRAINT chk_journey_status
        CHECK (status IN ('in_progress', 'completed')),

    -- Allows partial signatures during a journey:
    -- NULL, R, B, R1, B2, etc.
    CONSTRAINT chk_path_signature
        CHECK (
            path_signature IS NULL
            OR path_signature ~ '^[RB]([12]){0,2}$'
        ),

    -- Incomplete journeys cannot have a final prophecy.
    -- Completed journeys must have all completion details.
    CONSTRAINT chk_journey_completion
        CHECK (
            (
                status = 'in_progress'
                AND (
                    path_signature IS NULL
                    OR path_signature ~ '^[RB]([12])?$'
                )
                AND prophecy_id IS NULL
                AND completed_at IS NULL
            )
            OR
            (
                status = 'completed'
                AND path_signature IS NOT NULL
                AND path_signature ~ '^[RB][12][12]$'
                AND prophecy_id IS NOT NULL
                AND completed_at IS NOT NULL
            )
        )
);

-- ==========================================
-- 5. RESPONSES
-- ==========================================

CREATE TABLE responses (
    journey_id UUID NOT NULL,
    question_id INTEGER NOT NULL,
    option_id INTEGER NOT NULL,
    response_order SMALLINT NOT NULL,
    answered_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (journey_id, question_id),

    CONSTRAINT fk_response_journey
        FOREIGN KEY (journey_id)
        REFERENCES journeys (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_response_option
        FOREIGN KEY (question_id, option_id)
        REFERENCES options (question_id, id),

    -- A journey cannot submit two answers at the same step.
    CONSTRAINT uq_journey_response_order
        UNIQUE (journey_id, response_order),

    CONSTRAINT chk_response_order
        CHECK (response_order BETWEEN 1 AND 3)
);

-- Useful for aggregating statistics by question and option.
CREATE INDEX idx_responses_question_option
    ON responses (question_id, option_id);

-- ==========================================
-- 6. PROPHECY ROUTES
-- ==========================================

CREATE TABLE prophecy_routes (
    path_signature VARCHAR(3) PRIMARY KEY,
    prophecy_id INTEGER NOT NULL,

    CONSTRAINT fk_route_prophecy
        FOREIGN KEY (prophecy_id)
        REFERENCES prophecies (id),

    CONSTRAINT chk_route_signature
        CHECK (path_signature ~ '^[RB][12][12]$')
);

-- ==========================================
-- END OF SCHEMA
-- ==========================================
