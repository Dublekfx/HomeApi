To run manually, `python home_api.py`

Before first use, run 
```
python -m pip install -r requirements.txt
python generate_cert.py
```

Rename `config_template.py` to `config.py`, add switches, and change API Key or Tapo login info

In production, I'm running it with [NSSM](https://nssm.cc/) to ensure it starts with startup and restarts on crash

I then use [Tasker](https://tasker.joaoapps.com/) on my phone to detect when I am connected to my home wifi to send the appropriate curl command to the server.

I am also using https://www.duckdns.org/ to ensure that I have a consistent DNS name I can use to connect