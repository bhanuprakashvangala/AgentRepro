# JSON API Mock Server

This project is a JSON API mock server with custom responses, built with `json-server`.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

2.  The server will be running at `http://localhost:3000`.

### API Endpoints

-   `GET /posts`: Get all posts.
-   `GET /posts/1`: Get post with ID 1.
-   `POST /posts`: Create a new post.
-   `PUT /posts/1`: Update post with ID 1.
-   `PATCH /posts/1`: Partially update post with ID 1.
-   `DELETE /posts/1`: Delete post with ID 1.

### Query Parameters

-   `GET /posts?title=json-server`: Filter posts by title.
-   `GET /posts?_sort=views&_order=asc`: Sort posts by views in ascending order.
-   `GET /posts?_start=20&_end=30`: Paginate posts.

### Response Delay

The server has a configurable delay of 500ms for all responses.
