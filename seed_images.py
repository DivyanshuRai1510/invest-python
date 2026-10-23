"""Image URL generators for companies, products and investors"""
import random

def company_image_url(name, category):
    """Return a picsum image URL for a company"""
    seed = hash(name + "company") % 10000
    return f"https://picsum.photos/seed/{seed}/800/600"

def product_image_url(name, category):
    """Return a picsum image URL for a product"""
    seed = hash(name + category + "product") % 10000
    return f"https://picsum.photos/seed/{seed}/600/400"

def investor_avatar_url(name):
    """Return a picsum avatar for an investor"""
    seed = hash(name + "investor") % 10000
    return f"https://picsum.photos/seed/{seed}/300/300"

def user_avatar_url(name):
    """Return a picsum avatar for a user"""
    seed = hash(name + "user") % 10000
    return f"https://picsum.photos/seed/{seed}/300/300"
