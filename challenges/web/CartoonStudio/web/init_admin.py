import time
from pymongo import MongoClient
from config import MONGO_URI, ADMIN_PASSWORD

def wait_for_mongo(uri, retries=20, delay=1.5):
    for i in range(retries):
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            client.server_info()
            return client
        except Exception as e:
            print("Waiting for mongo...", e)
            time.sleep(delay)
    raise RuntimeError("Unable to connect to MongoDB")

def ensure_admin(db):
    users = db.users
    admin = users.find_one({"username": "admin"})
    if admin:
        print("Admin user already exists.")
        return
    users.insert_one({
        "username": "admin",
        "password": ADMIN_PASSWORD,
        "isAdmin": True,
        "watch_count": 0,
        "created_at": time.time()
    })
    print("Created admin user with username 'admin'")

def seed_cartoons(db):
    cartoons = db.cartoons
    if cartoons.count_documents({}) == 0:
        sample = [
            {"title": "Bouncy Bunny", "description": "A cheerful bunny adventure.", "url": "/static/sample_videos/bunny.mp4", "views": 0},
            {"title": "Space Cat", "description": "A cat explores the galaxy.", "url": "/static/sample_videos/spacecat.mp4", "views": 0},
            {"title": "Tiny Robots", "description": "Robots learning to dance.", "url": "/static/sample_videos/robots.mp4", "views": 0}
        ]
        cartoons.insert_many(sample)
        print("Seeded sample cartoons.")
    else:
        print("Cartoons already present, skipping seeding.")

if __name__ == "__main__":
    client = wait_for_mongo(MONGO_URI)
    db = client.get_default_database()
    ensure_admin(db)
    seed_cartoons(db)
    client.close()