def get_age_text(age):
    if 5 <= age <= 20:
        word = 'лет'
    elif age % 10 in [2, 3, 4]:
        word = 'года'
    elif age % 10 == 1:
        word = 'год'
    else:
        word = 'лет'

    return '%d %s' % (age, word)