#!/bin/bash
set -e

cd /var/www/juegos

echo "📥 Actualizando código..."
git fetch origin
git reset --hard origin/master

echo "🔄 Actualizando versión cache..."
npm version patch --no-git-tag-version

export PYTHONPATH=/var/www/juegos

echo "🔍 Comprobando config..."
./venv/bin/python scripts/check_config.py

echo "🚀 Reiniciando servicio..."
systemctl restart juegos

echo "✅ Deploy completado"