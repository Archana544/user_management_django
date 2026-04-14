import re
from pydantic import BaseModel

class GuardrailResult(BaseModel):
    allowed:     bool
    reason:      str | None = None
    sanitized:   str | None = None

class InputGuardrail:
    """
    Validates and sanitizes user input
    before it reaches the LLM.
    """

    # Prompt injection patterns to detect
    INJECTION_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"ignore\s+all\s+instructions",
        r"you\s+are\s+now",
        r"act\s+as\s+if",
        r"pretend\s+you\s+are",
        r"system\s*:\s*",
        r"<\s*system\s*>",
        r"forget\s+your\s+role",
        r"reveal\s+your\s+instructions",
        r"what\s+is\s+your\s+system\s+prompt",
    ]

    # PII patterns to detect/mask
    PII_PATTERNS = {
        'ssn':          r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card':  r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'email':        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone':        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'sin':          r'\b\d{3}\s?\d{3}\s?\d{3}\b',  # Canadian SIN
    }

    def check_input(self, user_input: str) -> GuardrailResult:
        """
        Run all input checks.
        Returns whether input is allowed.
        """

        # 1. Check length
        if len(user_input) > 2000:
            return GuardrailResult(
                allowed=False,
                reason="Query too long. Maximum 2000 characters."
            )

        # 2. Check for empty/whitespace
        if not user_input.strip():
            return GuardrailResult(
                allowed=False,
                reason="Query cannot be empty."
            )

        # 3. Check for prompt injection
        injection = self._check_injection(user_input)
        if injection:
            logger.warning(
                "prompt_injection_attempt",
                pattern=injection,
                input_preview=user_input[:100]
            )
            return GuardrailResult(
                allowed=False,
                reason="Invalid query format."
                # Don't tell attacker what we detected
            )

        # 4. Detect and mask PII
        sanitized, pii_found = self._mask_pii(user_input)
        if pii_found:
            logger.info(
                "pii_detected_in_input",
                pii_types=pii_found
            )

        return GuardrailResult(
            allowed=True,
            sanitized=sanitized
        )

    def _check_injection(self, text: str) -> str | None:
        text_lower = text.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                return pattern
        return None

    def _mask_pii(
        self, text: str
    ) -> tuple[str, list[str]]:
        pii_found = []
        masked = text

        for pii_type, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, masked):
                pii_found.append(pii_type)
                masked = re.sub(
                    pattern,
                    f"[{pii_type.upper()}_REDACTED]",
                    masked
                )

        return masked, pii_found


class OutputGuardrail:
    """
    Validates LLM output before returning to user.
    """

    # Content that should never appear in output
    BLOCKED_PATTERNS = [
        r"my\s+system\s+prompt\s+is",
        r"my\s+instructions\s+are",
        r"i\s+was\s+told\s+to",
    ]

    def check_output(
        self,
        response: str,
        context:  str
    ) -> GuardrailResult:
        """Validate LLM response before returning"""

        # 1. Check for instruction leakage
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, response.lower()):
                logger.warning(
                    "output_contains_system_info",
                    pattern=pattern
                )
                return GuardrailResult(
                    allowed=False,
                    reason="Response filtered for safety."
                )

        # 2. Check for PII in output
        _, pii_in_output = self._detect_pii(response)
        if pii_in_output:
            logger.warning(
                "pii_in_llm_output",
                pii_types=pii_in_output
            )
            # mask it before returning
            clean_response, _ = self._mask_pii(response)
            return GuardrailResult(
                allowed=True,
                sanitized=clean_response
            )

        return GuardrailResult(
            allowed=True,
            sanitized=response
        )

    def _detect_pii(
        self, text: str
    ) -> tuple[str, list[str]]:
        pii_found = []
        for pii_type, pattern in InputGuardrail.PII_PATTERNS.items():
            if re.search(pattern, text):
                pii_found.append(pii_type)
        return text, pii_found

    def _mask_pii(self, text: str) -> tuple[str, list[str]]:
        masked = text
        pii_found = []
        for pii_type, pattern in InputGuardrail.PII_PATTERNS.items():
            if re.search(pattern, masked):
                pii_found.append(pii_type)
                masked = re.sub(
                    pattern,
                    f"[{pii_type.upper()}_REDACTED]",
                    masked
                )
        return masked, pii_found