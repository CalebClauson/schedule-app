from datetime import date, datetime, timedelta

# used for students age when displaying
def calculate_age(birth_date):
    if birth_date is None:
        return None
        
    birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
    today = date.today()
    age = today.year - birth.year
    
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age

# used for buffering time between lessons
def add_minutes(time_str, minutes):
    time_obj = datetime.strptime(time_str, "%H:%M")
    new_time = time_obj + timedelta(minutes=minutes)
    return new_time.strftime("%H:%M")