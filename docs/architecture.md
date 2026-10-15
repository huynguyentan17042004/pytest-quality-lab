# Architecture

Dependency direction is `tests -> tests/support -> qa_framework -> external libraries`. The reusable package never imports application-specific page objects or clients. `tests/framework` verifies framework behavior offline or through controlled localhost/browser fixtures; live demos are separate and opt-in.
