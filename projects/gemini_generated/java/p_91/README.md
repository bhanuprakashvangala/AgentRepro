# Search Service with Elasticsearch

This project demonstrates a search service using Spring Boot and Elasticsearch.

## Requirements

- Java 8 or higher
- Maven
- Elasticsearch running on `localhost:9200`

## How to Run

1. **Start Elasticsearch:**
   Ensure you have an Elasticsearch instance running on `http://localhost:9200`. You can run it using Docker:
   ```bash
   docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:7.17.6
   ```

2. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd search-service
   ```

3. **Build the project:**
   ```bash
   mvn clean install
   ```

4. **Run the application:**
   ```bash
   mvn spring-boot:run
   ```

The application will start on port 8080.

## Usage

### Index Sample Data

First, index some sample data into Elasticsearch:

```bash
curl -X POST http://localhost:8080/products/index-sample-data
```

### Create a Product

```bash
curl -X POST -H "Content-Type: application/json" -d '
{
  "id": "11",
  "name": "Smartwatch",
  "description": "Fitness tracker with heart rate monitor",
  "price": 199.99
}' http://localhost:8080/products
```

### Get Product by ID

```bash
curl http://localhost:8080/products/1
```

### Search Products (Full-text search)

```bash
curl http://localhost:8080/products/search?query=laptop
```

### Filter Products by Price

```bash
curl http://localhost:8080/products/filter-by-price?minPrice=100&maxPrice=300
```

### Search and Paginate Products

```bash
curl http://localhost:8080/products/search-and-paginate?query=keyboard&page=0&size=5
```
