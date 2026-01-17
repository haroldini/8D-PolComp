
import json
import logging
import os
from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional

import requests
from flask import Blueprint, session, request, current_app
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from application.controllers.results import ResultsController as Results
from application.controllers.questions import QuestionsController as Questions


logger = logging.getLogger(__name__)


v = Blueprint("api", __name__)


# --------- Pydantic Schemas ---------


Axis = Literal["diplomacy", "economics", "government", "politics", "religion", "society", "state", "technology"]


class ToFormBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answers: Dict[int, int]

    @field_validator("answers")
    @classmethod
    def validate_answer_keys(cls, v):
        for q_id in v.keys():
            if not 1 <= int(q_id) <= 100:
                raise ValueError("Invalid question ID")
        return v

    @field_validator("answers")
    @classmethod
    def validate_answer_values(cls, v):
        for ans in v.values():
            if not -2 <= int(ans) <= 2:
                raise ValueError("Invalid answer value")
        return v


class ToTestBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["to_test"]


class ToInstructionsBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["to_instructions"]


class ToResultsBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    captcha: str = Field(min_length=1)
    demographics: Dict[str, Any]
    how_found: Optional[str] = None


class FiltersetModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    min_age: Optional[int] = Field(default=None, alias="min-age", ge=0, le=101)
    max_age: Optional[int] = Field(default=None, alias="max-age", ge=0, le=101)
    any_all: Literal["any", "all"] = Field(default="any", alias="any-all")
    color: str
    country: List[str] = Field(default_factory=list)
    religion: List[str] = Field(default_factory=list)
    ethnicity: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    party: List[str] = Field(default_factory=list)
    identities: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_age_range(self):
        if self.min_age is not None and self.max_age is not None:
            if self.min_age > self.max_age:
                raise ValueError("min-age cannot exceed max-age")
        return self


class FilterDataModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: Literal["random", "recent"]
    limit: int = Field(gt=0, le=10000)
    min_date: date = Field(alias="min-date")
    max_date: date = Field(alias="max-date")
    filtersets: List[FiltersetModel]

    @field_validator("min_date", "max_date", mode="before")
    @classmethod
    def parse_dates(cls, v):
        if isinstance(v, date) and not isinstance(v, datetime):
            return v
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            s = v.split("T")[0]
            return date.fromisoformat(s)
        raise ValueError("Invalid date")

    @model_validator(mode="after")
    def validate_dates(self):
        if self.min_date > self.max_date:
            raise ValueError("min-date cannot exceed max-date")
        return self


class DataApiBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["apply_filters"]
    data: Optional[dict] = None


class FilterCountBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["get_filterset_count"]
    data: dict


# --------- Internal validators ---------


class ScoresModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diplomacy: float = Field(ge=-1, le=1)
    economics: float = Field(ge=-1, le=1)
    government: float = Field(ge=-1, le=1)
    politics: float = Field(ge=-1, le=1)
    religion: float = Field(ge=-1, le=1)
    society: float = Field(ge=-1, le=1)
    state: float = Field(ge=-1, le=1)
    technology: float = Field(ge=-1, le=1)


