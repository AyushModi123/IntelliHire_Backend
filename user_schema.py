def user_insert_serializer(user: str, employer: str, email: str, hashed_password: str) -> dict:
    return {
        'name': user, 'employer': employer, 'email': email, 'password': hashed_password
        }