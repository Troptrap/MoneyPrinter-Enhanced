import json
uniq = []
with open("audiolibrary.json", "r") as f:
  data = json.load(f)
for i in data:
  for x in data[i]["instruments"]:
    if x.replace("'","").lower() not in uniq:
      uniq.append(x.replace("'","").lower())
with open("instr.json","w") as fi:
  json.dump(uniq,fi)