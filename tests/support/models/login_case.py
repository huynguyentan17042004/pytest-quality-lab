from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LoginCase:
    case_id: str
    username: str
    password: str
    expected_message: str
    technique: str
    requirement_id: str
