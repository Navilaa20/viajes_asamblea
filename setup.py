import subprocess

# Activar entorno virtual
subprocess.run("source /home/coopach/virtualenv/transporte/3.9/bin/activate && cd /home/coopach/transporte && pip install -r requirements.txt && pip list && python --version", shell=True)
