#!/bin/bash
# Script to install GitLab Runner locally for OSS MLOps Platform

echo "🚀 Installing GitLab Runner..."

# 1. Download binary directly from AWS S3 (Stable link for Linux amd64)
echo "Downloading GitLab Runner..."
sudo curl -L --output /usr/local/bin/gitlab-runner "https://s3.dualstack.us-east-1.amazonaws.com/gitlab-runner-downloads/latest/binaries/gitlab-runner-linux-amd64"

# 2. Grant execution permissions
sudo chmod +x /usr/local/bin/gitlab-runner

# 3. Install as a User Service
echo "⚙️ Configuring runner for user: $USER"
gitlab-runner install --user-service --working-directory=$HOME

# 4. Add current user to the docker group (Prep for Shell Executor)
echo "🐳 Adding $USER to docker group..."
sudo usermod -aG docker $USER

echo "✅ GitLab Runner installed successfully!"
echo "---------------------------------------------------------"
echo "👉 NEXT STEPS TO RUN IN TERMINAL:"
echo "1. Register the Runner: run 'gitlab-runner register'"
echo "   - URL: https://gitlab.com"
echo "   - Token: <Get from Settings -> CI/CD -> Runners on GitLab>"
echo "   - Executor: Enter 'shell'"
echo ""
echo "2. Start the Runner: run 'gitlab-runner run'"
echo "   (⚠️ Note: DO NOT use 'sudo' for this step since we are running in user-mode)"
echo "---------------------------------------------------------"