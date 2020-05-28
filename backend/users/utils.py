def user_has_completed_profile(user):
    profile = user.profile
    if not profile.name:
        return False
    if not profile.phone_number:
        return False
    return True
