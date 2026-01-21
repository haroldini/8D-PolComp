
import json
import logging
import os
from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

import requests
from flask import Blueprint, session, request, current_app
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from application.controllers.results import ResultsController as Results
from application.controllers.questions import QuestionsController as Questions


logger = logging.getLogger(__name__)


v = Blueprint("api", __name__)


Axis = Literal["diplomacy", "economics", "government", "politics", "religion", "society", "state", "technology"]


class ToFormBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

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


class ToResultsBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    captcha: str = Field(min_length=1)
    demographics: Dict[str, Any]
    how_found: Optional[str] = None


class FiltersetModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    label: str
    min_age: Optional[int] = Field(default=None, alias="min-age", ge=0, le=101)
    max_age: Optional[int] = Field(default=None, alias="max-age", ge=0, le=101)
    any_all: Literal["any", "all"] = Field(default="any", alias="any-all")
    color: str

    # Group tests
    group_ids: List[UUID] = Field(default_factory=list, alias="group-ids")

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
    model_config = ConfigDict(extra="ignore")

    order: Literal["random", "recent"]
    limit: int = Field(gt=0, le=2500)
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
    model_config = ConfigDict(extra="ignore")

    data: FilterDataModel


class FilterCountBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: FilterDataModel


class ScoresModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

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


def _flatten_party_values(demo_party: Any) -> set[str]:
    """
    Return all acceptable party values.

    Supports BOTH formats:

      Legacy:
        "party": { "United States": ["Democratic Party", ...] }
        -> acceptable value stored in DB is "United States-Democratic Party"

      New:
        "party": { "United States": [{"label": "...", "value": "United States-Democratic Party"}] }
        -> acceptable value stored in DB is exactly the entry's "value"

    """
    acceptable: set[str] = set()

    if not isinstance(demo_party, dict):
        return acceptable

    for country_key, party_list in demo_party.items():
        if not isinstance(party_list, list):
            continue

        for p in party_list:
            # Legacy string party name -> build legacy storage format
            if isinstance(p, str):
                acceptable.add(f"{country_key}-{p}")
                continue

            # New object format -> use value directly
            if isinstance(p, dict):
                v = p.get("value")
                if isinstance(v, str) and v.strip():
                    acceptable.add(v.strip())
                    continue

                # If "value" is missing, fall back to label in legacy scheme
                lbl = p.get("label")
                if isinstance(lbl, str) and lbl.strip():
                    acceptable.add(f"{country_key}-{lbl.strip()}")

    return acceptable


def _validate_how_found_against_file(how_found: Any) -> tuple[str | None, str | None]:
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
    try:
        demo_valid = _load_demo_valid()
    except Exception:
        logger.exception("[demographics] Failed to load demographics.json for validation")
        return None, "Validation unavailable"

    if not isinstance(demographics, dict):
        return None, "Demographics are invalid"

    for dem_key, dem_val in demographics.items():

        if dem_key not in demo_valid.keys():
            return None, f"{dem_key} is not a valid demographic"
        if dem_key != "identities" and dem_val == "":
            continue

        if dem_key == "age":
            if dem_val == -1:
                continue

            # Frontend includes "Over 100" option as 101
            if int(dem_val) == 101:
                continue

            try:
                allowed = [int(age_val) for age_val in demo_valid[dem_key]]
                if int(dem_val) in allowed:
                    continue
            except Exception:
                return None, f"{dem_val} is not a valid {dem_key}"
            return None, f"{dem_val} is not a valid {dem_key}"

        elif dem_key == "party":
            acceptable_vals = _flatten_party_values(demo_valid.get("party"))
            if dem_val in acceptable_vals:
                continue
            return None, f"{dem_val} is not a valid {dem_key}"

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

        elif dem_val not in demo_valid[dem_key]:
            return None, f"{dem_val} is not a valid {dem_key}"

    return demographics, None


def _validate_session_answers_and_scores() -> tuple[Dict[str, Any] | None, str | None]:
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
    session["answer_counts"] = {
        str(q_id): {"Strongly Agree": 0, "Agree": 0, "Neutral": 0, "Disagree": 0, "Strongly Disagree": 0}
        for q_id in session["answers"].keys()
    }
    keys = {2: "Strongly Agree", 1: "Agree", 0: "Neutral", -1: "Disagree", -2: "Strongly Disagree"}
    for q_id, q_ans in session["answers"].items():
        session["answer_counts"][str(q_id)][keys[q_ans]] += 1


