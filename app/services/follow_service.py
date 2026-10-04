from app.extensions import db
from app.models import Follow, User


class FollowService:

    @staticmethod
    def follow(follower, target):
        if follower.id == target.id:
            raise ValueError("Cannot follow yourself")
        if Follow.query.filter_by(follower_id=follower.id, followed_id=target.id).first():
            return False
        db.session.add(Follow(follower_id=follower.id, followed_id=target.id))
        db.session.commit()
        return True

    @staticmethod
    def unfollow(follower, target):
        rel = Follow.query.filter_by(follower_id=follower.id, followed_id=target.id).first()
        if rel:
            db.session.delete(rel)
            db.session.commit()
            return True
        return False

    @staticmethod
    def followers(user):
        return [f.follower for f in user.followers.all()]

    @staticmethod
    def following(user):
        return [f.followed for f in user.following.all()]

    @staticmethod
    def is_following(follower, target):
        return Follow.query.filter_by(
            follower_id=follower.id, followed_id=target.id
        ).first() is not None