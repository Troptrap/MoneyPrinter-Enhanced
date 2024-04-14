import edge_tts
import json


async def voices_list():
    """Print all available voices."""
    voicesdata = await edge_tts.list_voices()
    obj = {}
    for voice in voicesdata:
        locale = voice["Locale"]
        if locale not in obj:
            obj[locale] = []
        obj[locale].append({voice["ShortName"]: voice["ShortName"].replace("Neural", "").replace(locale + "-", "")})
    with open("../Frontend/microsoft_voices.json", "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)


async def msft_tts(text, voice, file):
    print("Generating with Microsoft..")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file)
    print("Saved as: " + file)
