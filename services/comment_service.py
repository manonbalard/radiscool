from models.models_nosql import CommentNoSQL


def add_comment(recipe_id, user_id, text):
    try:
        new_comment = CommentNoSQL(recipe_id=recipe_id, user_id=user_id, text=text)
        new_comment.save()
        return {"error": False, "message": "Comment added."}

    except Exception as e:
        return {"error": True, "message": str(e)}


def delete_comment(comment_id):
    try:
        result = CommentNoSQL.delete_comment(comment_id)

        if result.deleted_count == 1:
            return {"error": False, "message": "Comment deleted."}
        else:
            return {"error": True, "message": "Comment not found."}

    except Exception as e:
        return {"error": True, "message": str(e)}


def update_comment(comment_id, new_text):
    try:
        result = CommentNoSQL.update_comment(comment_id, new_text)

        if result.modified_count == 1:
            return {"error": False, "message": "Comment updated."}
        else:
            return {"error": True, "message": "Comment not found."}

    except Exception as e:
        return {"error": True, "message": str(e)}
