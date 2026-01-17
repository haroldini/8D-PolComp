
import logging

from application.models.questions import Questions


logger = logging.getLogger(__name__)


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

        try:
            res = Questions.query.all()
            return res[:5] if test else res
        except Exception:
            logger.exception("[QuestionsController.get_all] Failed")
            raise


    def get_num_questions():
        """
        Get total count of questions.

        Returns:
            int: number of questions.
        """

        try:
            return len(Questions.query.all())
        except Exception:
            logger.exception("[QuestionsController.get_num_questions] Failed")
            raise


    def get_texts(test=False):
        """
        Return question texts for frontend.

        Args:
            test (bool): If True, returns a small sample.

        Returns:
            list[dict]: [{"id": <int>, "text": <str>}, ...]
        """

        try:
            qs = Questions.query.all()
            texts = [
                {
                    "id": question.id,
                    "text": question.text
                } for question in qs
            ]
            return texts[:5] if test else texts
        except Exception:
            logger.exception("[QuestionsController.get_texts] Failed")
            raise


    def get_scores(test=False):
        """
        Return per-question scoring weights.

        Args:
            test (bool): If True, returns a small sample.

        Returns:
            dict[int, dict[str, float]]: {question_id: {axis: weight, ...}, ...}
        """

        try:
            qs = Questions.query.all()
            scores = {
                getattr(question, "id"): {
                    axis: getattr(question, axis) for axis in [
                        "society", "politics", "economics", "state", "diplomacy", "government", "technology", "religion"
                    ]
                } for question in qs
            }

            if test:
                return {k: scores[k] for k in sorted(scores.keys())[:5]}
            return scores

        except Exception:
            logger.exception("[QuestionsController.get_scores] Failed")
            raise


    def get_max_scores():
        """
        Compute maximum possible score for each axis.

        Returns:
            dict[str, float]: {axis: max_score, ...}
        """

        try:
            max_scores = {}
            for q_id, q_scores in QuestionsController.get_scores().items():
                max_scores[q_id] = {axis: abs(q_score) * 2 for axis, q_score in q_scores.items()}
            axis_scores = {axis: sum([v[axis] for v in max_scores.values()]) for axis in max_scores[1].keys()}
            return axis_scores
        except Exception:
            logger.exception("[QuestionsController.get_max_scores] Failed")
            raise
