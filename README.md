# Story Creator API

This API allows users to register, log in, create stories, contribute to stories, and export stories as PDFs or images. It is built using Django and Django REST Framework.

## Features

- **User Registration and Login:** Users can register and log in using JWT tokens.
- **Story Management:** Users can create, view, update, and delete stories.
- **Contributions:** Users can contribute two-line content to a story.
- **Exporting Stories:** Stories can be exported as PDFs or images.

#
## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/storytelling-api.git
    cd storytelling-api
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run migrations:**

    ```bash
    python manage.py migrate
    ```

5. **Create a superuser (optional):**

    ```bash
    python manage.py createsuperuser
    ```

6. **Start the development server:**

    ```bash
    python manage.py runserver
    ```

7. **Start Celery worker (for exporting tasks):**

    ```bash
    celery -A story_creator worker --loglevel=info
    ```





