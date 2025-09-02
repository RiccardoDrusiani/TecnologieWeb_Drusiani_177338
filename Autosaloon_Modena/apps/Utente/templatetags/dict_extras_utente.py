from django import template
register = template.Library()

@register.filter
def get_username_by_id(user_dict, user_id):
    """
    user_dict: dict {user_id: username}
    user_id: id da cercare
    """
    # Gestione robusta: prova sia int che str
    if user_dict is None or user_id is None:
        return "Sconosciuto"
    return (
        user_dict.get(user_id)
        or user_dict.get(str(user_id))
        or user_dict.get(int(user_id))
        or "Sconosciuto"
    )
