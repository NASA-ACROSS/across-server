import os


def create_env_file() -> None:
    env_file_path = ".env"

    env_vars = {
        "APP_ENV": "across-plat-lcl-local",
        "RUNTIME_ENV": "local",
        "ACROSS_DB_USER": "admin",
        "HOST": "http://localhost",
        "FRONTEND_HOST": "http://localhost:5173",
        "ACROSS_DB_PWD": "local",
        "ACROSS_DB_NAME": "across",
        "ACROSS_DB_HOST": "localhost",
        "ACROSS_DB_PORT": 5432,
        "ACROSS_DB_ROLE": "aws-developer-role",
        "ACROSS_DB_DEBUG": False,
        "ACROSS_ADMIN_TOKEN": "admin-token-local",
        "ACROSS_EMAIL": "gsfc-across-no-reply@mail.nasa.gov",
        "ACROSS_DEBUG": True,
        "HIDE_LOCAL_ROUTE": False,
        "AWS_SES_REGION": "us-east-1",
        "AWS_SES_SOURCE_ARN": "arn:aws:ses:us-east-1:866324986652:identity/nasa.gov",
        "AWS_SES_CONFIGURATION_SET": "across-no-reply-config-set",
        "ACROSS_EMAIL": "gsfc-across-no-reply@mail.nasa.gov",
        "RESTRICTED_TO_EMAIL_LIST": "",
        "ALLOWED_TOP_LEVEL_DOMAINS": "",
    }

    if not os.path.exists(env_file_path):
        with open(env_file_path, "w") as env_file:
            for key, value in env_vars.items():
                env_file.write(f"{key}={value}\n")
        print(f"Created '{env_file_path}'.")
    else:
        print(f"{env_file_path} already exists.")


if __name__ == "__main__":
    create_env_file()
