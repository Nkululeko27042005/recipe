"""
Seed the RecipE database with sample users, recipes, reactions, comments, follows.

Usage:
    flask seed          (via CLI: see app/__init__.py registration)
    python -m app.seed  (direct run)
"""
import random
from datetime import datetime, timedelta
from app.extensions import db
from app.models import (
    User, UserPreference, Recipe, Ingredient, Step,
    RecipeImage, Comment, Reaction, Follow, Notification,
)


SEED_USERS = [
    {
        "username": "chef_elena",
        "email": "elena@recipe.dev",
        "password": "password123",
        "bio": "Italian nonna at heart. Pasta is a love language.",
        "prefs": {"categories": ["Italian", "Pasta", "Desserts"], "dietary": []},
    },
    {
        "username": "greenfork",
        "email": "green@recipe.dev",
        "password": "password123",
        "bio": "Plant-forward, seasonal, always colourful.",
        "prefs": {"categories": ["Vegan", "Salads", "Bowls"], "dietary": ["Vegan", "Gluten-Free"]},
    },
    {
        "username": "spice_route",
        "email": "spice@recipe.dev",
        "password": "password123",
        "bio": "Chasing heat across continents.",
        "prefs": {"categories": ["Indian", "Thai", "Curries"], "dietary": []},
    },
    {
        "username": "bake_and_bloom",
        "email": "bake@recipe.dev",
        "password": "password123",
        "bio": "Flour on my apron, always.",
        "prefs": {"categories": ["Baking", "Desserts", "Bread"], "dietary": ["Vegetarian"]},
    },
    {
        "username": "quick_plate",
        "email": "quick@recipe.dev",
        "password": "password123",
        "bio": "30-minute dinners for busy nights.",
        "prefs": {"categories": ["Quick Meals", "Weeknight"], "dietary": []},
    },
]


