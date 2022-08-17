if [ ! -f config ]; then
    cp tmp.config config
fi
virtualenv pywebview_env -p python3
source pywebview_env/bin/activate
pip install -r requirements.txt
python3 solarsync.py --init
mkdir -p logs
