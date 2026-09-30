# Markdown Blog Engine

This project is a markdown blog engine with syntax highlighting and RSS feed generation.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

## Usage

1.  Build the blog:

    ```bash
    npm run build
    ```

2.  The generated HTML files and RSS feed will be in the `public` directory.

### Adding new posts

1.  Create a new markdown file in the `posts` directory.
2.  Add a frontmatter section with the title and date.
3.  Run the build command again.
