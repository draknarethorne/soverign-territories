"""ComfyUI render embeddings used as optional identity evidence."""

import pathlib

import numpy as np

import comfy_workflows as cw
from likeness_library.scoring import core_scores, nz


class Renders:
    """Load candidate ComfyUI renders and derive their centered identity cores."""

    def __init__(self, cfg, cache, embed, st, space, limit=40):
        self.cfg, self.cache, self.embed = cfg, cache, embed
        self.st, self.space, self.limit = st, space, limit
        self.memo = {}
        self.files = {}
        roots = []
        try:
            roots.append(cw.output_root(cfg))
            roots.append(pathlib.Path(cfg.get("sharedOutput", "")))
        except (KeyError, TypeError):
            pass
        for root in roots:
            if root and root.is_dir():
                for path in root.rglob("*.png"):
                    self.files.setdefault(path.name, path)

    def sister_files(self, hero):
        prefixes = (f"{hero}_Qwen_X_Pose_", f"{hero}_Qwen_Alpha_1_Prime_")
        return sorted(
            path for name, path in self.files.items() if name.startswith(prefixes)
        )

    def angel_files(self, hero):
        directory = cw.WF / "_candidates" / "angel-primes" / hero
        names = (
            {path.stem + ".png" for path in directory.rglob("*.json")}
            if directory.is_dir()
            else set()
        )
        return sorted(self.files[name] for name in names if name in self.files)

    def centroid(self, hero, kind):
        """Return a render-core vector and its core size, or None if no render is usable."""
        loaded = self._load(hero, kind)
        return loaded and (loaded[0], loaded[1])

    def _load(self, hero, kind):
        key = (hero.lower(), kind)
        if key not in self.memo:
            files = self.sister_files(hero) if kind == "sister" else self.angel_files(hero)
            if len(files) > self.limit:
                files = [
                    files[index]
                    for index in np.linspace(0, len(files) - 1, self.limit).astype(int)
                ]
            raw_vectors, added = [], False
            for path in files:
                digest = self.cache.sha(path)
                if digest not in self.cache.emb:
                    self.cache.emb[digest] = self.embed(path) or {"faces": -1}
                    added = True
                data = self.cache.emb[digest]
                if data.get("v") and data.get("px", 0) >= self.st["minFace"]:
                    raw_vectors.append(np.array(data["v"]))
            if added:
                self.cache.save()
            self.memo[key] = None
            if raw_vectors:
                vectors = np.array([nz(vector - self.space.mean) for vector in raw_vectors])
                _, core, centroid = core_scores(vectors)
                self.memo[key] = (centroid, len(core), np.array(raw_vectors), core)
        return self.memo[key]

    def render_space(self, heroes, kind):
        """Return render-only identity vectors centered across all requested heroes."""
        loaded = {hero: self._load(hero, kind) for hero in heroes}
        loaded = {hero: value for hero, value in loaded.items() if value}
        if not loaded:
            return {}
        mean = np.vstack([value[2] for value in loaded.values()]).mean(0)
        result = {}
        for hero, value in loaded.items():
            vectors = nz(value[2] - mean)
            _, _core, centroid = core_scores(vectors)
            result[hero] = centroid
        return result
