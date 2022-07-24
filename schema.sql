CREATE TABLE IF NOT EXISTS guilds (
    guild_id BIGINT PRIMARY KEY,
    moderator_roles BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    moderator_users BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    admin_roles BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    admin_users BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[]
);

CREATE TABLE IF NOT EXISTS counting_config (
    guild_id BIGINT PRIMARY KEY
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    channel_id BIGINT,
    lives INT,
    blacklisted_users BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    blacklisted_roles BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    num BIGINT DEFAULT 0,
    user_id BIGINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS levelling_config (
    guild_id BIGINT PRIMARY KEY
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    announce_channel BIGINT,
    xp_modifier FLOAT NOT NULL DEFAULT 1.0,
    blacklisted_roles BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    blacklisted_channels BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    card_background BYTEA,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    levelup_messages TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[]
);

CREATE TABLE IF NOT EXISTS levelling_rewards (
    reward_id BIGSERIAL,
    guild_id BIGINT
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    level INT NOT NULL,
    role BIGINT,
    PRIMARY KEY (guild_id, role)
);

CREATE TABLE IF NOT EXISTS levelling_users (
    user_id BIGINT PRIMARY KEY,
    guild_id BIGINT NOT NULL
        REFERENCES levelling_config(guild_id)
            ON DELETE CASCADE,
    xp BIGINT NOT NULL DEFAULT 0,
    level INT NOT NULL DEFAULT 0,
    rewards_earned BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[]
);

CREATE TABLE IF NOT EXISTS currency_config (
    guild_id BIGINT PRIMARY KEY
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    channel_id BIGINT NOT NULL,
    blacklisted_channels BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    blacklisted_roles BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    bank_limit BIGINT
);

CREATE TABLE IF NOT EXISTS shop (
    item_id BIGSERIAL NOT NULL UNIQUE,
    guild_id BIGINT
        REFERENCES currency_config(guild_id)
            ON DELETE CASCADE,
    name TEXT NOT NULL UNIQUE,
    price BIGINT NOT NULL,
    reward_role BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS currency_users (
    user_id  BIGINT,
    guild_id BIGINT NOT NULL
        REFERENCES currency_config (guild_id)
            ON DELETE CASCADE,
    wallet BIGINT NOT NULL DEFAULT 0,
    bank BIGINT NOT NULL DEFAULT 0,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (user_id, guild_id)
);

CREATE TABLE IF NOT EXISTS inventory (
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    item_id BIGINT NOT NULL
        REFERENCES shop(item_id)
            ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 1,
    PRIMARY KEY (user_id, guild_id, item_id),
    CONSTRAINT inv_u_g_fk
        FOREIGN KEY (user_id, guild_id)
            REFERENCES currency_users(user_id, guild_id)
                ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS suggestions (
    suggestion_id BIGSERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    channel_id BIGINT NOT NULL,
        -- for fetching message purposes in case
        -- guilds(suggestions_channel_id) is deleted.
    user_id BIGINT NOT NULL,
    suggestion TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    up_voters BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    down_voters BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[]
);

CREATE TABLE IF NOT EXISTS ticket_panels (
    panel_id BIGSERIAL PRIMARY KEY,
    guild_id BIGINT
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    category BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    mod_roles BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[]
);

CREATE TABLE IF NOT EXISTS tickets (
    guild_id BIGINT NOT NULL
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    channel_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (guild_id, channel_id)
);

CREATE TABLE IF NOT EXISTS serverstats (
    guild_id BIGINT
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    time_channel BIGINT,
    timezone TEXT,
    membercount_channel BIGINT,
    channels_channel BIGINT,
    status_channel BIGINT,
    milestone_channel BIGINT,
    milestone BIGINT
);

CREATE TABLE IF NOT EXISTS modmail_config (
    guild_id BIGINT PRIMARY KEY
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    category BIGINT,
    whitelist_roles BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    whitelist_members BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    on_create_pings BOOL NOT NULL DEFAULT FALSE,
    on_message_pings BOOL NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS log_config (
    guild_id BIGINT PRIMARY KEY
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    guild_logs BIGINT,
    message_logs BIGINT,
    user_logs BIGINT,
    moderation_logs BIGINT,
    voice_logs BIGINT,
    member_logs BIGINT,
    join_logs BIGINT
);

CREATE TABLE IF NOT EXISTS custom_commands (
    guild_id BIGINT NOT NULL
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    command_name TEXT NOT NULL,
    command_text TEXT NOT NULL,
    command_creator BIGINT NOT NULL,
    created_at BIGINT NOT NULL,
    PRIMARY KEY (guild_id, command_name)
);

CREATE TABLE IF NOT EXISTS disabled_commands (
    guild_id BIGINT NOT NULL
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    command_name TEXT NOT NULL,
    whitelist_users BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    whitelist_roles BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    PRIMARY KEY (guild_id, command_name)
);

CREATE TABLE IF NOT EXISTS cases (
    case_id BIGSERIAL NOT NULL UNIQUE,
    case_type TEXT NOT NULL,
    guild_id BIGINT NOT NULL
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    moderator_id BIGINT NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    last_updated TIMESTAMP WITHOUT TIME ZONE,
    expires TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS commands(
    user_id bigint NOT NULL,
    command_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS emotion(
    user_id bigint NOT NULL,
    action_name text NOT NULL
);

CREATE TABLE IF NOT EXISTS marriages(
    user_one bigint NOT NULL,
    user_two bigint NOT NULL
);

-- LISTENERS
CREATE OR REPLACE FUNCTION update_guild_staff_cache()
  RETURNS TRIGGER AS $$
  BEGIN
    IF TG_OP = 'DELETE' THEN
      PERFORM pg_notify('delete_everything', OLD.guild_id::TEXT);
    ELSEIF TG_OP = 'UPDATE' THEN
        IF old.moderator_roles <> new.moderator_roles THEN
          PERFORM pg_notify('update_moderator_roles',
            JSON_BUILD_OBJECT(
                  'guild_id', NEW.guild_id,
                  'ids', NEW.moderator_roles
                )::TEXT
              );
        END IF;
        IF old.moderator_users <> new.moderator_users THEN
          PERFORM pg_notify('update_moderator_users',
            JSON_BUILD_OBJECT(
                  'guild_id', NEW.guild_id,
                  'ids', NEW.moderator_users
                )::TEXT
              );
        END IF;
        IF old.admin_roles <> new.admin_roles THEN
          PERFORM pg_notify('update_admin_roles',
            JSON_BUILD_OBJECT(
                  'guild_id', NEW.guild_id,
                  'ids', NEW.admin_roles
                )::TEXT
              );
        END IF;
        IF old.admin_users <> new.admin_users THEN
          PERFORM pg_notify('update_admin_users',
            JSON_BUILD_OBJECT(
                  'guild_id', NEW.guild_id,
                  'ids', NEW.admin_users
                )::TEXT
              );
        END IF;
    ELSE
      PERFORM pg_notify('insert_everything', NEW.guild_id::TEXT);
    END IF;
    RETURN NEW;
  END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_guild_staff_cache_trigger ON guilds;
CREATE TRIGGER update_guild_staff_cache_trigger
  AFTER INSERT OR UPDATE OR DELETE
  ON guilds
  FOR EACH ROW
  EXECUTE PROCEDURE update_guild_staff_cache();


CREATE TABLE IF NOT EXISTS ticketpanels(
    guild_id BIGINT
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    panel_name TEXT NOT NULL,
    ticket_category BIGINT NOT NULL,
    message_content TEXT,
    message_id BIGINT,
    views JSONB[] NOT NULL DEFAULT ARRAY[]::JSONB[], -- Whitelisted Roles, Custom ID, Label, Emoji etc
    PRIMARY KEY (guild_id, panel_name)
);

CREATE TABLE IF NOT EXISTS ticketpanelembeds(
    guild_id BIGINT,
    panel_name TEXT,
    embed_description TEXT,
    embed_colour BIGINT,
    embed_thumbnail TEXT,
    embed_image TEXT,
    FOREIGN KEY (guild_id, panel_name) REFERENCES ticketpanels (guild_id, panel_name)
);

CREATE TABLE IF NOT EXISTS tickets(
    guild_id BIGINT
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    channel_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (guild_id, channel_id)
);