# Chicago Array of Things Build: Data Science Server

## Development Build

1. In the root of this repo, create  virtual environment ([guide](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/))
    ```
    python -m venv env
    ```

2. Activate the environment

    Windows
    ```
    env\Scripts\activate
    ```

    macOS and Linux
    ```
    source env/bin/activate
    ```

3. Install requirements
    ```
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
    ```

4. Create a `.env` in the root directory of this repo with the following info. This file **is not version controlled**. This is where we place secret credentials.
    ```
    FLASK_APP=___:APP
    FLASK_ENV="development"
    FLASK_DEBUG=True
    ```

5. Run the server in development
    ```
    flask run
    ```
