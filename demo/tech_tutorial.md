# Getting Started with Docker

## Prerequisites

- A machine running **Linux**, **macOS**, or **Windows 10/11**
- Basic comfort with the terminal and command line
- At least **4 GB of RAM** available
- A free [Docker Hub](https://hub.docker.com) account

---

## Step 1: Install Docker

1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. Run the installer and follow the on-screen prompts
3. Verify the installation by running the version check:

```bash
docker --version
docker compose version
```

---

## Step 2: Run Your First Container

1. Pull the official Nginx image from Docker Hub
2. Start a container and map port 8080 on your host to port 80 in the container
3. Open your browser and navigate to `http://localhost:8080`

```bash
docker pull nginx:latest
docker run -d --name my-web -p 8080:80 nginx:latest
docker ps
```

> **Tip:** The `-d` flag runs the container in detached mode so your terminal stays free. Use `docker logs my-web` to check output.

---

## Step 3: Build a Custom Image

Create a file called `Dockerfile` in your project root:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Then build and run it:

```bash
docker build -t my-api:1.0 .
docker run -d -p 8000:8000 my-api:1.0
```

---

## Step 4: Compose Multi-Container Apps

Create a `docker-compose.yml` to orchestrate your API and a database together:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/appdb

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

```bash
docker compose up -d
docker compose logs -f
```

---

## Quick Reference

| Command | Description |
|---|---|
| `docker ps` | List running containers |
| `docker ps -a` | List all containers including stopped |
| `docker images` | List downloaded images |
| `docker stop <name>` | Stop a running container |
| `docker rm <name>` | Remove a stopped container |
| `docker rmi <image>` | Remove an image |
| `docker compose up -d` | Start all services in background |
| `docker compose down` | Stop and remove all services |

> **Remember:** Containers are ephemeral. Always use **volumes** for data you need to persist, and **environment variables** for configuration that changes between environments.
