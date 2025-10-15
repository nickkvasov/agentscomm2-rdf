# Multi-Agent Collaboration POC - Docker Setup

This document explains how to run the Multi-Agent Collaboration POC system using Docker Compose.

## 🐳 Docker Architecture

The system consists of two main services:

1. **Fuseki** - Apache Jena Fuseki SPARQL server
2. **Gateway** - FastAPI-based validator gateway

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 2GB RAM available
- Ports 3030 and 8000 available

### Setup and Run

1. **Start the services:**
   ```bash
   ./docker-setup.sh
   ```

2. **Or manually:**
   ```bash
   docker-compose up --build -d
   ```

3. **Test the system:**
   ```bash
   python test-docker.py
   ```

4. **Run the demo:**
   ```bash
   python simple_demo.py
   ```

## 📊 Services

### Fuseki (SPARQL Server)
- **URL**: http://localhost:3030
- **Admin UI**: http://localhost:3030
- **SPARQL Endpoint**: http://localhost:3030/ds
- **Dataset**: `ds` (TDB2 persistent storage)

### Gateway (API Server)
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

## 🔧 Management Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fuseki
docker-compose logs -f gateway
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild and Restart
```bash
docker-compose up --build -d
```

### Access Container Shell
```bash
# Gateway container
docker-compose exec gateway bash

# Fuseki container
docker-compose exec fuseki bash
```

## 📁 Data Persistence

- **Fuseki Data**: Stored in Docker volume `fuseki_data`
- **Application Data**: Mounted from `./data/` directory
- **Logs**: Available in `./logs/` directory

## 🔍 Troubleshooting

### Services Not Starting

1. **Check if ports are available:**
   ```bash
   lsof -i :3030
   lsof -i :8000
   ```

2. **Check Docker logs:**
   ```bash
   docker-compose logs
   ```

3. **Restart services:**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

### Fuseki Issues

1. **Check Fuseki status:**
   ```bash
   curl http://localhost:3030/$/ping
   ```

2. **Access Fuseki admin:**
   - Open http://localhost:3030 in browser
   - Default dataset: `ds`

### Gateway Issues

1. **Check Gateway health:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check Gateway logs:**
   ```bash
   docker-compose logs gateway
   ```

## 🧪 Testing

### Run Tests
```bash
# Test Docker services
python test-docker.py

# Run POC demo
python simple_demo.py

# Run full test suite
python src/tests/test_runner.py
```

### SPARQL Queries

You can query the knowledge graph directly:

```bash
# Example SPARQL query
curl -X POST \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/sparql-results+json" \
  -d "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10" \
  http://localhost:3030/ds/query
```

## 📈 Monitoring

### Health Checks
- **Fuseki**: http://localhost:3030/$/ping
- **Gateway**: http://localhost:8000/health

### Metrics
- **Gateway Metrics**: http://localhost:8000/metrics
- **Fuseki Stats**: http://localhost:3030/$/stats

## 🔒 Security Notes

- Services are exposed on localhost only
- No authentication configured (development setup)
- For production, add authentication and HTTPS

## 🚀 Production Deployment

For production deployment:

1. **Add authentication** to Gateway
2. **Configure HTTPS** for both services
3. **Set up monitoring** and alerting
4. **Configure backup** for Fuseki data
5. **Use environment variables** for configuration
6. **Set up logging** aggregation

## 📝 Configuration

### Environment Variables

- `FUSEKI_ENDPOINT`: Fuseki SPARQL endpoint URL
- `PYTHONPATH`: Python path for the application

### Volume Mounts

- `./data/` → `/app/data/` (application data)
- `fuseki_data` → `/fuseki` (Fuseki persistent storage)

## 🎯 Next Steps

1. **Load initial data** into Fuseki
2. **Configure agents** to connect to Gateway
3. **Run test scenarios** to validate functionality
4. **Monitor performance** and optimize
5. **Scale to multiple agents** for load testing

The Docker setup provides a complete, isolated environment for running the Multi-Agent Collaboration POC system!
