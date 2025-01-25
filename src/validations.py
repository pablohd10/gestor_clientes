import re

def validate_email(email):
    """
    Valida una dirección de email.
    Retorna True si es válida, False si no.
    """
    if not isinstance(email, str) or len(email) > 320:
        return False
    
    # Expresión regular para validar emails
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)" # https://emailregex.com/
    return bool(re.match(pattern, email)) # Si hay match, devuelve True, sino False. (bool() convierte el match en True o False)

def validate_telefono(telefono):
    """
    Valida un número de teléfono.
    Retorna True si es válido, False si no.
    """
    if not isinstance(telefono, str) or len(telefono) > 15:
        return False
    
    # Expresión regular para validar teléfonos
    pattern = r"^\d{7,15}$" # De 7 a 15 dígitos
    return bool(re.match(pattern, telefono))
