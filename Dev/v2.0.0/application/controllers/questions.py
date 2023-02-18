from application.models.questions import Questions

def get_all():
    return Questions.query.all()