SEED_RECIPES = [
    {
        "title": "Rustic Tomato Basil Pasta",
        "category": "Italian",
        "description": "A bright, garlicky pasta that comes together in twenty minutes.",
        "author": "chef_elena",
        "ingredients": [
            {"name": "Spaghetti", "quantity": "400", "unit": "g"},
            {"name": "Ripe tomatoes", "quantity": "6", "unit": "whole", "notes": "roughly chopped"},
            {"name": "Garlic", "quantity": "4", "unit": "cloves"},
            {"name": "Fresh basil", "quantity": "1", "unit": "handful"},
            {"name": "Olive oil", "quantity": "3", "unit": "tbsp"},
            {"name": "Parmesan", "quantity": "50", "unit": "g", "notes": "grated"},
        ],
        "steps": [
            "Boil salted water and cook spaghetti until al dente.",
            "Warm olive oil, add sliced garlic, cook until fragrant.",
            "Add tomatoes, simmer 8 minutes until saucy.",
            "Toss pasta with sauce, torn basil and parmesan.",
            "Serve immediately with extra basil on top.",
        ],
    },
    {
        "title": "Golden Turmeric Chickpea Bowl",
        "category": "Vegan",
        "description": "A nourishing bowl of turmeric chickpeas, greens and tahini.",
        "author": "greenfork",
        "ingredients": [
            {"name": "Chickpeas", "quantity": "2", "unit": "cans", "notes": "drained"},
            {"name": "Turmeric", "quantity": "1", "unit": "tsp"},
            {"name": "Kale", "quantity": "200", "unit": "g"},
            {"name": "Tahini", "quantity": "3", "unit": "tbsp"},
            {"name": "Lemon", "quantity": "1", "unit": "whole"},
            {"name": "Brown rice", "quantity": "1", "unit": "cup"},
        ],
        "steps": [
            "Cook rice per package instructions.",
            "Sauté chickpeas with turmeric, salt and a splash of oil until golden.",
            "Massage kale with lemon juice and olive oil.",
            "Whisk tahini with lemon and water to make a dressing.",
            "Assemble bowls and drizzle generously.",
        ],
    },
    {
        "title": "Red Thai Coconut Curry",
        "category": "Thai",
        "description": "Fragrant, creamy, and ready in half an hour.",
        "author": "spice_route",
        "ingredients": [
            {"name": "Red curry paste", "quantity": "3", "unit": "tbsp"},
            {"name": "Coconut milk", "quantity": "1", "unit": "can"},
            {"name": "Chicken thigh", "quantity": "500", "unit": "g", "notes": "sliced"},
            {"name": "Bell peppers", "quantity": "2", "unit": "whole"},
            {"name": "Thai basil", "quantity": "1", "unit": "handful"},
            {"name": "Fish sauce", "quantity": "2", "unit": "tbsp"},
        ],
        "steps": [
            "Fry curry paste in a little oil until aromatic.",
            "Add chicken and sear.",
            "Pour in coconut milk, simmer 12 minutes.",
            "Add peppers and fish sauce, cook 5 minutes more.",
            "Finish with Thai basil and serve with rice.",
        ],
    },
    {
        "title": "Sourdough Country Loaf",
        "category": "Bread",
        "description": "Crackly crust, open crumb, deeply satisfying.",
        "author": "bake_and_bloom",
        "ingredients": [
            {"name": "Bread flour", "quantity": "500", "unit": "g"},
            {"name": "Water", "quantity": "375", "unit": "g"},
            {"name": "Active starter", "quantity": "100", "unit": "g"},
            {"name": "Salt", "quantity": "10", "unit": "g"},
        ],
        "steps": [
            "Mix flour and water, rest 30 minutes (autolyse).",
            "Add starter and salt, knead until smooth.",
            "Bulk ferment 4 hours with stretch-and-folds every 45 minutes.",
            "Shape and cold-proof overnight.",
            "Bake in a preheated Dutch oven at 250°C for 20 min covered, 20 min uncovered.",
        ],
    },
    {
        "title": "15-Minute Garlic Butter Shrimp",
        "category": "Quick Meals",
        "description": "Weeknight hero. Serve over rice, pasta, or crusty bread.",
        "author": "quick_plate",
        "ingredients": [
            {"name": "Shrimp", "quantity": "500", "unit": "g", "notes": "peeled"},
            {"name": "Butter", "quantity": "3", "unit": "tbsp"},
            {"name": "Garlic", "quantity": "5", "unit": "cloves"},
            {"name": "Lemon", "quantity": "1", "unit": "whole"},
            {"name": "Parsley", "quantity": "2", "unit": "tbsp"},
        ],
        "steps": [
            "Melt butter in a pan, add minced garlic.",
            "Add shrimp, cook 2 minutes per side.",
            "Squeeze lemon over, toss parsley.",
            "Serve immediately.",
        ],
    },
    {
        "title": "Molten Chocolate Cake",
        "category": "Desserts",
        "description": "Crisp outside, warm chocolate inside. Ready in ten minutes.",
        "author": "chef_elena",
        "ingredients": [
            {"name": "Dark chocolate", "quantity": "200", "unit": "g"},
            {"name": "Butter", "quantity": "100", "unit": "g"},
            {"name": "Eggs", "quantity": "3", "unit": "whole"},
            {"name": "Sugar", "quantity": "100", "unit": "g"},
            {"name": "Flour", "quantity": "60", "unit": "g"},
        ],
        "steps": [
            "Melt chocolate and butter together.",
            "Whisk eggs and sugar until pale.",
            "Fold in chocolate mixture, then flour.",
            "Bake in buttered ramekins at 200°C for 10 minutes.",
            "Invert and serve immediately.",
        ],
    },
    {
        "title": "Miso Mushroom Ramen",
        "category": "Japanese",
        "description": "Deep umami broth with silky noodles.",
        "author": "spice_route",
        "ingredients": [
            {"name": "Miso paste", "quantity": "3", "unit": "tbsp"},
            {"name": "Mushrooms", "quantity": "300", "unit": "g"},
            {"name": "Ramen noodles", "quantity": "2", "unit": "portions"},
            {"name": "Vegetable stock", "quantity": "1", "unit": "L"},
            {"name": "Soft-boiled eggs", "quantity": "2", "unit": "whole"},
            {"name": "Spring onion", "quantity": "3", "unit": "stalks"},
        ],
        "steps": [
            "Sauté mushrooms until golden.",
            "Add stock and miso, simmer 10 minutes.",
            "Cook noodles separately and divide into bowls.",
            "Pour broth over, top with mushrooms, egg, and spring onion.",
        ],
    },
    {
        "title": "Avocado Grapefruit Salad",
        "category": "Salads",
        "description": "Bright, buttery, and tangy plate with three ingredients and one dressing.",
        "author": "greenfork",
        "ingredients": [
            {"name": "Avocado", "quantity": "2", "unit": "whole"},
            {"name": "Grapefruit", "quantity": "1", "unit": "whole"},
            {"name": "Arugula", "quantity": "100", "unit": "g"},
            {"name": "Olive oil", "quantity": "2", "unit": "tbsp"},
            {"name": "Lime", "quantity": "1", "unit": "whole"},
        ],
        "steps": [
            "Segment grapefruit over a bowl to catch juice.",
            "Whisk juice with lime and olive oil.",
            "Arrange arugula, avocado and grapefruit.",
            "Drizzle dressing and serve cold.",
        ],
    },
]


SEED_COMMENTS = [
    "Made this tonight, the whole family loved it!",
    "Subbed the dairy and it still worked beautifully.",
    "This is going straight into my weeknight rotation.",
    "Thank you for the clear steps, first time went perfectly.",
    "I added a bit of chilli and it was divine.",
    "Saved! Can't wait to try it this weekend.",
    "The flavour balance here is spot on.",
    "Quick, cheap and delicious. Five stars.",
]


