from application.models.questions import Questions

class QuestionsController:
    def get_all(test=False):
        return Questions.query.all()[:5] if test else Questions.query.all()
    
    def get_num_questions():
        return len(Questions.query.all())

    # Returns [{question: text}, ...]
    def get_texts(test=False):
        texts = [
            {
            "id": question.id,
            "text": question.text 
            } for question in Questions.query.all()
        ]
        return texts[:5] if test else texts
    
    # Returns {question: {society: scores, ...}, ...} 
    def get_scores(test=False):
        scores = { getattr(question, "id"): {
            axis: getattr(question, axis) for axis in [
                "society", "politics", "economics", "state", "diplomacy", "government", "technology", "religion"
                ]
            } for question in Questions.query.all() }
        
        return {k: scores[k] for k in sorted(scores.keys())[:5]} if test else scores

    # Returns {axis: sum of scores, ...}
    def get_max_scores():
        max_scores = {}
        for q_id, q_scores in QuestionsController.get_scores().items():
            max_scores[q_id] = { axis: abs(q_score)*2 for axis, q_score in q_scores.items() }   
        axis_scores = { axis: sum([ v[axis] for v in max_scores.values() ]) for axis in max_scores[1].keys() }
        return axis_scores