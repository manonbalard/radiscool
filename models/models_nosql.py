from extensions import mongo_db
from datetime import datetime
from bson import ObjectId


class CommentNoSQL:
    """Represents a comment for a recipe stored in MongoDB (NoSQL)."""

    def __init__(self, recipe_id, user_id, text):
        """
        Initialize a new comment object.

        :param recipe_id: ID of the recipe the comment is associated with (from SQL database).
        :param user_id: ID of the user who made the comment (from SQL database).
        :param text: The content of the comment.
        """
        self.recipe_id = recipe_id  # ID of the recipe in the SQL database
        self.user_id = user_id  # ID of the user in the SQL database
        self.text = text  # Comment text
        self.date = datetime.utcnow()  # Timestamp of when the comment was created

    def save(self):
        """
        Save the current comment to the MongoDB database.

        :return: The result of the insert operation from MongoDB.
        """
        comment_data = {
            "recipe_id": self.recipe_id,
            "user_id": self.user_id,
            "text": self.text,
            "date": self.date,
        }
        return mongo_db.comments.insert_one(comment_data)

    @staticmethod
    def get_comments_by_recipe(recipe_id):
        """
        Retrieve all comments for a specific recipe.

        :param recipe_id: The ID of the recipe for which comments are retrieved.
        :return: A list of comments associated with the specified recipe ID.
        """
        # Return list of comments for a recipe from the MongoDB database
        return list(mongo_db.comments.find({"recipe_id": recipe_id}))

    @staticmethod
    def delete_comment(comment_id):
        """
        Delete a specific comment by its MongoDB ObjectId.

        :param comment_id: The ID of the comment to be deleted.
        :return: The result of the delete operation from MongoDB.
        """
        # Delete a comment by its MongoDB ObjectId
        return mongo_db.comments.delete_one({"_id": ObjectId(comment_id)})

    @staticmethod
    def update_comment(comment_id, new_text):
        """
        Update the text of a specific comment and refresh its timestamp.

        :param comment_id: The ID of the comment to be updated.
        :param new_text: The new text that will replace the current comment.
        :return: The result of the update operation from MongoDB.
        """
        # Update the comment text and date
        return mongo_db.comments.update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$set": {"text": new_text, "date": datetime.utcnow()}
            },  # Update with new text and timestamp
        )
