-- ===========================================================================
-- URL:          http://arsvincere.com
-- AUTHOR:       Alex Avin
-- E-MAIL:       mr.alexavin@gmail.com
-- LICENSE:      GNU GPLv3
-- ===========================================================================

CREATE SCHEMA IF NOT EXISTS analytic -- {{{
    AUTHORIZATION pg_database_owner;
COMMENT ON SCHEMA analytic
    IS 'analytic data';
-- }}}

CREATE TYPE "Size" AS ENUM (--{{{
    'BLACKSWAN_SMALL',
    'GREATEST_SMALL',
    'ANOMAL_SMALL',
    'EXTRA_SMALL',
    'VERY_SMALL',
    'SMALLEST',
    'SMALLER',
    'SMALL',
    'NORMAL',
    'BIG',
    'BIGGER',
    'BIGGEST',
    'VERY_BIG',
    'EXTRA_BIG',
    'ANOMAL_BIG',
    'GREATEST_BIG',
    'BLACKSWAN_BIG'
    );
--}}}
CREATE TYPE "SimpleSize" AS ENUM (--{{{
    'XXS',
    'XS',
    'S',
    'M',
    'L',
    'XL',
    'XXL'
    );
--}}}
CREATE TYPE "Term" AS ENUM (--{{{
    'ST', 'MT', 'LT'
    );
--}}}
CREATE TYPE "Trend.Type" AS ENUM (--{{{
    'BEAR', 'BULL'
    );
--}}}
CREATE TYPE "Trend.Trait" AS ENUM (--{{{
    'TYPE', 'PERIOD', 'DELTA', 'SPEED', 'VOLUME'
    );
--}}}

CREATE TABLE IF NOT EXISTS analytic."Trend" ( -- {{{
    figi text
        REFERENCES "Asset"(figi),
    timeframe "TimeFrame" NOT NULL,
    term "Term" NOT NULL,
    type "Trend.Type" NOT NULL,
    period integer NOT NULL,
    delta float NOT NULL,
    speed float NOT NULL,
    volume bigint NOT NULL,

    period_size "Size",
    delta_size "Size",
    speed_size "Size",
    volume_size "Size",

    period_ss "SimpleSize",
    delta_ss "SimpleSize",
    speed_ss "SimpleSize",
    volume_ss "SimpleSize"
    );
-- }}}

