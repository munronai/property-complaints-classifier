"""Pillow image normalization (EXIF orientation transpose, RGB conversion, <=1568px scaling) and synthetic test image generator."""

import base64
import io
import os
import uuid
from typing import Any, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageOps

from app.domain.schemas import ImageTelemetry

MAX_JEV_IMAGE_EDGE = 1568


def prepare_image_for_jev(
    image_source: Any,
    asset_ref: Optional[str] = None,
) -> Tuple[str, str, ImageTelemetry]:
    """Ensures upright EXIF orientation, converts to RGB, resizes longest side <= 1568px, and returns base64 JPEG + telemetry."""
    if asset_ref is None:
        asset_ref = f"asset-{uuid.uuid4().hex[:8]}"

    if isinstance(image_source, str):
        if os.path.exists(image_source):
            img = Image.open(image_source)
        else:
            # Treat as base64 string (strip data URI prefix if present)
            raw_b64 = image_source.split(",")[-1].strip()
            img_bytes = base64.b64decode(raw_b64)
            img = Image.open(io.BytesIO(img_bytes))
    elif isinstance(image_source, bytes):
        img = Image.open(io.BytesIO(image_source))
    elif isinstance(image_source, Image.Image):
        img = image_source.copy()
    else:
        raise ValueError(f"Unsupported image input type: {type(image_source)}")

    orig_w, orig_h = img.size
    exif_orientation = img.getexif().get(0x0112, 1) if hasattr(img, "getexif") else 1
    exif_transposed = exif_orientation not in (None, 1)

    # 1. Transpose based on EXIF so mobile/WhatsApp photos never arrive sideways
    img = ImageOps.exif_transpose(img)

    # 2. Ensure RGB format
    if img.mode != "RGB":
        img = img.convert("RGB")

    # 3. Resize so longest side <= 1568px
    w, h = img.size
    resized = False
    if max(w, h) > MAX_JEV_IMAGE_EDGE:
        scale = MAX_JEV_IMAGE_EDGE / float(max(w, h))
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        resized = True

    norm_w, norm_h = img.size
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    jpeg_bytes = buffer.getvalue()
    encoded_b64 = base64.b64encode(jpeg_bytes).decode("utf-8")

    telemetry = ImageTelemetry(
        asset_ref=asset_ref,
        original_width=orig_w,
        original_height=orig_h,
        normalized_width=norm_w,
        normalized_height=norm_h,
        exif_transposed=exif_transposed,
        resized=resized,
        mime_type="image/jpeg",
        size_bytes=len(jpeg_bytes),
    )
    return encoded_b64, "image/jpeg", telemetry


SYNTHETIC_IMAGE_CATALOG: Dict[str, str] = {
    "cistern_valve": "WC Cistern Overflow & Float Valve (Plumbing 194010)",
    "sink_leak": "Under-Sink Pipe & Push-Fit Waste Trap Leak (Plumbing 192001 / 192005)",
    "black_mould": "Awaab's Law Black Mould on Window Reveal (Damp 114001)",
    "ceiling_light_leak": "Emergency Water Ingress Through Ceiling Rose (Electrical 211001)",
    "broken_hinge": "Snapped Kitchen Base Unit Concealed Hinge (Joinery 125011)",
    "inappropriate_placeholder": "Simulated Inappropriate / Rude Photo Attachment (Safety Gate Test)",
}


