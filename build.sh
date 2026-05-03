#!/bin/bash
# Build script for single-service deployment
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..
echo "Frontend build complete!"
