#!/bin/bash

echo "=================================================="
echo "🎉 CI/CD Github Actions Ansible Image"
echo ""
echo "Welcome"
echo ""
echo "📚 For more information:"
echo "  - This project: https://github.com/drkeyongenesis/ansible-github-actions-cicd"
echo "  - Official docs: https://ansible.readthedocs.io/projects/ansible-build-data"
echo "=================================================="
echo ""

echo "📦 Essential packages installed by install-essential.sh:"
echo "=================================================="
cat /install.sh
echo "=================================================="
echo ""

echo "🐍 Python packages installed from requirements.txt:"
echo "=================================================="
cat /requirements.txt
echo "=================================================="
echo ""

echo "ℹ️  Installed Ansible version:"
echo "=================================================="
ansible --version
echo "=================================================="
echo ""

echo "💡 Suggested commands:"
echo "=================================================="
echo "- ansible          : Run ansible commands"
echo "- ansible-playbook : Execute ansible playbooks"
echo "- ansible-galaxy   : Manage Ansible roles and collections"
echo "=================================================="

# Keep container running
exec "$@" 
