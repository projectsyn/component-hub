import pytest
import os

from dotenv import load_dotenv
from github import Github

from component_hub import github_wrapper


def _setup():
    load_dotenv()
    gh = Github(os.environ["GITHUB_TOKEN"])
    owners = {
        "organizations": {},
        "users": {},
    }
    for org in ["vshn", "projectsyn"]:
        owners["organizations"][org] = github_wrapper.GithubOwner(gh.get_organization(org))
    for user in ["simu", "tobru"]:
        owners["users"][user] = github_wrapper.GithubOwner(gh.get_user(user))
    return owners


def _github_owner_lt_cases():
    owners = _setup()

    cases = []

    # org < user
    cases.append((owners["organizations"]["vshn"], owners["users"]["simu"], True))
    # orgs alphabetical
    cases.append((owners["organizations"]["vshn"], owners["organizations"]["projectsyn"], False))
    # users alphabetical
    cases.append((owners["users"]["tobru"], owners["users"]["simu"], False))
    # user > org
    cases.append((owners["users"]["tobru"], owners["organizations"]["vshn"], False))

    return cases


def _github_owner_instance_cases():
    owners = _setup()
    cases = []
    for k, v in owners.items():
        cases.extend([(x, k == "organizations") for x in v.values()])
    return cases


@pytest.mark.parametrize("owner,expected", _github_owner_instance_cases())
def test_github_owner_isinstance(owner: github_wrapper.GithubOwner, expected: bool):
    assert owner.is_organization == expected


@pytest.mark.parametrize("a,b,expected", _github_owner_lt_cases())
def test_github_owner_lt(
    a: github_wrapper.GithubOwner, b: github_wrapper.GithubOwner, expected: bool
):
    assert (a < b) == expected
