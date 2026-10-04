from app.extensions import db
from app.models import User, UserPreference
from app.utils.file_handler import delete_file


class UserService:

    @staticmethod
    def create_user(username, email, password, bio="", preferences=None):
        if User.query.filter_by(username=username).first():
            raise ValueError("Username already taken")
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already registered")

        user = User(username=username, email=email, bio=bio)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        prefs = UserPreference(
            user_id=user.id,
            categories=",".join((preferences or {}).get("categories", [])),
            dietary=",".join((preferences or {}).get("dietary", [])),
        )
        db.session.add(prefs)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user, **fields):
        # Handle avatar: delete old file when replacing or removing
        if "avatar" in fields and fields["avatar"] is not None:
            old_avatar = user.avatar
            new_avatar = fields["avatar"]
            if old_avatar and old_avatar != new_avatar:
                delete_file(old_avatar)
            user.avatar = new_avatar

        if "bio" in fields and fields["bio"] is not None:
            user.bio = fields["bio"]

        db.session.commit()
        return user

    @staticmethod
    def update_preferences(user, categories=None, dietary=None):
        prefs = user.preference or UserPreference(user_id=user.id)
        if categories is not None:
            prefs.categories = ",".join(categories)
        if dietary is not None:
            prefs.dietary = ",".join(dietary)
        db.session.add(prefs)
        db.session.commit()
        return prefs

    @staticmethod
    def get_user(user_id):
        return User.query.get_or_404(user_id)

    @staticmethod
    def search(query, limit=20):
        return (User.query
                .filter(User.username.ilike(f"%{query}%"))
                .limit(limit).all())