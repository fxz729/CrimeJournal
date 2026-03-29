"""
Slug Service Tests

测试语义化URL生成和解析
"""
import pytest
from app.services.slug import (
    _normalize_case_name,
    _infer_case_type,
    _get_country,
    generate_case_slug,
    parse_slug,
    build_slug_url,
)


class TestNormalizeCaseName:
    """测试案例名称标准化"""

    def test_basic(self):
        assert _normalize_case_name("People v. Smith") == "people-v-smith"

    def test_with_numbers(self):
        assert _normalize_case_name("Brown v. Board of Education") == "brown-v-board-of-education"

    def test_accented_characters(self):
        assert _normalize_case_name("José García v. State") == "jose-garcia-v-state"

    def test_empty_string(self):
        assert _normalize_case_name("") == "untitled-case"

    def test_special_chars(self):
        assert _normalize_case_name("Doe #123 v. State (2020)") == "doe-123-v-state-2020"

    def test_long_name_truncated(self):
        long_name = "A" * 200
        result = _normalize_case_name(long_name)
        assert len(result) <= 80

    def test_multiple_spaces(self):
        assert _normalize_case_name("State    v.    Jones") == "state-v-jones"


class TestInferCaseType:
    """测试从法院ID推断案件类型"""

    def test_appellate_court(self):
        assert _infer_case_type("calapp", None) == "civil"
        assert _infer_case_type("ca9", None) == "civil"

    def test_district_court(self):
        assert _infer_case_type("dcd", None) == "criminal"
        assert _infer_case_type("cand", None) == "criminal"

    def test_supreme_court(self):
        assert _infer_case_type("supreme", None) == "general"

    def test_family_court(self):
        assert _infer_case_type("calfam", None) == "family"

    def test_bankruptcy(self):
        assert _infer_case_type("bankr", None) == "bankruptcy"

    def test_family(self):
        assert _infer_case_type("calfam", None) == "family"

    def test_citation_indicates_type(self):
        # F.2d = Federal Circuit
        assert _infer_case_type("ca9", "123 F.2d 456") == "civil"
        # F. Crim. = Federal Criminal
        assert _infer_case_type("dcd", "123 F. Supp. 2d 456") == "criminal"

    def test_default(self):
        assert _infer_case_type(None, None) == "general"
        assert _infer_case_type("unknown", None) == "general"


class TestGetCountry:
    """测试从法院ID推断国家"""

    def test_us_federal(self):
        assert _get_country("ca9") == "us"
        assert _get_country("dcd") == "us"
        assert _get_country("nyed") == "us"

    def test_us_state(self):
        assert _get_country("calapp") == "us"
        assert _get_country("pennapp") == "us"

    def test_unknown(self):
        assert _get_country(None) == "us"
        assert _get_country("unknown") == "us"


class TestGenerateCaseSlug:
    """测试完整slug生成"""

    def test_basic(self):
        url = build_slug_url(
            case_id=123,
            case_name="People v. Smith",
            court_id="calapp",
            citation="89 Cal.App.4th 123",
        )
        assert url == "/cases/us/civil/people-v-smith-123/"

    def test_federal_circuit(self):
        url = build_slug_url(
            case_id=456,
            case_name="United States v. Jones",
            court_id="ca9",
            citation="123 F.3d 789",
        )
        assert "/cases/us/" in url
        assert "united-states-v-jones-456" in url

    def test_district_criminal(self):
        url = build_slug_url(
            case_id=789,
            case_name="State v. Criminal",
            court_id="dcd",
        )
        assert "/cases/us/criminal/" in url
        assert "state-v-criminal-789" in url


class TestParseSlug:
    """测试slug解析"""

    def test_basic(self):
        slug_name, case_id = parse_slug("us/criminal/people-v-smith-123456789")
        assert slug_name == "people-v-smith"
        assert case_id == 123456789

    def test_simple_slug(self):
        slug_name, case_id = parse_slug("robbery-case-42")
        assert slug_name == "robbery-case"
        assert case_id == 42

    def test_no_case_id(self):
        slug_name, case_id = parse_slug("no-id-here")
        assert slug_name == "no-id-here"
        assert case_id is None

    def test_empty(self):
        slug_name, case_id = parse_slug("")
        assert slug_name is None
        assert case_id is None

    def test_only_slashes(self):
        slug_name, case_id = parse_slug("///")
        assert slug_name is None
        assert case_id is None

    def test_with_trailing_slash(self):
        # parse_slug extracts case_id from the end of the LAST path segment
        # For "case-999", the case_id is 999, leaving slug_name="case"
        slug_name, case_id = parse_slug("us/civil/case-999")
        assert slug_name == "case"
        assert case_id == 999

    def test_simple_slug(self):
        slug_name, case_id = parse_slug("robbery-case-42")
        assert slug_name == "robbery-case"
        assert case_id == 42

    def test_full_url_roundtrip(self):
        # Simulate what happens in the API: build URL from parts, parse it back
        original_case_name = "People v. Smith"
        original_case_id = 123456789
        url = build_slug_url(
            case_id=original_case_id,
            case_name=original_case_name,
            court_id="calapp",
        )
        # URL: /cases/us/civil/people-v-smith-123456789/
        slug_path = url.lstrip("/cases/").rstrip("/")  # "us/civil/people-v-smith-123456789"
        parsed_name, parsed_id = parse_slug(slug_path)
        assert parsed_id == original_case_id
        # parsed_name is just the last segment without case_id
        assert parsed_name == "people-v-smith"  # Slash before number, so no match

    def test_numeric_only(self):
        slug_name, case_id = parse_slug("123")
        assert slug_name == "123"
        assert case_id is None


class TestBuildSlugUrl:
    """测试完整URL构建"""

    def test_basic(self):
        url = build_slug_url(
            case_id=123,
            case_name="People v. Smith",
            court_id="calapp",
        )
        assert url == "/cases/us/civil/people-v-smith-123/"

    def test_with_citation(self):
        url = build_slug_url(
            case_id=456,
            case_name="United States v. Jones",
            court_id="ca9",
            citation="789 F.3d 123",
        )
        assert "/cases/us/" in url
        assert "united-states-v-jones-456" in url

    def test_district_court(self):
        url = build_slug_url(
            case_id=789,
            case_name="State v. Robber",
            court_id="dcd",
        )
        assert "/cases/us/criminal/" in url
        assert "state-v-robber-789" in url
