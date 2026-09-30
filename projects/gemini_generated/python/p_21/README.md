# Flask URL Shortener Service

This project is a self-contained URL shortener web service built with Flask and a SQLite database.

## Features

- **Shorten URLs**: Converts long URLs into a random 6-character code.
- **Custom Aliases**: Users can provide their own custom name for a short link.
- **Click Tracking**: Counts every time a shortened link is used.
- **Analytics**: A public stats page for each link shows the click count, original URL, and other metadata.
- **Link Expiration**: Users can set an expiration time in hours for their links.
- **Self-Contained**: Creates and uses a local `shortener.db` file, requiring no external database setup.

## Setup and Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize the Database:**
    Before running the app for the first time, you must create the database schema. Run the following command in your terminal:
    ```bash
    flask init-db
    ```
    This will create a `shortener.db` file in the project directory.

4.  **Run the Application:**
    ```bash
    flask run
    ```
    The application will be running at `http://127.0.0.1:5000`.

## How to Use the Service

- **Create a short link**: Go to `http://127.0.0.1:5000`, enter a long URL, and click "Shorten".
- **Use a short link**: Navigate to `http://127.0.0.1:5000/<your-short-code>` to be redirected to the original URL.
- **View stats**: Navigate to `http://127.0.0.1:5000/stats/<your-short-code>` to see the click count and other details.
