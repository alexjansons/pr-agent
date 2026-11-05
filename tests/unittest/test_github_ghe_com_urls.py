"""GitHub Enterprise Cloud with data residency (GHE.com) serves its REST API on ``api.<subdomain>.ghe.com``.

Pull request and issue URLs on that host must parse like ``api.github.com`` ones, and links built from
``github.base_url`` must point at ``<subdomain>.ghe.com`` rather than ``github.com``.
"""
from urllib.parse import urlparse

import pytest

from pr_agent.git_providers.github_provider import GithubProvider


@pytest.mark.parametrize("base_url, expected", [
    ("https://api.github.com", "https://github.com"),
    ("https://github.example.com/api/v3", "https://github.example.com"),
    ("https://api.octo.ghe.com", "https://octo.ghe.com"),
])
def test_html_base_url(base_url, expected):
    assert GithubProvider._html_base_url(base_url) == expected


@pytest.mark.parametrize("url, resource", [
    ("https://api.octo.ghe.com/repos/owner/repo/pulls/7", "pulls"),
    ("https://octo.ghe.com/owner/repo/pull/7", "pull"),
    ("https://api.octo.ghe.com/repos/owner/repo/issues/3", "issues"),
])
def test_url_resource_on_ghe_com(url, resource):
    assert GithubProvider._get_url_resource(url) == resource


@pytest.mark.parametrize("url", [
    "https://api.octo.ghe.com/repos/owner/repo/pulls/7",
    "https://octo.ghe.com/owner/repo/pull/7",
])
def test_parse_pr_url_on_ghe_com(url):
    provider = GithubProvider.__new__(GithubProvider)
    assert provider._parse_pr_url(url) == ("owner/repo", 7)


def test_parse_issue_url_on_ghe_com():
    provider = GithubProvider.__new__(GithubProvider)
    assert provider._parse_issue_url("https://api.octo.ghe.com/repos/owner/repo/issues/3") == ("owner/repo", 3)


def test_api_prefixed_server_host_is_not_treated_as_api_url():
    # Only *.ghe.com gets the api.<host> treatment; a self-hosted server named api.<company> keeps web URLs.
    assert not GithubProvider._is_api_url(urlparse("https://api.example.com/owner/repo/pull/7"))
