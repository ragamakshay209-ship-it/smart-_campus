import bcrypt
from utils.database import get_user_by_email, add_user, update_user

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def register_user(name, email, password, role):
    """Registers a new user, checking for duplicates and hashing the password."""
    # Ensure inputs are clean
    name = name.strip()
    email = email.strip().lower()
    
    if not name or not email or not password or not role:
        return False, "All fields are required."
        
    # Check for duplicate user
    if get_user_by_email(email):
        return False, "User with this email address already exists."
        
    hashed = hash_password(password)
    user_data = {
        "name": name,
        "email": email,
        "password": hashed,
        "role": role,
        "profile_picture": None
    }
    
    if add_user(user_data):
        return True, "User registered successfully."
    else:
        return False, "Error writing to database. Please try again."

def authenticate_user(email, password):
    """Checks user credentials and returns a success flag along with the user info if valid."""
    email = email.strip().lower()
    user = get_user_by_email(email)
    
    if not user:
        return False, "Invalid email or password.", None
        
    if check_password(password, user.get("password")):
        return True, "Authentication successful.", user
    else:
        return False, "Invalid email or password.", None

def update_user_profile(email, name, password=None, profile_picture_base64=None):
    """Updates user name, password (if provided), and profile picture (base64 string)."""
    updated_fields = {
        "name": name.strip()
    }
    if password and len(password.strip()) > 0:
        updated_fields["password"] = hash_password(password)
    if profile_picture_base64:
        updated_fields["profile_picture"] = profile_picture_base64
        
    if update_user(email, updated_fields):
        # Fetch updated user object
        updated_user = get_user_by_email(email)
        return True, "Profile updated successfully.", updated_user
    else:
        return False, "Failed to update profile.", None
