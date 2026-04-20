import urllib.request, json

data = json.loads(urllib.request.urlopen("https://openrouter.ai/api/v1/models").read())
for m in data.get("data", []):
    if "deepseek" in m["id"].lower():
        inp = float(m["pricing"]["prompt"]) * 1e6
        out = float(m["pricing"]["completion"]) * 1e6
        print(f"{m['id']:50s} | in: ${inp:.2f}/M  out: ${out:.2f}/M")
