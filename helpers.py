from datetime import date, datetime

def calculate_age(birth_date):
    if birth_date is None:
        return None
        
    birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
    today = date.today()
    age = today.year - birth.year
    
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age