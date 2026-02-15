from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def transform_image(input_path: str, output_path: str, preset: str) -> None:
    img = Image.open(input_path).convert("RGB")

    if preset == "pencil_sketch_outline":
        gray = ImageOps.grayscale(img)
        inv = ImageOps.invert(gray)
        blur = inv.filter(ImageFilter.GaussianBlur(radius=8))
        out = Image.blend(gray, ImageOps.invert(blur), alpha=0.6)
    elif preset == "charcoal_shading":
        gray = ImageOps.grayscale(img).filter(ImageFilter.EDGE_ENHANCE_MORE)
        out = ImageEnhance.Contrast(gray).enhance(2.5)
    elif preset == "watercolor_wash_reference":
        out = img.filter(ImageFilter.SMOOTH_MORE).filter(ImageFilter.GaussianBlur(radius=1.8))
        out = ImageEnhance.Color(out).enhance(1.35)
    elif preset == "simplified_shapes_block_in":
        out = img.quantize(colors=12, method=Image.FASTOCTREE).convert("RGB")
        out = out.filter(ImageFilter.SMOOTH)
    elif preset == "value_map":
        gray = ImageOps.grayscale(img)
        out = gray.point(lambda p: 0 if p < 51 else 64 if p < 102 else 128 if p < 153 else 192 if p < 204 else 255)
    else:
        out = img

    out.save(output_path)
