-- Step 1: Create a trigger function
CREATE OR REPLACE FUNCTION create_impulse_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO ImpulseUser (auth_id)
    VALUES (NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 2: Create a trigger that calls the trigger function after insert on the 'users' table
CREATE TRIGGER create_impulse_user_trigger
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION create_impulse_user();
