
import argparse
from main import generate_fingerprint, SessionLocal, Fingerprint

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and check fingerprint")
    parser.add_argument("--image", required=True, help="Path to the image file")
    parser.add_argument("--name", required=True, help="Name to include in the fingerprint")

    args = parser.parse_args()

    with open(args.image, "rb") as f:
        image_bytes = f.read()

    fingerprint = generate_fingerprint(image_bytes, args.name)

    db = SessionLocal()
    exists = db.query(Fingerprint).filter(Fingerprint.hash_value == fingerprint).first()

    print(f"Fingerprint: {fingerprint}")

    if exists:
        print("Status: BLOCKED (already exists in the database)")
    else:
        print("Status: NEW (adding to database)")
        db.add(Fingerprint(hash_value=fingerprint))
        db.commit()
