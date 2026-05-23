#!/usr/bin/env python3
"""Backgrounds surreais v2 para os 3 carrosseis de domingo."""

from google import genai
from google.genai import types
from PIL import Image
import io, os, time

client = genai.Client(api_key="AIzaSyB_XVBqAYPwzICrzmBCQjSHYjLTj98cEoM")
OUT = "/home/user/WEB/carrossel-pmi"

PROMPTS = {
    # ── A: BRUTALISMO — tema "conteúdo de robô" ─────────────────
    "v2_a_s01": (
        "Photorealistic surrealism: a businessman in an expensive suit sitting at a desk, "
        "but his head is replaced by a vintage CRT television monitor showing a spinning "
        "loading buffering wheel. Empty brutalist concrete office. Dramatic side lighting. "
        "Cinematic, hyper-detailed, dark tones with one warm spotlight."
    ),
    "v2_a_s02": (
        "Dark surreal editorial: an industrial factory assembly line, but instead of products, "
        "hundreds of identical human FACES are being mass-produced and stamped by mechanical arms. "
        "The faces all have the same blank expression. Noir lighting, cinematic. "
        "Hyperrealistic photographic quality."
    ),
    "v2_a_s03": (
        "Surreal editorial photo: a person stands in front of a mirror, "
        "but their reflection is a cold metallic robot. The human is colorful and warm, "
        "the reflection is grey and mechanical. Split lighting, dramatic, cinematic 8K."
    ),
    "v2_a_s04": (
        "Macro surreal editorial: two hands side by side on a desk. "
        "Left hand is a human hand writing with a pen, warm skin. "
        "Right hand is a transparent glass hand with visible circuits and wires inside, "
        "typing on a keyboard. Dark background, single overhead light, hyperrealistic."
    ),
    "v2_a_s05": (
        "Surreal editorial: a person walks through a doorway. "
        "On the left side (entrance) they are full of color, personality, expressive. "
        "On the right side (exit) they become a grey identical robot like everyone else. "
        "High contrast doorway scene, cinematic, dark background."
    ),

    # ── B: RAW EDITORIAL — tema "viral vs comunidade" ────────────
    "v2_b_s01": (
        "Surreal editorial: a massive translucent soap bubble the size of a building "
        "floating above a grey city at night. Inside the bubble: a tiny crowd of fans cheering. "
        "The bubble has a visible crack. Vivid iridescent colors against dark city. Cinematic 8K."
    ),
    "v2_b_s02": (
        "Dramatic surreal photo: a marathon runner crossing a finish line made of giant "
        "glowing heart icons and like buttons. But just beyond the finish line is a dark void, "
        "nothing there. The runner looks confused. Bright neon finish line, dark void ahead. "
        "Cinematic editorial."
    ),
    "v2_b_s03": (
        "Surreal editorial: two doors side by side in darkness. "
        "Behind door 1 (left): a roaring stadium with 100k people, bright lights, chaos. "
        "Behind door 2 (right): an intimate round dinner table with 8 people, warm candlelight, "
        "everyone laughing and engaged. High contrast. Cinematic."
    ),
    "v2_b_s04": (
        "Conceptual editorial photo: a person made entirely of shredded colorful confetti "
        "is celebrating with arms raised, but the confetti that forms their body is already "
        "beginning to fall and scatter into nothing. Dark background, dramatic lighting. "
        "Hyperrealistic surrealism."
    ),
    "v2_b_s05": (
        "Warm cinematic editorial: a single round dinner table with 5-6 people, "
        "all leaning in, laughing, genuinely connected. Warm golden candlelight. "
        "Beautiful bokeh background. Intimate and real. Dark surroundings, "
        "light focused on the table. Like a fine dining magazine photo."
    ),

    # ── C: ANTI-DESIGN — tema "47M empreendedores" ───────────────
    "v2_c_s01": (
        "Aerial view surreal: a bird's eye photo of a massive identical grey labyrinth-maze "
        "filled with thousands of tiny identical businesspeople all walking in circles, "
        "none finding the exit. Slightly desaturated, cinematic, editorial. "
        "The maze fills the entire frame."
    ),
    "v2_c_s02": (
        "Surreal editorial: a Brazilian street market but every single product on every stall "
        "is exactly identical — same box, same color, same label. One confused vendor "
        "looks lost among infinite identical shelves. Warm chaotic lighting, real texture. "
        "Hyperrealistic."
    ),
    "v2_c_s03": (
        "Conceptual editorial: a giant megaphone mounted on a wall, shooting out hundreds "
        "of identical flyers into the air. Every single flyer flies away unread and falls. "
        "Next to it: one person whispering into another person's ear, both smiling. "
        "Dark dramatic contrast between the two scenes. Cinematic."
    ),
    "v2_c_s04": (
        "Clean editorial split: two identical glass fishbowls side by side. "
        "Left fishbowl: crystal clear water, one happy goldfish. "
        "Right fishbowl: completely murky brown water, nothing visible. "
        "White or light grey studio background, dramatic spotlight. Editorial photography."
    ),
    "v2_c_s05": (
        "Warm dramatic editorial: a single spotlight on an empty theater stage. "
        "The stage has one microphone stand. The audience seats are completely packed "
        "with people leaning forward in anticipation. Dark auditorium, one warm spotlight. "
        "Cinematic, hopeful tension."
    ),
}


def generate(key, prompt, retries=3):
    path = f"{OUT}/bg_v2_{key}.png"
    if os.path.exists(path):
        print(f"  skip {key}"); return True
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
            img = Image.open(io.BytesIO(resp.generated_images[0].image.image_bytes))
            img.save(path)
            print(f"  ✓ {key}"); return True
        except Exception as e:
            print(f"  ✗ {key} [{attempt+1}]: {e}")
            time.sleep(4)
    print(f"  FALHOU {key}"); return False


if __name__ == "__main__":
    groups = [
        ("A — Brutalismo", [k for k in PROMPTS if "a_s" in k]),
        ("B — Raw Editorial", [k for k in PROMPTS if "b_s" in k]),
        ("C — Anti-Design",   [k for k in PROMPTS if "c_s" in k]),
    ]
    for label, keys in groups:
        print(f"\n{label}")
        for k in sorted(keys):
            generate(k, PROMPTS[k])
            time.sleep(1)
    total = sum(1 for k in PROMPTS if os.path.exists(f"{OUT}/bg_v2_{k}.png"))
    print(f"\n{total}/{len(PROMPTS)} gerados")
