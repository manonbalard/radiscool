from models.models_nosql import CommentNoSQL


def add_comment(recipe_id, user_id, text):
    """
    Add a new comment to a recipe.

    Args:
        recipe_id (str): The ID of the recipe being commented on.
        user_id (str): The ID of the user adding the comment.
        text (str): The text content of the comment.

    Returns:
        dict: A dictionary with error status and a message indicating success or failure.
    """
    try:
        # Create a new comment object and save it to the database.
        new_comment = CommentNoSQL(recipe_id=recipe_id, user_id=user_id, text=text)
        new_comment.save()
        return {"error": False, "message": "Comment added."}

    except Exception as e:
        # Handle any exceptions that occur during the save operation.
        return {"error": True, "message": str(e)}


def delete_comment(comment_id):
    """
    Delete a comment based on its ID.

    Args:
        comment_id (str): The ID of the comment to delete.

    Returns:
        dict: A dictionary with error status and a message indicating success or failure.
    """
    try:
        # Attempt to delete the comment by its ID.
        result = CommentNoSQL.delete_comment(comment_id)

        if result.deleted_count == 1:
            # Successful deletion if exactly one comment was deleted.
            return {"error": False, "message": "Comment deleted."}
        else:
            # Handle cases where no comment was found to delete.
            return {"error": True, "message": "Comment not found."}

    except Exception as e:
        # Handle any exceptions that occur during the delete operation.
        return {"error": True, "message": str(e)}


def update_comment(comment_id, new_text):
    """
    Update the text of an existing comment.

    Args:
        comment_id (str): The ID of the comment to update.
        new_text (str): The new text content for the comment.

    Returns:
        dict: A dictionary with error status and a message indicating success or failure.
    """
    try:
        # Attempt to update the comment's text using its ID.
        result = CommentNoSQL.update_comment(comment_id, new_text)

        if result.modified_count == 1:
            # Successful update if exactly one comment was modified.
            return {"error": False, "message": "Comment updated."}
        else:
            # Handle cases where no comment was found to update.
            return {"error": True, "message": "Comment not found."}

    except Exception as e:
        # Handle any exceptions that occur during the update operation.
        return {"error": True, "message": str(e)}
