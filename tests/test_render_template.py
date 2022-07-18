import pytest

from component_hub.render_template import Renderer


class FakeOwner:
    def __init__(self, name):
        self.name = name


class FakeRepo:
    def __init__(self, name, owner):
        self.name = name
        self.owner = FakeOwner(owner)
        self.github_full_name = owner + "_" + name


def _deduplicate_cases():
    out = []

    empty = Renderer({}, [])
    empty_expected = Renderer({}, [])
    out.append((empty, empty_expected))

    comp1 = FakeRepo("comp1", "syn")
    comp2 = FakeRepo("comp2", "vshn")
    pkg1 = FakeRepo("pkg1", "vshn")
    nocollision = Renderer({}, [])
    nocollision._component_repositories = [
        comp1,
        comp2,
    ]
    nocollision._package_repositories = [
        pkg1,
    ]
    nocollision_expected = Renderer({}, [])
    nocollision_expected._component_repositories = [
        comp1,
        comp2,
    ]
    nocollision_expected._package_repositories = [
        pkg1,
    ]
    out.append((nocollision, nocollision_expected))

    comp1_col = FakeRepo("comp1", "other")
    comp1_vshn = FakeRepo("comp1", "vshn")
    pkg1_comp = FakeRepo("pkg1", "other")
    collision = Renderer({}, ["syn", "vshn"])
    collision._component_repositories = [
        comp1_col,
        comp1,
        comp1_vshn,
        comp2,
        pkg1_comp,
    ]
    collision._package_repositories = [
        pkg1,
    ]
    collision_expected = Renderer({}, ["syn", "vshn"])
    collision_expected._component_repositories = [
        comp1,
        comp2,
    ]
    collision_expected._package_repositories = [
        pkg1,
    ]
    out.append((collision, collision_expected))

    return out


@pytest.mark.parametrize("input,expected", _deduplicate_cases())
def test_deduplicate_repositories(input, expected):
    input._deduplicate_repositories()

    assert input._component_repositories == expected._component_repositories
    assert input._package_repositories == expected._package_repositories
