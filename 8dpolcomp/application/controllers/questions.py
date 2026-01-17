
from application.models.questions import Questions


class QuestionsController:
    """
    Read-only query helpers for Questions.
    """

    def get_all(test=False):
        """
        Fetch all questions.

        Args:
            test (bool): If True, returns a small sample.

        Returns:
            list[Questions]: Question rows.
        """

        res = Questions.query.all()
        return res[:5] if test else res


    def get_num_questions():
        """
        Get total count of questions.

        Returns:
            int: number of questions.
        """

        return Questions.query.count()


    def get_texts(test=False):
        """
        Return question texts for frontend.

        Args:
            test (bool): If True, returns a small sample.

        Returns:
            list[dict]: [{"id": <int>, "text": <str>}, ...]
        """

        qs = Questions.query.all()
        texts = [{"id": q.id, "text": q.text} for q in qs]
        return texts[:5] if test else texts


    def get_scores(test=False):
        """
        Return per-question scoring weights.

        Args:
            test (bool): If True, returns a small sample.

        Returns:
            dict[int, dict[str, float]]: {question_id: {axis: weight, ...}, ...}
        """

        axes = ["society", "politics", "economics", "state", "diplomacy", "government", "technology", "religion"]

        qs = Questions.query.all()
        scores = {
            q.id: {axis: getattr(q, axis) for axis in axes}
            for q in qs
        }

        if test:
            return {k: scores[k] for k in sorted(scores.keys())[:5]}
        return scores


    def get_max_scores():
        """
        Compute maximum possible score for each axis.

        Returns:
            dict[str, float]: {axis: max_score, ...}
        """

        scores = QuestionsController.get_scores()
        if not scores:
            return {}

        max_scores = {}
        for q_id, q_scores in scores.items():
            max_scores[q_id] = {axis: abs(weight) * 2 for axis, weight in q_scores.items()}

        first = next(iter(max_scores.values()))
        axis_scores = {axis: sum(v[axis] for v in max_scores.values()) for axis in first.keys()}
        return axis_scores
