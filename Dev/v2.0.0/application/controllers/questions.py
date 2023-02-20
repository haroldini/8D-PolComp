from application.models.questions import Questions

class QuestionsController:
    def get_all():
        return Questions.query.all()

    def get_texts(test=False):
        texts = [
            {
            "id": question.id,
            "text": question.text 
            } for question in Questions.query.all()
        ]
        return texts[:5] if test else texts
    
    def get_downvotes(test=False):
        downvotes = [
            {
            "id": question.id,
            "downvotes": question.downvotes 
            } for question in Questions.query.all()
        ]
        return downvotes[:5] if test else downvotes

    def get_scores(test=False):
        scores = [
            {
            axis: getattr(question, axis) for axis in [
                "id", "society", "politics", "economics", "state", "diplomacy", "government", "technology", "religion"
                ]
            } for question in Questions.query.all() 
        ]
        return scores[:5] if test else scores