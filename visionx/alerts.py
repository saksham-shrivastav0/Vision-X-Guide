import time

# Fallback ordering only, NOT danger scores.
OBJECT_PRIORITY = {
    "car": 3,
    "bus": 3,
    "truck": 3,
    "motorcycle": 3,
    "bicycle": 2,
    "person": 2,
}

# Convert model labels into familiar spoken words.
FRIENDLY_NAMES = {
    "person": "person",
    "car": "car",
    "bus": "bus",
    "truck": "truck",
    "motorcycle": "motorcycle",
    "bicycle": "bicycle",
    "cell phone": "mobile phone",
    "traffic light": "traffic light",
    "stop sign": "stop sign",
    "chair": "chair",
    "bench": "bench",
    "dog": "dog",
    "cat": "cat",
    "bottle": "bottle",
    "backpack": "bag",
    "suitcase": "suitcase",
    "handbag": "handbag",
    "potted plant": "plant",
    "fire hydrant": "fire hydrant",
    "stairs": "stairs",
}


class AlertManager:
    def __init__(
        self,
        cooldown=3.0,
        forget_after=2.0,
        min_confidence=0.60,
    ):
        self.cooldown = cooldown
        self.forget_after = forget_after
        self.min_confidence = min_confidence

        self.last_message = None
        self.last_announcement_time = float("-inf")

        self.last_seen_time = {}
        self.announced_keys = set()
        self.current_priority = None

    def _make_message(self, name, position):
        label = FRIENDLY_NAMES.get(name, name.replace("_", " "))

        if name in {"car", "bus", "truck", "motorcycle", "bicycle"}:
            label = "vehicle"

        if position == "on the left":
            location = "on your left"
        elif position == "on the right":
            location = "on your right"
        else:
            location = "near the center of your camera view"

        return f"{label.capitalize()} detected {location}."

    def choose_alert(self, detections, now=None):
        """
        Each detection:
            name, position, confidence

        Optional:
            area_ratio

        Larger apparent bounding boxes are considered first.
        This is NOT a real distance or collision-risk estimate.

        Returns one spoken message, or None.
        """
        if now is None:
            now = time.monotonic()

        valid = []

        for item in detections:
            try:
                confidence = float(item["confidence"])
                name = str(item["name"]).strip().lower()
                position = str(item["position"]).strip()
                area_ratio = float(item.get("area_ratio", 0.0))
            except (KeyError, TypeError, ValueError):
                continue

            if not name or not position:
                continue

            if confidence < self.min_confidence:
                continue

            if not 0.0 <= confidence <= 1.0:
                continue

            if area_ratio < 0.0:
                area_ratio = 0.0

            area_ratio = min(area_ratio, 1.0)

            key = f"{name}:{position}"
            self.last_seen_time[key] = now

            valid.append(
                {
                    "key": key,
                    "name": name,
                    "position": position,
                    "confidence": confidence,
                    "area_ratio": area_ratio,
                    "priority": OBJECT_PRIORITY.get(name, 1),
                }
            )

        # Forget detections that have disappeared.
        self.last_seen_time = {
            key: seen_at
            for key, seen_at in self.last_seen_time.items()
            if now - seen_at <= self.forget_after
        }

        self.announced_keys.intersection_update(self.last_seen_time.keys())

        if self.last_message not in self.last_seen_time:
            self.last_message = None

        if not valid:
            self.current_priority = None
            return None

        # First: largest apparent box.
        # Then: fallback category priority and confidence.
        valid.sort(
            key=lambda item: (
                item["area_ratio"],
                item["priority"],
                item["confidence"],
            ),
            reverse=True,
        )

        self.current_priority = valid[0]

        # Do not repeat an alert for an object that remains visible.
        candidate = next(
            (item for item in valid if item["key"] not in self.announced_keys),
            None,
        )

        if candidate is None:
            return None

        # Keep a short gap between spoken alerts.
        if now - self.last_announcement_time < self.cooldown:
            return None

        self.last_message = candidate["key"]
        self.last_announcement_time = now
        self.announced_keys.add(candidate["key"])

        return self._make_message(
            candidate["name"],
            candidate["position"],
        )

    def reset_if_scene_clear(self, now=None):
        if now is None:
            now = time.monotonic()

        self.last_seen_time = {
            key: seen_at
            for key, seen_at in self.last_seen_time.items()
            if now - seen_at <= self.forget_after
        }

        self.announced_keys.intersection_update(self.last_seen_time.keys())

        if self.last_message not in self.last_seen_time:
            self.last_message = None
