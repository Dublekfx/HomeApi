To run manually, `python home_api.py`

Before first use, run 
```
python -m pip install -r requirements.txt
python generate_cert.py
```

Rename `config_template.py` to `config.py` add switches or change API Key or Tapo login info

In production, I'm running it with NSSM (https://nssm.cc/)