#!/bin/bash

cd /docker/nerdearla-mcp

git fetch origin main

if [ $(git rev-list HEAD...origin/main --count) != 0 ]; then
    echo "Changes detected, deploying..."
    git pull origin main
    docker compose down
    docker compose build --no-cache
    docker compose up -d
    echo "Deployment complete"
fi
