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
        "ACROSS_DB_PORT": "5432",
        "ACROSS_DB_ROLE": "aws-developer-role",
        "ACROSS_DB_DEBUG": "False",
        "ACROSS_ADMIN_TOKEN": "admin-token-local",
        "ACROSS_EMAIL": "nasa.across.dev@gmail.com",
        "ACROSS_EMAIL_PASSWORD": "acrossemailpassword",
        "ACROSS_EMAIL_HOST": "smtp.gmail.com",
        "ACROSS_EMAIL_PORT": "465",
        "SPACETRACK_USER": "spacetrack_user",
        "SPACETRACK_PWD": "spacetrackpassword",
        "ACROSS_DEBUG": True,
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
