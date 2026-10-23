"""Stable image URLs for demo content. User portraits are real stock photographs,
not generated avatars. Users can replace them with their own uploaded headshot.
"""
import hashlib

# RandomUser hosts real photographic portraits suitable for demo accounts.
def _stable_index(name, namespace, count=90):
    digest = hashlib.sha256((namespace + str(name)).encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % count + 1


def _industry_photo(category):
    c = (category or "").lower()
    photos = [
        (("hydrogen", "fuel cell", "clean energy", "energy", "solar", "sustain"), "photo-1473341304170-971146b5b4b9"),
        (("health", "medical", "biotech"), "photo-1576091160399-112ba8d25d1d"),
        (("agri", "farm", "food"), "photo-1500382017468-9049fed747ef"),
        (("fintech", "finance", "bank"), "photo-1460925895917-afdab827c52f"),
        (("robot", "manufact", "automation"), "photo-1485827404703-89b55fcc595e"),
        (("ai", "deeptech", "software", "iot", "technology"), "photo-1518770660439-4636190af475"),
        (("education", "edtech"), "photo-1523580494863-6f3031224c94"),
    ]
    return next((image for keys, image in photos if any(key in c for key in keys)), "photo-1486406146926-c627a92ad1ab")


def company_image_url(name, category):
    # Seed company marks with sector-related editorial imagery rather than unrelated random animals/scenes.
    image = _industry_photo(category)
    return f"https://images.unsplash.com/{image}?auto=format&fit=crop&w=600&h=600&q=85"


def product_image_url(name, category):
    image = _industry_photo(category)
    return f"https://images.unsplash.com/{image}?auto=format&fit=crop&w=900&h=650&q=85"


def investor_avatar_url(name):
    index = _stable_index(name, "investor")
    gender = "women" if int(hashlib.sha256(str(name).encode()).hexdigest()[-1], 16) % 2 else "men"
    return f"https://randomuser.me/api/portraits/{gender}/{index}.jpg"


def user_avatar_url(name):
    index = _stable_index(name, "founder")
    gender = "women" if int(hashlib.sha256(str(name).encode()).hexdigest()[-1], 16) % 2 else "men"
    return f"https://randomuser.me/api/portraits/{gender}/{index}.jpg"
