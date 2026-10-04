from app.extensions import db
from app.models import Recipe, Ingredient, Step, RecipeImage, RecipeVideo
from app.utils.file_handler import save_file, delete_file


class RecipeService:

    @staticmethod
    def create_recipe(author, data, images=None, video=None):
        recipe = Recipe(
            title=data["title"],
            description=data.get("description", ""),
            category=data.get("category", ""),
            user_id=author.id,
        )
        db.session.add(recipe)
        db.session.flush()

        RecipeService._set_ingredients(recipe, data.get("ingredients", []))
        RecipeService._set_steps(recipe, data.get("steps", []))

        if images:
            for i, img in enumerate(images):
                fname = save_file(img, "image")
                if fname:
                    db.session.add(RecipeImage(
                        recipe_id=recipe.id, filename=fname, is_primary=(i == 0)
                    ))

        if video:
            vname = save_file(video, "video")
            if vname:
                db.session.add(RecipeVideo(recipe_id=recipe.id, filename=vname))

        db.session.commit()
        return recipe

    @staticmethod
    def update_recipe(recipe, data, new_images=None, new_video=None, remove_image_ids=None):
        for f in ("title", "description", "category"):
            if f in data:
                setattr(recipe, f, data[f])

        if "ingredients" in data:
            for ing in list(recipe.ingredients):
                db.session.delete(ing)
            db.session.flush()
            RecipeService._set_ingredients(recipe, data["ingredients"])

        if "steps" in data:
            for step in list(recipe.steps):
                db.session.delete(step)
            db.session.flush()
            RecipeService._set_steps(recipe, data["steps"])

        if remove_image_ids:
            for img in recipe.images:
                if img.id in remove_image_ids:
                    delete_file(img.filename)
                    db.session.delete(img)

        if new_images:
            for img in new_images:
                fname = save_file(img, "image")
                if fname:
                    db.session.add(RecipeImage(
                        recipe_id=recipe.id, filename=fname,
                        is_primary=(len(recipe.images) == 0)
                    ))

        if new_video:
            if recipe.video:
                delete_file(recipe.video.filename)
                db.session.delete(recipe.video)
            vname = save_file(new_video, "video")
            if vname:
                db.session.add(RecipeVideo(recipe_id=recipe.id, filename=vname))

        db.session.commit()
        return recipe

    @staticmethod
    def _set_ingredients(recipe, items):
        for idx, item in enumerate(items):
            db.session.add(Ingredient(
                recipe_id=recipe.id,
                name=item.get("name", ""),
                quantity=item.get("quantity", ""),
                unit=item.get("unit", ""),
                weight=item.get("weight", ""),
                notes=item.get("notes", ""),
                position=idx,
            ))

    @staticmethod
    def _set_steps(recipe, items):
        for idx, item in enumerate(items, start=1):
            db.session.add(Step(
                recipe_id=recipe.id,
                position=idx,
                instruction=item.get("instruction", ""),
            ))

    @staticmethod
    def delete_recipe(recipe):
        for img in recipe.images:
            delete_file(img.filename)
        if recipe.video:
            delete_file(recipe.video.filename)
        db.session.delete(recipe)
        db.session.commit()

    @staticmethod
    def save_for_user(user, recipe):
        if not recipe.savers.filter_by(id=user.id).first():
            recipe.savers.append(user)
            db.session.commit()
        return True

    @staticmethod
    def unsave_for_user(user, recipe):
        if recipe.savers.filter_by(id=user.id).first():
            recipe.savers.remove(user)
            db.session.commit()
        return True

    @staticmethod
    def list_recipes(category=None, search=None, limit=50, offset=0):
        q = Recipe.query
        if category:
            q = q.filter(Recipe.category.ilike(category))
        if search:
            q = q.filter(Recipe.title.ilike(f"%{search}%"))
        return (q.order_by(Recipe.created_at.desc())
                .limit(limit).offset(offset).all())