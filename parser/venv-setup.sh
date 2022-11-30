VENV_DIR="./.venv"

if command -v deactivate &> /dev/null
then
    deactivate
fi

if [ -d "$VENV_DIR" ]; then
  rm -rf ./.venv
fi

python3 -m venv ./.venv
source ./.venv/bin/activate
python -m pip install -r ./requirements.txt
