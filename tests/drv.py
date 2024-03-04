import subprocess
cmd = ["wget", "http://docs.google.com/uc?export=open&id=1GgOgE_S_r4yvRyo0X9VVdEDfOMdWoux0","-O","somes.mp3"]
result = subprocess.run(cmd)