def _backdate(days=0, hours=0):
    return datetime.utcnow() - timedelta(days=days, hours=hours)


def seed():
    print("🌱 Seeding RecipE database...")

    # Clean slate (safe for dev): delete in dependency order
    db.session.query(Notification).delete()
    db.session.query(Reaction).delete()
    db.session.query(Comment).delete()
    db.session.query(Follow).delete()
    db.session.query(Step).delete()
    db.session.query(Ingredient).delete()
    db.session.query(RecipeImage).delete()
    db.session.query(Recipe).delete()
    db.session.query(UserPreference).delete()
    db.session.query(User).delete()
    db.session.commit()

    # --- Users ---
    users = {}
    for i, u in enumerate(SEED_USERS):
        user = User(
            username=u["username"],
            email=u["email"],
            bio=u["bio"],
            created_at=_backdate(days=30 - i * 2),
        )
        user.set_password(u["password"])
        db.session.add(user)
        db.session.flush()

        prefs = UserPreference(
            user_id=user.id,
            categories=",".join(u["prefs"]["categories"]),
            dietary=",".join(u["prefs"]["dietary"]),
        )
        db.session.add(prefs)
        users[u["username"]] = user

    db.session.commit()
    print(f"  ✓ {len(users)} users created")

    # --- Recipes ---
    recipes = []
    for i, r in enumerate(SEED_RECIPES):
        author = users[r["author"]]
        recipe = Recipe(
            title=r["title"],
            category=r["category"],
            description=r["description"],
            user_id=author.id,
            created_at=_backdate(days=20 - i, hours=random.randint(0, 23)),
        )
        db.session.add(recipe)
        db.session.flush()

        for idx, ing in enumerate(r["ingredients"]):
            db.session.add(Ingredient(
                recipe_id=recipe.id,
                name=ing["name"],
                quantity=ing.get("quantity", ""),
                unit=ing.get("unit", ""),
                weight=ing.get("weight", ""),
                notes=ing.get("notes", ""),
                position=idx,
            ))

        for idx, step in enumerate(r["steps"], start=1):
            db.session.add(Step(
                recipe_id=recipe.id,
                position=idx,
                instruction=step,
            ))

        recipes.append(recipe)

    db.session.commit()
    print(f"  ✓ {len(recipes)} recipes created")

    # --- Follows (random graph) ---
    follow_count = 0
    for follower in users.values():
        for followed in users.values():
            if follower.id == followed.id:
                continue
            # ~40% chance of following
            if random.random() < 0.4:
                db.session.add(Follow(
                    follower_id=follower.id,
                    followed_id=followed.id,
                    created_at=_backdate(days=random.randint(1, 20)),
                ))
                follow_count += 1
    db.session.commit()
    print(f"  ✓ {follow_count} follow relationships created")

    # --- Reactions (random likes / dislikes) ---
    reaction_count = 0
    for recipe in recipes:
        # pick 2-5 random reactors
        reactors = random.sample(list(users.values()), k=random.randint(2, 5))
        for user in reactors:
            if user.id == recipe.user_id:
                continue
            value = 1 if random.random() < 0.85 else -1
            db.session.add(Reaction(
                user_id=user.id,
                recipe_id=recipe.id,
                value=value,
                created_at=_backdate(days=random.randint(0, 15)),
            ))
            reaction_count += 1
    db.session.commit()
    print(f"  ✓ {reaction_count} reactions created")

    # --- Comments (top-level + some replies) ---
    comment_count = 0
    for recipe in recipes:
        commenters = random.sample(list(users.values()), k=random.randint(1, 3))
        parent_ids = []
        for user in commenters:
            body = random.choice(SEED_COMMENTS)
            comment = Comment(
                recipe_id=recipe.id,
                user_id=user.id,
                body=body,
                created_at=_backdate(days=random.randint(0, 10)),
            )
            db.session.add(comment)
            db.session.flush()
            parent_ids.append(comment.id)
            comment_count += 1

        # One reply on the first comment
        if parent_ids and random.random() < 0.6:
            replier = random.choice(list(users.values()))
            db.session.add(Comment(
                recipe_id=recipe.id,
                user_id=replier.id,
                parent_id=parent_ids[0],
                body="Totally agree, thanks for the tip!",
                created_at=_backdate(days=random.randint(0, 5)),
            ))
            comment_count += 1

    db.session.commit()
    print(f"  ✓ {comment_count} comments created")

    print("✅ Seeding complete.")
    print("   Login with any of these:")
    for u in SEED_USERS:
        print(f"     - {u['username']} / {u['password']}")


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed()