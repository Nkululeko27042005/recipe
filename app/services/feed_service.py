from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models import Recipe, User, Follow, Reaction, Comment, UserPreference
from app.models.recipe import saved_recipes as saved_recipes_table


def _month_start():
    """First moment of the current calendar month (UTC)."""
    now = datetime.utcnow()
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _week_ago():
    return datetime.utcnow() - timedelta(days=7)


def _thirty_days_ago():
    return datetime.utcnow() - timedelta(days=30)


class FeedService:

    # ------------------------------------------------------------------ #
    #  Core feeds                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def main_feed(limit=30):
        return (Recipe.query.order_by(Recipe.created_at.desc())
                .limit(limit).all())

    @staticmethod
    def my_recipes(user):
        return (Recipe.query.filter_by(user_id=user.id)
                .order_by(Recipe.created_at.desc()).all())

    @staticmethod
    def saved_recipes(user):
        return (user.saved_recipes
                .order_by(Recipe.created_at.desc()).all())

    # ------------------------------------------------------------------ #
    #  Recipes: rankings                                                   #
    # ------------------------------------------------------------------ #

    @staticmethod
    def top_liked(limit=6):
        """All-time most liked recipes. Only recipes with ≥1 like appear."""
        likes = (db.session.query(
                    Reaction.recipe_id,
                    func.count(Reaction.id).label("likes")
                 )
                 .filter(Reaction.value == 1)
                 .group_by(Reaction.recipe_id)
                 .subquery())
        return (db.session.query(Recipe)
                .join(likes, Recipe.id == likes.c.recipe_id)
                .order_by(likes.c.likes.desc(), Recipe.created_at.desc())
                .limit(limit).all())

    @staticmethod
    def most_famous_recipe():
        """
        The single most famous recipe of all time:
        score = likes*3 + saves*2 + comments*1
        Returns one Recipe or None.
        """
        likes_sq = (db.session.query(
                        Reaction.recipe_id,
                        func.count(Reaction.id).label("likes")
                    )
                    .filter(Reaction.value == 1)
                    .group_by(Reaction.recipe_id)
                    .subquery())

        saves_sq = (db.session.query(
                        saved_recipes_table.c.recipe_id,
                        func.count().label("saves")
                    )
                    .group_by(saved_recipes_table.c.recipe_id)
                    .subquery())

        comments_sq = (db.session.query(
                           Comment.recipe_id,
                           func.count(Comment.id).label("cmts")
                       )
                       .group_by(Comment.recipe_id)
                       .subquery())

        score = (
            func.coalesce(likes_sq.c.likes, 0) * 3
            + func.coalesce(saves_sq.c.saves, 0) * 2
            + func.coalesce(comments_sq.c.cmts, 0)
        )

        result = (db.session.query(Recipe, score.label("score"))
                  .outerjoin(likes_sq, Recipe.id == likes_sq.c.recipe_id)
                  .outerjoin(saves_sq, Recipe.id == saves_sq.c.recipe_id)
                  .outerjoin(comments_sq, Recipe.id == comments_sq.c.recipe_id)
                  .having(score > 0)
                  .group_by(Recipe.id)
                  .order_by(score.desc())
                  .first())
        return result[0] if result else None

    @staticmethod
    def most_interacted_recipe_this_month():
        """
        Recipe with the most interactions (likes + comments + saves) this month.
        Returns one Recipe or None.
        """
        since = _month_start()

        likes_sq = (db.session.query(
                        Reaction.recipe_id,
                        func.count(Reaction.id).label("likes")
                    )
                    .filter(Reaction.value == 1, Reaction.created_at >= since)
                    .group_by(Reaction.recipe_id)
                    .subquery())

        comments_sq = (db.session.query(
                           Comment.recipe_id,
                           func.count(Comment.id).label("cmts")
                       )
                       .filter(Comment.created_at >= since)
                       .group_by(Comment.recipe_id)
                       .subquery())

        saves_sq = (db.session.query(
                        saved_recipes_table.c.recipe_id,
                        func.count().label("saves")
                    )
                    .filter(saved_recipes_table.c.saved_at >= since)
                    .group_by(saved_recipes_table.c.recipe_id)
                    .subquery())

        score = (
            func.coalesce(likes_sq.c.likes, 0)
            + func.coalesce(comments_sq.c.cmts, 0)
            + func.coalesce(saves_sq.c.saves, 0)
        )

        result = (db.session.query(Recipe, score.label("score"))
                  .outerjoin(likes_sq, Recipe.id == likes_sq.c.recipe_id)
                  .outerjoin(comments_sq, Recipe.id == comments_sq.c.recipe_id)
                  .outerjoin(saves_sq, Recipe.id == saves_sq.c.recipe_id)
                  .having(score > 0)
                  .group_by(Recipe.id)
                  .order_by(score.desc())
                  .first())
        return result[0] if result else None

    @staticmethod
    def most_saved(limit=6):
        """Recipes saved by the most users (all time, ≥1 save required)."""
        saves_sq = (db.session.query(
                        saved_recipes_table.c.recipe_id,
                        func.count().label("saves")
                    )
                    .group_by(saved_recipes_table.c.recipe_id)
                    .subquery())
        return (db.session.query(Recipe)
                .join(saves_sq, Recipe.id == saves_sq.c.recipe_id)
                .order_by(saves_sq.c.saves.desc(), Recipe.created_at.desc())
                .limit(limit).all())

    @staticmethod
    def fresh_this_week(limit=6):
        """Newest recipes posted in the last 7 days."""
        since = _week_ago()
        return (Recipe.query
                .filter(Recipe.created_at >= since)
                .order_by(Recipe.created_at.desc())
                .limit(limit).all())

    # ------------------------------------------------------------------ #
    #  Users: rankings                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def rising_users(limit=8):
        """
        Cooks who gained the most new followers in the last 30 days.
        Only users with ≥1 recent follow appear (truly 'rising').
        """
        since = _thirty_days_ago()
        recent_follows = (db.session.query(
                              Follow.followed_id,
                              func.count(Follow.id).label("new_followers")
                          )
                          .filter(Follow.created_at >= since)
                          .group_by(Follow.followed_id)
                          .subquery())
        return (db.session.query(User)
                .join(recent_follows, User.id == recent_follows.c.followed_id)
                .order_by(recent_follows.c.new_followers.desc(),
                          User.created_at.desc())
                .limit(limit).all())

    @staticmethod
    def top_cooks_this_month(limit=6):
        """
        Users whose recipes received the most total interactions this month.
        Interaction score = likes*3 + comments*2 + saves*1
        Only cooks with ≥1 interaction this month appear.
        """
        since = _month_start()

        likes_sq = (db.session.query(
                        Recipe.user_id,
                        func.count(Reaction.id).label("likes")
                    )
                    .join(Reaction, Recipe.id == Reaction.recipe_id)
                    .filter(Reaction.value == 1, Reaction.created_at >= since)
                    .group_by(Recipe.user_id)
                    .subquery())

        comments_sq = (db.session.query(
                           Recipe.user_id,
                           func.count(Comment.id).label("cmts")
                       )
                       .join(Comment, Recipe.id == Comment.recipe_id)
                       .filter(Comment.created_at >= since)
                       .group_by(Recipe.user_id)
                       .subquery())

        saves_sq = (db.session.query(
                        Recipe.user_id,
                        func.count().label("saves")
                    )
                    .join(saved_recipes_table,
                          Recipe.id == saved_recipes_table.c.recipe_id)
                    .filter(saved_recipes_table.c.saved_at >= since)
                    .group_by(Recipe.user_id)
                    .subquery())

        score = (
            func.coalesce(likes_sq.c.likes, 0) * 3
            + func.coalesce(comments_sq.c.cmts, 0) * 2
            + func.coalesce(saves_sq.c.saves, 0)
        )

        return (db.session.query(User, score.label("score"))
                .outerjoin(likes_sq, User.id == likes_sq.c.user_id)
                .outerjoin(comments_sq, User.id == comments_sq.c.user_id)
                .outerjoin(saves_sq, User.id == saves_sq.c.user_id)
                .having(score > 0)
                .group_by(User.id)
                .order_by(score.desc())
                .limit(limit).all())

    # ------------------------------------------------------------------ #
    #  Personalised                                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def recommended_for(user, limit=20):
        """Recommend based on preferences + who they follow."""
        prefs = user.preference
        pref_cats = prefs.get_categories() if prefs else []
        followed_ids = [f.followed_id for f in user.following.all()]

        q = Recipe.query
        if pref_cats:
            q = q.filter(Recipe.category.in_(pref_cats))
        q = q.filter(Recipe.user_id != user.id)

        recipes = q.order_by(Recipe.created_at.desc()).limit(limit).all()

        if len(recipes) < limit and followed_ids:
            extra = (Recipe.query
                     .filter(Recipe.user_id.in_(followed_ids),
                             Recipe.id.notin_([r.id for r in recipes]))
                     .order_by(Recipe.created_at.desc())
                     .limit(limit - len(recipes)).all())
            recipes.extend(extra)

        return recipes