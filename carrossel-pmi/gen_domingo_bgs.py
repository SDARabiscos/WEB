#!/usr/bin/env python3
"""Gera backgrounds para os 3 carrosseis de domingo via Gemini Image API (google.genai)."""

from google import genai
from google.genai import types
from PIL import Image
import io, os, time

client = genai.Client(api_key="AIzaSyB_XVBqAYPwzICrzmBCQjSHYjLTj98cEoM")

OUT = "/home/user/WEB/carrossel-pmi"

PROMPTS = {
    # ── CAROUSEL A — "Seu conteúdo parece feito por robô" ──────────
    "dom_a_s01": (
        "Dark cinematic editorial photo. Infinite grid of identical glowing smartphones "
        "in a pitch black void, all screens showing the exact same social media post. "
        "Dramatic purple and pink neon reflections. Top-down perspective. "
        "Hyperrealistic 8K, fashion magazine aesthetic."
    ),
    "dom_a_s02": (
        "Surreal editorial: industrial assembly line in darkness, robotic arms stamping "
        "out hundreds of identical glowing content cards. Deep purple neon lighting. "
        "Cinematic, dark, dystopian elegance."
    ),
    "dom_a_s03": (
        "Striking editorial photo: a long corridor of identical mannequins all holding "
        "identical phones, all posing identically. At the very end one real human with "
        "a glowing distinct warm aura. Dark moody, cinematic, purple tones."
    ),
    "dom_a_s04": (
        "Intimate editorial: a single human hand writing with a real pen on paper, "
        "surrounded by floating faded digital screens. Warm focused light on the hand, "
        "everything else dark blue-purple. Depth of field, cinematic."
    ),
    "dom_a_s05": (
        "Minimal dark editorial: one glowing human fingerprint floating in total darkness, "
        "surrounded by thousands of identical binary code patterns fading away. "
        "Purple neon glow, high contrast, cinematic."
    ),

    # ── CAROUSEL B — "Viralizar não é mais o objetivo" ─────────────
    "dom_b_s01": (
        "Dramatic editorial: a giant iridescent soap bubble floating in dark space, "
        "inside the bubble hundreds of tiny social media icons. About to pop. "
        "Vivid colors, cinematic tension, dark background."
    ),
    "dom_b_s02": (
        "Surreal editorial: a massive crowd of identical people all chasing "
        "floating transparent bubbles disappearing into darkness. No one looking back. "
        "Aerial view, cinematic, dark moody, purple-blue tones."
    ),
    "dom_b_s03": (
        "Editorial contrast: left side a massive empty stadium with lights blazing, "
        "right side a small intimate bonfire gathering of 5 friends, warmth and connection. "
        "High contrast, cinematic."
    ),
    "dom_b_s04": (
        "Cinematic contrast: a single steady candle burning bright on left, "
        "massive fireworks already fading and smoking on right. Dark background. "
        "Metaphor for lasting vs fleeting. Editorial."
    ),
    "dom_b_s05": (
        "Cinematic editorial: a person confidently walking toward a small warm group of people, "
        "leaving a blurry massive crowd behind. Strong directional movement. "
        "Dark background, golden warm light ahead."
    ),

    # ── CAROUSEL C — "47 milhões de empreendedores" ─────────────────
    "dom_c_s01": (
        "Aerial drone shot: an overwhelming sea of people seen from directly above, "
        "all wearing grey, filling every inch of space. "
        "Slightly desaturated, cinematic, editorial."
    ),
    "dom_c_s02": (
        "Surreal editorial: a person standing overwhelmed in a chaotic Brazilian street market, "
        "surrounded by identical products piled to the ceiling, looking confused and lost. "
        "Warm vivid colors, cinematic."
    ),
    "dom_c_s03": (
        "Editorial split metaphor: foggy scene with a megaphone pointing at empty chairs "
        "on left, versus one person whispering to an engaged attentive crowd on right. "
        "Dark cinematic contrast."
    ),
    "dom_c_s04": (
        "Clean editorial split: crystal clear water on left, murky opaque water on right. "
        "Perfect mirror symmetry. Visual metaphor for clarity vs confusion. "
        "Dark cinematic frame."
    ),
    "dom_c_s05": (
        "Warm cinematic editorial: Brazilian entrepreneur at a minimalist desk, "
        "single focused beam of golden light, eureka moment expression, "
        "dark dramatic background."
    ),
}


def generate(key, prompt, retries=3):
    path = f"{OUT}/bg_domingo_{key}.png"
    if os.path.exists(path):
        print(f"  skip {key} (já existe)")
        return True
    for attempt in range(retries):
        try:
            resp = client.models.generate_images(
                model="imagen-4.0-generate-001",
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="3:4",
                    output_mime_type="image/png",
                )
            )
            img_data = resp.generated_images[0].image.image_bytes
            img = Image.open(io.BytesIO(img_data))
            img.save(path)
            print(f"  ✓ {key}")
            return True
        except Exception as e:
            print(f"  ✗ {key} tentativa {attempt+1}: {e}")
            time.sleep(4)
    print(f"  FALHOU {key}")
    return False


if __name__ == "__main__":
    print("Gerando backgrounds para Domingo...\n")
    groups = [
        ("CAROUSEL A — Robô", sorted(k for k in PROMPTS if k.startswith("dom_a"))),
        ("CAROUSEL B — Viral", sorted(k for k in PROMPTS if k.startswith("dom_b"))),
        ("CAROUSEL C — 47M",  sorted(k for k in PROMPTS if k.startswith("dom_c"))),
    ]
    for label, keys in groups:
        print(f"\n{label}")
        for k in keys:
            generate(k, PROMPTS[k])
            time.sleep(1)

    total = sum(1 for k in PROMPTS if os.path.exists(f"{OUT}/bg_domingo_{k}.png"))
    print(f"\n{total}/{len(PROMPTS)} backgrounds prontos → {OUT}")