def calculate_results(answers: Dict[int, int], scoring: Dict[int, Dict[str, float]]) -> Dict[str, float]:
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


@v.route("/api/to_form", methods=["POST"])
def to_form():
    """
    Store answers in the session and compute result scores.

    Args:
        None

    Returns:
        Tuple[dict, int]: JSON status response and HTTP status code.

    Raises:
        400: If request payload validation fails.
        500: If server computation fails.
    """
    try:
        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict):
            return {"status": "Invalid request. Please refresh and try again."}, 400

        try:
            body = ToFormBody(**payload)
        except ValidationError:
            logger.warning("[/api/to_form] ValidationError")
            return {"status": "Invalid request. Please refresh and try again."}, 400

        try:
            scoring = Questions.get_scores(test=False)
        except Exception:
            logger.exception("[/api/to_form] Failed to load question scoring data")
            return {"status": "Server error. Please refresh and try again."}, 500

        answers = body.answers

        if set(answers.keys()) != set(scoring.keys()):
            logger.warning("[/api/to_form] Answer keys mismatch")
            return {"status": "Invalid request. Please refresh and try again."}, 400

        results = calculate_results(answers, scoring)

        session["answers"] = answers
        session["results"] = results
        session["template"] = "form"

        return {"status": "success"}, 200

    except Exception:
        logger.exception("[/api/to_form] Unhandled error")
        return {"status": "Server error. Please refresh and try again."}, 500


@v.route("/api/to_test", methods=["GET"])
def to_test():
    """
    Set session state to render the test page.

    Args:
        None

    Returns:
        Tuple[dict, int]: JSON status response and HTTP status code.

    Raises:
        500: If server error occurs.
    """
    try:
        session["template"] = "test"
        return {"status": "success"}, 200

    except Exception:
        logger.exception("[/api/to_test] Unhandled error")
        return {"status": "Server error. Please refresh and try again."}, 500


@v.route("/api/to_instructions", methods=["GET"])
def to_instructions():
    """
    Set session state to render the instructions page.

    Args:
        None

    Returns:
        Tuple[dict, int]: JSON status response and HTTP status code.

    Raises:
        500: If server error occurs.
    """
    try:
        session["template"] = "instructions"
        return {"status": "success"}, 200

    except Exception:
        logger.exception("[/api/to_instructions] Unhandled error")
        return {"status": "Server error. Please refresh and try again."}, 500


