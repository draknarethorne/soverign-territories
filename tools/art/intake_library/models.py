"""Local model files for intake: fetched once into the per-user model folder, verified, then loaded lazily."""
import functools
import hashlib
import os
import pathlib
import urllib.request

import comfy_workflows as cw

MODELS = {
    "person": {
        "file": "maskrcnn_resnet50_fpn_v2_coco-73cbd019.pth",
        "url": "https://download.pytorch.org/models/maskrcnn_resnet50_fpn_v2_coco-73cbd019.pth",
        "sha256": "73cbd0190fcbe3ba339921fbce2c3a0b6bb9126c9a133c85e43a2a8e060a109e",
    },
    "fill": {
        "file": "big-lama.pt",
        "url": "https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt",
        "sha256": "7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c",
    },
}


def folder():
    return cw.model_cache_root() / "models"


def digest(path):
    value = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def path(kind):
    """The verified local file; downloads it once (with a printed notice) when missing."""
    spec = MODELS[kind]
    target = folder() / spec["file"]
    if not target.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_name(target.name + ".part")
        print(f"Downloading the {kind} model {spec['file']} once into {target.parent} ...")
        try:
            urllib.request.urlretrieve(spec["url"], partial)
            if digest(partial) != spec["sha256"]:
                raise OSError(f"downloaded {spec['file']} does not match its pinned sha256")
            partial.replace(target)
        finally:
            partial.unlink(missing_ok=True)
    return target


def threads():
    """Torch threads per process; parallel intake workers split the cores through ST_INTAKE_THREADS."""
    try:
        wanted = int(os.environ.get("ST_INTAKE_THREADS", "0"))
    except ValueError:
        wanted = 0
    return max(1, wanted or min(8, os.cpu_count() or 1))


def describe():
    """Recipe evidence: pinned files and hashes (verified at download, not re-hashed on every import)."""
    return {kind: {"file": spec["file"], "sha256": spec["sha256"]} for kind, spec in MODELS.items()}


@functools.lru_cache(maxsize=None)
def person_detector():
    import torch
    from torchvision.models.detection import maskrcnn_resnet50_fpn_v2

    torch.set_num_threads(threads())
    net = maskrcnn_resnet50_fpn_v2(weights=None, weights_backbone=None)
    net.load_state_dict(torch.load(path("person"), map_location="cpu"))
    return net.eval()


@functools.lru_cache(maxsize=None)
def fill_model():
    import torch

    torch.set_num_threads(threads())
    return torch.jit.load(str(path("fill")), map_location="cpu").eval()
