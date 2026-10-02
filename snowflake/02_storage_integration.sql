USE ROLE ACCOUNTADMIN;

-- create integration between aws and snowflake
CREATE OR REPLACE STORAGE INTEGRATION ZOMATO_S3_INT
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = 'S3'
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::968579693494:role/snowflake-s3-role'
    STORAGE_ALLOWED_LOCATIONS = ('s3://zomato-pipeline-dev-rozie/');
    -- least priviledge access (PoLP: Principle of Least Privilege) a principle that give the access into a user in very lowest format.

GRANT USAGE ON INTEGRATION ZOMATO_S3_INT TO ROLE DBT_ROLE;

DESC INTEGRATION ZOMATO_S3_INT;
