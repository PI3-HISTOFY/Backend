#!/bin/bash
set -xe

# Instalar Tesseract en Amazon Linux 2023
dnf install -y tesseract

chmod +x .platform/hooks/postdeploy/01_install_tesseract.sh
