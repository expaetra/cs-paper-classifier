import joblib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CSClassifier:
    def __init__(self):
        logger.info("Loading trained models...")
        base_path = Path(__file__).resolve().parent

        # Load discipline model & vectorizer
        self.discipline_model = joblib.load(base_path / "logreg_disc_optuna.pkl")
        self.discipline_vectorizer = joblib.load(base_path / "tfidf_disc_optuna.pkl")

        # Load field model & vectorizer
        self.field_model = joblib.load(base_path / "logreg_field_optuna.pkl")
        self.field_vectorizer = joblib.load(base_path/ "tfidf_field_optuna.pkl")

        # Taxonomy mapping field to discipline
        self.taxonomy = {
            'cs.LG': {'field': 'Machine Learning', 'discipline': 'Artificial Intelligence'},
            'cs.CV': {'field': 'Computer Vision', 'discipline': 'Computer Imaging and Vision'},
            'cs.AI': {'field': 'General Artificial Intelligence', 'discipline': 'Artificial Intelligence'},
            'cs.CL': {'field': 'Natural Language Processing', 'discipline': 'Artificial Intelligence'},
            'cs.IT': {'field': 'Information Theory', 'discipline': 'Communication'},
            'cs.RO': {'field': 'General Robotics', 'discipline': 'Robotics'},
            'cs.CR': {'field': 'Cryptography', 'discipline': 'Cybersecurity'},
            'cs.HC': {'field': 'General Human-Computer Interaction', 'discipline': 'Human-Computer Interaction'},
            'cs.DS': {'field': 'Data Structures and Algorithms', 'discipline': 'Theory of Computation'},
            'cs.DC': {'field': 'Distributed Computer Systems', 'discipline': 'Distributed Systems'},
            'cs.CY': {'field': 'Computers and Society', 'discipline': 'Social Computing'},
            'cs.NI': {'field': 'General Computer Networks', 'discipline': 'Computer Networks'},
            'cs.SE': {'field': 'General Software Engineering', 'discipline': 'Software Engineering'},
            'cs.IR': {'field': 'General Information Retrieval', 'discipline': 'Information Retrieval'},
            'cs.SI': {'field': 'Social Networks', 'discipline': 'World Wide Web'},
            'cs.SD': {'field': 'Sound and Signal Processing', 'discipline': 'Multimedia'},
            'cs.LO': {'field': 'Formal Logic', 'discipline': 'Artificial Intelligence'},
            'cs.NE': {'field': 'Neural Networks', 'discipline': 'Artificial Intelligence'},
            'cs.DM': {'field': 'Discrete Mathematics', 'discipline': 'Theory of Computation'},
            'cs.GT': {'field': 'Game Theory', 'discipline': 'Artificial Intelligence'},
            'cs.CC': {'field': 'Computational Complexity', 'discipline': 'Theory of Computation'},
            'cs.MA': {'field': 'Multiagent Systems', 'discipline': 'Artificial Intelligence'},
            'cs.DB': {'field': 'Database Systems', 'discipline': 'Computer Systems'},
            'cs.CE': {'field': 'Computational Engineering', 'discipline': 'Computational Science'},
            'cs.PL': {'field': 'Programming Languages', 'discipline': 'Computer Programming'},
            'cs.MM': {'field': 'General Multimedia', 'discipline': 'Multimedia'},
            'cs.CG': {'field': 'Computational Geometry', 'discipline': 'Computer Graphics'},
            'cs.AR': {'field': 'Hardware Architecture', 'discipline': 'Computer Hardware'},
            'cs.ET': {'field': 'Emerging Technologies', 'discipline': 'Emerging Technologies'},
            'cs.DL': {'field': 'Digital Libraries', 'discipline': 'World Wide Web'},
            'cs.FL': {'field': 'Formal Languages and Automata Theory', 'discipline': 'Theoretical Computer Science'},
            'cs.PF': {'field': 'Performance', 'discipline': 'Computer Systems'},
        }

        # Reverse lookup: field name to discipline name
        self.field_to_discipline = {
            value["field"]: value["discipline"]
            for value in self.taxonomy.values()
        }

    def predict_discipline(self, text: str) -> dict:
        logger.debug("Running discipline prediction")
        X = self.discipline_vectorizer.transform([text])
        probs = self.discipline_model.predict_proba(X)[0]
        classes = self.discipline_model.classes_

        sorted_pairs = sorted(
            zip(classes, probs),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        return {
            "prediction": sorted_pairs[0][0],
            "probabilities": {
                cls: float(prob)
                for cls, prob in sorted_pairs
            },
        }

    def predict_field(self, text: str) ->dict:
        logger.debug("Running field prediction")
        X = self.field_vectorizer.transform([text])
        probs = self.field_model.predict_proba(X)[0]
        classes = self.field_model.classes_

        sorted_pairs = sorted(
            zip(classes, probs),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        return {
            "prediction": sorted_pairs[0][0],
            "probabilities": {
                cls: float(prob)
                for cls, prob in sorted_pairs
            },
        }

    def rerank_discipline_with_taxonomy(self, discipline_prediction: dict, field_prediction: dict) -> dict:
        predicted_field = field_prediction["prediction"]
        expected_discipline = self.field_to_discipline.get(predicted_field)

        if not expected_discipline:
            discipline_prediction["taxonomy_match"] = None
            discipline_prediction["taxonomy_expected_discipline"] = None
            return discipline_prediction

        probabilities = discipline_prediction["probabilities"]
        current_top = discipline_prediction["prediction"]

        discipline_prediction["taxonomy_expected_discipline"] = expected_discipline
        discipline_prediction["taxonomy_match"] = (current_top == expected_discipline)

        # Only rerank if expected discipline is alraedy in top 3 and close to the top result
        if expected_discipline in probabilities:
            current_top_prob = probabilities[current_top]
            expected_prob = probabilities[expected_discipline]

            # Promote only if close enough
            if current_top != expected_discipline and (current_top_prob - expected_prob) <= 0.05:
                reordered = [(expected_discipline, expected_prob)]
                for label, prob in probabilities.items():
                    if label !=expected_discipline:
                        reordered.append((label, prob))

                discipline_prediction["prediction"] = expected_discipline
                discipline_prediction["probabilities"] = {
                    label: float(prob)
                    for label, prob in reordered
                }
                discipline_prediction["taxonomy_match"] = True
                discipline_prediction["taxonomy_reranked"] = True
            else:
                discipline_prediction["taxonomy_reranked"] = False
        else:
            discipline_prediction["taxonomy_reranked"] = False

        return discipline_prediction