@v.route("/api/to_results", methods=["POST"])
def to_results():
    """
    Validate captcha + demographics and store a completed test result.

    Args:
        None

    Returns:
        Tuple[dict, int]: JSON status payload (including results_id) and HTTP status code.

    Raises:
        400: If request is invalid or session is expired.
        401: If captcha or payload validation fails.
        503: If captcha verification is unavailable.
        500: If server/database write fails.
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

        # ----------------
        # Validate captcha
        # ----------------
        verify_url = current_app.config.get("HCAPTCHA_VERIFY_URL")
        secret = current_app.config.get("HCAPTCHA_SECRET_KEY")

        if not verify_url or not secret:
            logger.error("[/api/to_results] hCaptcha config missing (url/secret)")
            return {"status": "Captcha verification unavailable. Please try again."}, 503

        data = {
            "secret": secret,
            "response": body.captcha,
        }

        # remoteip is optional; include only if present
        if request.remote_addr:
            data["remoteip"] = request.remote_addr

        verify_response = None

        # 1 retry to squash transient network hiccups
        for attempt in (1, 2):
            try:
                resp = requests.post(
                    url=verify_url,
                    data=data,
                    timeout=8,
                )

                if resp.status_code != 200:
                    logger.warning(
                        "[/api/to_results] hCaptcha verify non-200 (attempt %s): status=%s ct=%r body=%r",
                        attempt,
                        resp.status_code,
                        resp.headers.get("Content-Type"),
                        (resp.text or "")[:200],
                    )
                    raise requests.HTTPError(f"Non-200 from hCaptcha: {resp.status_code}")

                try:
                    verify_response = resp.json()
                except ValueError as e:
                    logger.warning(
                        "[/api/to_results] hCaptcha verify invalid JSON (attempt %s): ct=%r body=%r err=%r",
                        attempt,
                        resp.headers.get("Content-Type"),
                        (resp.text or "")[:200],
                        e,
                    )
                    raise

                break  # success path

            except (requests.RequestException, ValueError) as e:
                if attempt == 1:
                    continue  # retry once
                logger.warning(
                    "[/api/to_results] Captcha verification unavailable after retry: %r",
                    e,
                    exc_info=True,
                )
                return {"status": "Captcha verification unavailable. Please try again."}, 503

        if not isinstance(verify_response, dict):
            logger.warning("[/api/to_results] hCaptcha verify response missing/invalid: %r", verify_response)
            return {"status": "Captcha verification unavailable. Please try again."}, 503

        if not verify_response.get("success"):
            logger.info(
                "[/api/to_results] Captcha verification failed: error_codes=%r hostname=%r",
                verify_response.get("error-codes"),
                verify_response.get("hostname"),
            )
            return {"status": "Captcha verification failed. Please try again."}, 401

        # ---------------------------
        # Validate session answers/results
        # ---------------------------
        session_payload, err = _validate_session_answers_and_scores()
        if err:
            logger.warning("[/api/to_results] %s", err)
            return {"status": err}, 400

        # ---------------------------
        # Validate demographics + how_found
        # ---------------------------
        demographics, dem_err = _validate_demographics_against_file(body.demographics or {})
        if dem_err:
            logger.warning("[/api/to_results] Demographics validation failed: %s", dem_err)
            return {"status": f"Result Validation Failed: {dem_err}. Refresh and try again."}, 401

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

        # Parse optional group_id from session
        group_uuid = None
        raw_gid = session.get("group_id")
        if raw_gid:
            try:
                group_uuid = UUID(str(raw_gid))
            except Exception:
                group_uuid = None

        # Add user's result to database
        try:
            if current_app.config.get("DEV"):
                session["results_id"] = 1006
            else:
                result_row = {
                    "group_id": group_uuid,
                    "demographics": demographics,
                    "scores": session_payload["scores"],
                    "answers": session_payload["answers"],
                    "how_found": how_found,
                }
                session["results_id"] = Results.add_result(result_row, return_id=True) - 1
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
    Query the database for filtered datasets (data explorer).

    Args:
        None

    Returns:
        Tuple[str, int]: JSON string response and HTTP status code.

    Raises:
        400: If request payload is invalid.
        401: If filter validation fails.
        500: If server/database query fails.
    """
    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return json.dumps({"status": "Invalid request. Please refresh and try again."}), 400

        try:
            body = DataApiBody(**payload)
        except ValidationError as e:
            logger.warning("[/api/data] ValidationError")

            bad_request = False
            try:
                bad_request = any(tuple(err.get("loc", ())) == ("data",) for err in e.errors())
            except Exception:
                bad_request = False

            if bad_request:
                return json.dumps({"status": "Invalid request. Please refresh and try again."}), 400

            return json.dumps({"status": "Filterset validation failed: Invalid filters"}), 401

        filter_data = body.data.model_dump(by_alias=True)
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

    except Exception:
        logger.exception("[/api/data] Unhandled error")
        return json.dumps({"status": "Server error. Please refresh and try again."}), 500


@v.route("/api/get_filterset_count", methods=["POST"])
def get_filterset_count():
    """
    Return dataset counts for a single filterset (custom filters UI).

    Args:
        None

    Returns:
        Tuple[str, int]: JSON string response and HTTP status code.

    Raises:
        400: If request payload is invalid.
        401: If filter validation fails.
        500: If server/database query fails.
    """
    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return json.dumps({"status": "Invalid request. Please refresh and try again."}), 400

        try:
            body = FilterCountBody(**payload)
        except ValidationError as e:
            logger.warning("[/api/get_filterset_count] ValidationError")

            bad_request = False
            try:
                bad_request = any(tuple(err.get("loc", ())) == ("data",) for err in e.errors())
            except Exception:
                bad_request = False

            if bad_request:
                return json.dumps({"status": "Invalid request. Please refresh and try again."}), 400

            return json.dumps({"status": "Filterset validation failed: Invalid filters"}), 401

        filter_data = body.data.model_dump(by_alias=True)
        counts = Results.get_filtered_dataset_count(filter_data)
        return json.dumps({"status": "success", "counts": counts}), 200

    except Exception:
        logger.exception("[/api/get_filterset_count] Unhandled error")
        return json.dumps({"status": "Server error. Please refresh and try again."}), 500