def _load_demo_valid():
    demo_path = os.path.join(current_app.config["REL_DIR"], "application/data/demographics/demographics.json")
    with open(demo_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _validate_how_found_against_file(how_found: Any) -> tuple[str | None, str | None]:
    """
    Validate how_found against the demographics.json file schema.

    Returns:
        (validated_value, error_message)
    """

    if how_found is None or how_found == "":
        return None, None

    if not isinstance(how_found, str):
        return None, "how_found is invalid"

    try:
        demo_valid = _load_demo_valid()
    except Exception:
        logger.exception("[how_found] Failed to load demographics.json for validation")
        return None, "Validation unavailable"

    allowed = demo_valid.get("how_found", [])
    if not isinstance(allowed, list):
        return None, "Validation unavailable"

    if how_found in allowed:
        return how_found, None

    return None, f"{how_found} is not a valid how_found"


def _validate_demographics_against_file(demographics: Dict[str, Any]) -> tuple[Dict[str, Any] | None, str | None]:
    """
    Validate demographics against the demographics.json file schema.

    Returns:
        (validated_demographics, error_message)
    """

    try:
        demo_valid = _load_demo_valid()
    except Exception:
        logger.exception("[demographics] Failed to load demographics.json for validation")
        return None, "Validation unavailable"

    if not isinstance(demographics, dict):
        return None, "Demographics are invalid"

    for dem_key, dem_val in demographics.items():

        # Unknown demographic key = invalid
        # Empty demographic value = valid
        if dem_key not in demo_valid.keys():
            return None, f"{dem_key} is not a valid demographic"
        if dem_key != "identities" and dem_val == "":
            continue

        # For age key, cast to list of acceptable vals to integer
        if dem_key == "age":
            if dem_val == -1:
                continue
            try:
                allowed = [int(age_val) for age_val in demo_valid[dem_key]]
                if int(dem_val) in allowed:
                    continue
            except Exception:
                return None, f"{dem_val} is not a valid {dem_key}"
            return None, f"{dem_val} is not a valid {dem_key}"

        # For party key - acceptable vals are contained within countries
        elif dem_key == "party":
            acceptable_vals = []
            for country, party_list in demo_valid["party"].items():
                for party in party_list:
                    acceptable_vals.append(country + "-" + party)

            if dem_val in acceptable_vals:
                continue
            return None, f"{dem_val} is not a valid {dem_key}"

        # For identity key, just check for valid values across each identity in list
        elif dem_key == "identities":
            if dem_val == []:
                continue
            if not isinstance(dem_val, list):
                return None, "Identities must be a list"
            cleaned = []
            for identity in dem_val:
                if identity == "":
                    continue
                if identity not in demo_valid[dem_key]:
                    return None, f"{identity} is not a valid {dem_key}"
                cleaned.append(identity)
            demographics["identities"] = cleaned

        # For other keys - just check for valid values inside demo_valid for key.
        elif dem_val not in demo_valid[dem_key]:
            return None, f"{dem_val} is not a valid {dem_key}"

    return demographics, None


def _validate_session_answers_and_scores() -> tuple[Dict[str, Any] | None, str | None]:
    """
    Validate session["answers"] and session["results"] before DB insertion.

    Returns:
        (validated_payload, error_message)
    """

    if "answers" not in session or "results" not in session:
        return None, "Session expired. Please refresh and try again."

    answers = session.get("answers")
    scores = session.get("results")

    try:
        parsed_answers = ToFormBody(answers={int(k): int(v) for k, v in answers.items()}).answers
    except Exception:
        logger.warning("[session validate] answers invalid")
        return None, "Session expired. Please refresh and try again."

    try:
        parsed_scores = ScoresModel(**scores).model_dump()
    except Exception:
        logger.warning("[session validate] scores invalid")
        return None, "Session expired. Please refresh and try again."

    return {"answers": parsed_answers, "scores": parsed_scores}, None


def get_answer_counts():
    """
    Compute per-question answer counts for the current session answers.

    Args:
        None

    Returns:
        None

    Raises:
        KeyError: If session["answers"] is missing.
    """

    session["answer_counts"] = {
        str(q_id): {"Strongly Agree": 0, "Agree": 0, "Neutral": 0, "Disagree": 0, "Strongly Disagree": 0}
        for q_id in session["answers"].keys()
    }
    keys = {2: "Strongly Agree", 1: "Agree", 0: "Neutral", -1: "Disagree", -2: "Strongly Disagree"}
    for q_id, q_ans in session["answers"].items():
        session["answer_counts"][str(q_id)][keys[q_ans]] += 1


def calculate_results(answers: Dict[int, int], scoring: Dict[int, Dict[str, float]]) -> Dict[str, float]:
    """
    Convert answers -> axis score result dict.

    Args:
        answers (dict[int, int]): question_id -> answer value
        scoring (dict[int, dict[str, float]]): question_id -> axis weights

    Returns:
        dict: axis -> score (rounded)

    Raises:
        KeyError: If required answers are missing.
    """

    missing = set(scoring.keys()) - set(answers.keys())
    if missing:
        raise KeyError("Missing answers")

    r_scores = {}
    for q_id, q_scores in scoring.items():
        r_scores[q_id] = {axis: q_score * answers[q_id] for axis, q_score in q_scores.items()}

    first = next(iter(r_scores.values()))
    r_sums = {axis: sum([v[axis] for v in r_scores.values()]) for axis in first.keys()}

    max_scores = Questions.get_max_scores()
    return {axis: round(val / max_scores[axis], 2) for axis, val in r_sums.items()}


# --------- Routes ---------


@v.route("/api/to_form", methods=["POST"])
def to_form():
    """
    Accept answers payload, calculate axis results, and move user to demographics form.

    Args:
        JSON body:
            answers (dict[int,int]): question_id -> answer

    Returns:
        dict: {"status": "success"}

    Raises:
        400: Invalid request body.
        500: Unexpected server error.
    """

    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return {"status": "Invalid request. Please refresh and try again."}, 400

        try:
            body = ToFormBody(**payload)
        except ValidationError as e:
            logger.warning("[/api/to_form] ValidationError: %s", str(e))
            return {"status": "Invalid request. Please refresh and try again."}, 400

        try:
            scoring = Questions.get_scores(test=False)
        except Exception:
            logger.exception("[/api/to_form] Failed to load question scoring data")
            return {"status": "Server error. Please refresh and try again."}, 500

        answers = {int(q): int(a) for q, a in body.answers.items()}

        if set(answers.keys()) != set(scoring.keys()):
            logger.warning(
                "[/api/to_form] Answer keys mismatch: required=%s provided=%s",
                len(scoring.keys()),
                len(answers.keys()),
            )
            return {"status": "Invalid request. Please refresh and try again."}, 400

        results = calculate_results(answers, scoring)

        session["answers"] = answers
        session["results"] = results
        session["template"] = "form"

        return {"status": "success"}, 200

    except Exception:
        logger.exception("[/api/to_form] Unhandled error")
        return {"status": "Server error. Please refresh and try again."}, 500


@v.route("/api/to_test", methods=["POST"])
def to_test():
    """
    Move user state into the test page.

    Args:
        JSON body:
            action (str): must be "to_test"

    Returns:
        dict: {"status": "success"}

    Raises:
        400: Invalid request.
        500: Unexpected server error.
    """

    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return {"status": "Invalid request. Please refresh and try again."}, 400

        try:
            ToTestBody(**payload)
        except ValidationError as e:
            logger.warning("[/api/to_test] ValidationError: %s", str(e))
            return {"status": "Invalid request. Please refresh and try again."}, 400

        session["template"] = "test"
        return {"status": "success"}, 200

    except Exception:
        logger.exception("[/api/to_test] Unhandled error")
        return {"status": "Server error. Please refresh and try again."}, 500


@v.route("/api/to_instructions", methods=["POST"])
def to_instructions():
    """
    Reset user flow back to instructions page.

    Args:
        JSON body:
            action (str): must be "to_instructions"

    Returns:
        dict: {"status": "success"}

    Raises:
        400: Invalid request.
        500: Unexpected server error.
    """

    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return {"status": "Invalid request. Please refresh and try again."}, 400

        try:
            ToInstructionsBody(**payload)
        except ValidationError as e:
            logger.warning("[/api/to_instructions] ValidationError: %s", str(e))
            return {"status": "Invalid request. Please refresh and try again."}, 400

        session["template"] = "instructions"
        return {"status": "success"}, 200

    except Exception:
        logger.exception("[/api/to_instructions] Unhandled error")
        return {"status": "Server error. Please refresh and try again."}, 500


@v.route("/api/to_results", methods=["POST"])
def to_results():
    """
    Finalise a test submission and persist results.

    Validates captcha, validates session results/answers, validates demographics payload,
    and (in non-dev) inserts into DB.

    Args:
        JSON body:
            captcha (str): hCaptcha token.
            demographics (dict): User demographics data.
            how_found (str): Optional selection describing how the app was found.

    Returns:
        dict: {"status": "success", "results_id": <id>} on success
        dict: {"status": "<message>"} on error

    Raises:
        400: Invalid request / missing required fields.
        401: Captcha failure / validation failure.
        503: Captcha verification unavailable.
        500: Unexpected server error.
    """

    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return {"status": "Invalid request. Please refresh and try again."}, 400

        try:
            body = ToResultsBody(**payload)
        except ValidationError as e:
            logger.warning("[/api/to_results] ValidationError: %s", str(e))
            return {"status": "Invalid request. Please refresh and try again."}, 400

        # Validate captcha
        try:
            resp = requests.post(
                url=current_app.config["HCAPTCHA_VERIFY_URL"],
                data={
                    "secret": current_app.config["HCAPTCHA_SECRET_KEY"],
                    "response": body.captcha,
                    "remoteip": request.remote_addr
                },
                timeout=3
            )
            verify_response = resp.json()
        except (requests.RequestException, ValueError):
            logger.warning("[/api/to_results] Captcha verification unavailable")
            return {"status": "Captcha verification unavailable. Please try again."}, 503

        if not verify_response.get("success"):
            logger.info("[/api/to_results] Captcha verification failed")
            return {"status": "Captcha verification failed. Please try again."}, 401

        # Validate session answers/results
        session_payload, err = _validate_session_answers_and_scores()
        if err:
            logger.warning("[/api/to_results] %s", err)
            return {"status": err}, 400

        # Validate demographics payload against file
        demographics, dem_err = _validate_demographics_against_file(body.demographics or {})
        if dem_err:
            logger.warning("[/api/to_results] Demographics validation failed: %s", dem_err)
            return {"status": f"Result Validation Failed: {dem_err}. Refresh and try again."}, 401

        # Validate how_found against file
        how_found, hf_err = _validate_how_found_against_file(body.how_found)
        if hf_err:
            logger.warning("[/api/to_results] how_found validation failed: %s", hf_err)
            return {"status": f"Result Validation Failed: {hf_err}. Refresh and try again."}, 401

        # Count answers for each question to add user data to pie
        try:
            get_answer_counts()
        except Exception:
            logger.exception("[/api/to_results] Failed to compute answer counts")
            return {"status": "Server error. Please refresh and try again."}, 500

        # Add user's result to database
        try:
            if current_app.config.get("DEV"):
                session["results_id"] = 1006
            else:
                result_row = {
                    "demographics": demographics,
                    "scores": session_payload["scores"],
                    "answers": session_payload["answers"],
                    "how_found": how_found
                }
                session["results_id"] = Results.add_result(result_row, return_id=True) - 1  # -1 for 0-start indexed db IDs
        except Exception:
            logger.exception("[/api/to_results] Failed to store result")
            return {"status": "Server error. Please refresh and try again."}, 500

        session["template"] = "instructions"
        return {"status": "success", "results_id": session["results_id"]}, 200

    except Exception:
        logger.exception("[/api/to_results] Unhandled error")
        return {"status": "Server error. Please refresh and try again."}, 500


@v.route("/api/data", methods=["POST"])
def data_api():
    """
    Data API used by the frontend to:
      - apply_filters

    Args:
        JSON body:
            action (str)
            data (dict) required for apply_filters

    Returns:
        JSON string: {"status": "...", ...}

    Raises:
        401: Validation failure / unknown action
        500: Server error
    """

    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return json.dumps({"status": "Invalid request. Please refresh and try again."}), 400

        try:
            body = DataApiBody(**payload)
        except ValidationError as e:
            logger.warning("[/api/data] ValidationError: %s", str(e))
            return json.dumps({"status": "Invalid request. Please refresh and try again."}), 400

        if body.action == "apply_filters":
            if not isinstance(body.data, dict):
                return json.dumps({"status": "Filterset validation failed: Invalid filters"}), 401

            try:
                filt = FilterDataModel(**body.data)
            except ValidationError as e:
                logger.warning("[/api/data] FilterData ValidationError: %s", str(e))
                return json.dumps({"status": "Filterset validation failed: Invalid filters"}), 401

            filter_data = filt.model_dump(by_alias=True)
            datasets = Results.get_filtered_datasets(filter_data)

            if "answer_counts" in session:
                datasets.insert(0, {
                    "name": "your_results",
                    "label": "Your Results",
                    "custom_dataset": False,
                    "result_id": session.get("results_id"),
                    "color": "salmon",
                    "count": 1,
                    "point_props": [1, 8],
                    "all_scores": [session.get("results")],
                    "answer_counts": session.get("answer_counts")
                })

            return json.dumps({"status": "success", "compass_datasets": datasets}), 200

        return json.dumps({"status": "Error: Unknown action. Contact the developer if you think this is a mistake."}), 401

    except Exception:
        logger.exception("[/api/data] Unhandled error")
        return json.dumps({"status": "Server error. Please refresh and try again."}), 500


@v.route("/api/get_filterset_count", methods=["POST"])
def get_filterset_count():
    """
    Return counts for each filterset without returning datasets.

    Args:
        JSON body:
            action (str): must be "get_filterset_count"
            data (dict): filter data object

    Returns:
        JSON string: {"status": "success", "counts": {...}}

    Raises:
        401: Validation failure.
        500: Server error.
    """

    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return json.dumps({"status": "Invalid request. Please refresh and try again."}), 400

        try:
            body = FilterCountBody(**payload)
        except ValidationError as e:
            logger.warning("[/api/get_filterset_count] ValidationError: %s", str(e))
            return json.dumps({"status": "Invalid request. Please refresh and try again."}), 400

        try:
            filt = FilterDataModel(**body.data)
        except ValidationError as e:
            logger.warning("[/api/get_filterset_count] FilterData ValidationError: %s", str(e))
            return json.dumps({"status": "Filterset validation failed: Invalid filters"}), 401

        filter_data = filt.model_dump(by_alias=True)
        counts = Results.get_filtered_dataset_count(filter_data)
        return json.dumps({"status": "success", "counts": counts}), 200

    except Exception:
        logger.exception("[/api/get_filterset_count] Unhandled error")
        return json.dumps({"status": "Server error. Please refresh and try again."}), 500
