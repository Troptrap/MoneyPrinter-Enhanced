import json
with open("audiolibrary.json","r") as f:
  t = json.load(f)
  t = json.dumps(t).replace("export=download","export=open")
with open("audiolibrary.json","w") as ff:
  tt =json.loads(t)
  json.dump(tt,ff)
    