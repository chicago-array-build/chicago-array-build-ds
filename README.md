# Chicago Array of Things Build: Data Science Server

## Resources
* [Database Schema](https://dbdiagram.io/d/5ce41f0e1f6a891a6a6564ae)
* [Array of Things Workshop in R](https://geodacenter.github.io/aot-workshop/)
* [Array of Things Jupyter Notebook Tutorial](https://github.com/ddiLab/CommunitySensing/blob/master/AoT-Workshop_2018/AoT_Tutorial.ipynb)
* Official Array of Things pages
    * https://api-of-things.plenar.io/
    * https://api.arrayofthings.org/
    * https://arrayofthings.github.io/

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

4. Create a `.env` in the root directory of this repo with the following info. **This file is not version controlled**. This is where we place secret credentials.
    ```
    FLASK_APP=app:APP
    FLASK_ENV="development"
    FLASK_DEBUG=True
    PLOTLY_USER=""
    PLOTLY_API_KEY=""
    ```

5. Instantiate the database
    ```
    flask shell
    DB.create_all()
    ```

6. Run the server in development
    ```
    flask run
    ```

7. _Optional:_ Create an ipython kernel to use Jupyter Notebook with this environment. After calling `jupyter notebook`, you'll need to select this kernel in the interface (see [documentation](https://ipython.readthedocs.io/en/stable/install/kernel_install.html)).
    ```
    ipython kernel install --user --name=chicago-aot-env
    ```