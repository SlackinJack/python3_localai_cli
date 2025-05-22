echo
echo
echo
echo "### Installing APT requirements... (You may be prompted for your password.)"
sudo apt install -y $(cat requirements/apt_requirements)

echo
echo
echo
echo "### Removing old virtual environment if it exists..."
rm -r .venv

echo
echo
echo
echo "### Setting up Python virtual environment..."
python3 -m venv .venv

echo
echo
echo
echo "### Installing Python requirements..."
source .venv/bin/activate
python3 -m pip install -r requirements/python_requirements