def generate_synthetic_defect_image(
    preset_key: str,
    width: int = 800,
    height: int = 600,
) -> bytes:
    """Generates a visual synthetic defect image in JPEG bytes for repeatable multimodal sandbox testing."""
    img = Image.new("RGB", (width, height), color=(238, 236, 230))
    draw = ImageDraw.Draw(img)

    if preset_key == "black_mould":
        # Window reveal frame with dark mould spore clusters
        draw.rectangle([40, 40, width - 40, height - 40], outline=(160, 160, 160), width=4)
        for offset in range(0, 260, 18):
            draw.ellipse(
                [55 + offset, 55 + (offset % 90), 140 + offset, 150 + (offset % 90)],
                fill=(28, 32, 26),
            )
            draw.ellipse(
                [70 + (offset % 140), 120 + offset, 165 + (offset % 140), 210 + offset],
                fill=(38, 42, 35),
            )
        draw.text((60, height - 80), "SYNTHETIC SAMPLE: BLACK MOULD ON REVEAL", fill=(20, 20, 20))

    elif preset_key == "sink_leak":
        # Under-sink cabinet with copper pipe & white plastic U-trap + water puddle
        draw.rectangle([100, 60, width - 100, height - 60], fill=(215, 205, 190))
        # Copper supply pipe
        draw.rectangle([260, 80, 284, 420], fill=(184, 115, 51))
        # White push-fit waste trap
        draw.rectangle([420, 80, 465, 340], fill=(245, 245, 245), outline=(180, 180, 180), width=2)
        draw.ellipse([400, 290, 510, 390], fill=(245, 245, 245), outline=(180, 180, 180), width=2)
        # Water puddle at base
        draw.ellipse([220, 430, 560, 515], fill=(70, 135, 195))
        draw.text((120, height - 95), "SYNTHETIC SAMPLE: UNDER-SINK PIPE / TRAP LEAK", fill=(20, 20, 20))

    elif preset_key == "ceiling_light_leak":
        # Stained ceiling rose with water droplets and electrical pendant
        draw.ellipse([220, 120, 580, 420], fill=(175, 155, 125))
        draw.ellipse([340, 210, 460, 310], fill=(250, 250, 250), outline=(90, 90, 90), width=3)
        draw.line([400, 310, 400, 470], fill=(60, 60, 60), width=6)
        # Water droplets falling
        for dx, dy in [(365, 340), (425, 360), (385, 410), (440, 430)]:
            draw.ellipse([dx, dy, dx + 14, dy + 24], fill=(40, 120, 220))
        draw.text((130, height - 80), "SYNTHETIC SAMPLE: WATER IN CEILING ROSE", fill=(20, 20, 20))

    elif preset_key == "broken_hinge":
        # Kitchen carcass side panel with detached 110-degree metal hinge
        draw.rectangle([80, 50, 320, height - 50], fill=(225, 220, 210), outline=(140, 130, 120), width=3)
        draw.polygon([(330, 70), (660, 130), (660, height - 30), (330, height - 90)], fill=(195, 160, 120))
        # Snapped metal hinge plate
        draw.rectangle([290, 180, 370, 240], fill=(150, 155, 160), outline=(60, 60, 60), width=2)
        draw.text((100, height - 85), "SYNTHETIC SAMPLE: SNAPPED KITCHEN CABINET HINGE", fill=(20, 20, 20))

    elif preset_key == "inappropriate_placeholder":
        # Safe red moderation test pattern representing an inappropriate image upload
        img = Image.new("RGB", (width, height), color=(140, 25, 35))
        draw = ImageDraw.Draw(img)
        draw.rectangle([40, 40, width - 40, height - 40], outline=(255, 210, 210), width=6)
        draw.text(
            (90, height // 2 - 20),
            "MODERATION TEST FIXTURE: INAPPROPRIATE / RUDE PHOTO",
            fill=(255, 255, 255),
        )
        draw.text(
            (90, height // 2 + 20),
            "Stage 1 Content Safety Gate will Flag & Purge these bytes",
            fill=(255, 220, 220),
        )

    else:
        # Default: cistern_valve or generic plumbing fixture
        draw.rectangle([200, 100, 600, 420], fill=(248, 248, 252), outline=(150, 150, 160), width=3)
        draw.line([210, 210, 590, 210], fill=(60, 140, 210), width=4)
        draw.ellipse([450, 175, 530, 245], fill=(220, 80, 60))
        draw.text((160, height - 80), f"SYNTHETIC SAMPLE: {preset_key.upper()}", fill=(30, 30, 30))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()
