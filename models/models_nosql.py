from extensions import mongo_db
from datetime import datetime
from bson import ObjectId

class CommentNoSQL:
    def __init__(self, recipe_id, user_id, text):
        self.recipe_id = recipe_id  # ID de la recette dans la base SQL
        self.user_id = user_id  # ID de l'utilisateur dans la base SQL
        self.text = text
        self.date = datetime.utcnow()

    def save(self):
        comment_data = {
            "recipe_id": self.recipe_id,
            "user_id": self.user_id,
            "text": self.text,
            "date": self.date
        }
        return mongo_db.comments.insert_one(comment_data)

    @staticmethod
    def get_comments_by_recipe(recipe_id):
        # Return list of comments for a recipe
        return list(mongo_db.comments.find({"recipe_id": recipe_id}))

    @staticmethod
    def delete_comment(comment_id):
        # Delete a comment by its MongoDB ObjectId
        return mongo_db.comments.delete_one({"_id": ObjectId(comment_id)})

    @staticmethod
    def update_comment(comment_id, new_text):
        # Update the comment text and date
        return mongo_db.comments.update_one(
            {"_id": ObjectId(comment_id)},
            {"$set": {"text": new_text, "date": datetime.utcnow()}}
        )
