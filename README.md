# eBay Backend Development Assignment - Listings API

Note: WIP

## Setup and Run

### 1. Create a local environment file `.env` from the example file:
```bash
   cp .env.example .env
```
   Update Database configurations in the `.env` file. 

   Check for compose.yaml file for the database configurations.


### 2. Run the application:

#### 2.1 Build and run the application as using local environment:
```bash
   make
   make run
```

#### 2.2 Or run the application using docker and docker compose:
```bash
   make docker-up
```

### 3. Access the API at `http://0.0.0.0:1903/v1/docs`.

## Run tests
Run all tests:
```bash
   make test
```