"""Unit tests for interaction filtering logic - edge cases and boundary values."""

from app.models.interaction import InteractionLog
from app.routers.interactions import filter_by_max_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


# KEPT: Tests zero max_item_id boundary with mixed positive/negative/zero item_ids - not covered by existing tests.
def test_filter_with_zero_max_item_id() -> None:
    """Test filtering when max_item_id is zero - only item_id 0 or negative should pass."""
    interactions = [_make_log(1, 1, 0), _make_log(2, 1, 1), _make_log(3, 1, -1)]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=0)
    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 3


# KEPT: Tests negative max_item_id boundary - exercises filtering logic with negative values not covered elsewhere.
def test_filter_with_negative_max_item_id() -> None:
    """Test filtering with negative max_item_id - only negative item_ids should pass."""
    interactions = [
        _make_log(1, 1, -5),
        _make_log(2, 1, -1),
        _make_log(3, 1, 0),
        _make_log(4, 1, 1),
    ]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=-2)
    assert len(result) == 1
    assert result[0].id == 1


# KEPT: Tests very large max_item_id to verify no integer overflow issues and all interactions pass.
def test_filter_with_very_large_max_item_id() -> None:
    """Test filtering with very large max_item_id - all interactions should pass."""
    interactions = [_make_log(1, 1, 1), _make_log(2, 1, 100), _make_log(3, 1, 999999)]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=10**9)
    assert len(result) == 3
    assert result == interactions


# KEPT: Tests duplicate item_ids across different learners - verifies filtering handles duplicates correctly.
def test_filter_with_duplicate_item_ids() -> None:
    """Test filtering when multiple interactions have the same item_id."""
    interactions = [
        _make_log(1, 1, 5),
        _make_log(2, 2, 5),
        _make_log(3, 3, 5),
        _make_log(4, 1, 6),
    ]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=5)
    assert len(result) == 3
    assert all(i.item_id == 5 for i in result)


# KEPT: Tests scenario where all interactions are excluded (all above max) - distinct from empty input test.
def test_filter_all_interactions_above_max() -> None:
    """Test filtering when all interactions have item_id greater than max_item_id."""
    interactions = [_make_log(1, 1, 10), _make_log(2, 1, 20), _make_log(3, 1, 30)]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=5)
    assert len(result) == 0


# KEPT: Tests all interactions pass (all below max) with clear margin - validates no false exclusions.
def test_filter_all_interactions_below_max() -> None:
    """Test filtering when all interactions have item_id less than max_item_id."""
    interactions = [_make_log(1, 1, 1), _make_log(2, 1, 2), _make_log(3, 1, 3)]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=100)
    assert len(result) == 3
    assert result == interactions


# KEPT: Tests that filtering preserves original list order - important for deterministic behavior.
def test_filter_preserves_original_order() -> None:
    """Test that filtering preserves the original order of interactions."""
    interactions = [
        _make_log(1, 1, 5),
        _make_log(2, 1, 10),
        _make_log(3, 1, 3),
        _make_log(4, 1, 8),
        _make_log(5, 1, 1),
    ]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=7)
    assert len(result) == 3
    assert result[0].id == 1
    assert result[1].id == 3
    assert result[2].id == 5


# DISCARDED: Duplicates existing test_filter_includes_interaction_at_boundary which already tests single interaction at boundary.
# def test_filter_with_single_interaction_at_boundary() -> None:
#     """Test filtering with single interaction exactly at max_item_id boundary."""
#     interactions = [_make_log(1, 1, 10)]
#     result = filter_by_max_item_id(interactions=interactions, max_item_id=10)
#     assert len(result) == 1
#     assert result[0].id == 1
#
#     result_excluded = filter_by_max_item_id(interactions=interactions, max_item_id=9)
#     assert len(result_excluded) == 0


# KEPT: Tests filtering with multiple learners and varied item_ids - validates learner_id is ignored in filtering.
def test_filter_with_mixed_learners_and_item_ids() -> None:
    """Test filtering with multiple learners and varied item_ids."""
    interactions = [
        _make_log(1, 1, 3),
        _make_log(2, 2, 7),
        _make_log(3, 1, 5),
        _make_log(4, 3, 2),
        _make_log(5, 2, 8),
    ]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=5)
    assert len(result) == 3
    assert result[0].id == 1
    assert result[1].id == 3
    assert result[2].id == 4


# KEPT: Tests consecutive item_ids at exact boundary - verifies precise <= comparison with sequential values.
def test_filter_with_consecutive_item_ids_boundary() -> None:
    """Test filtering at boundary with consecutive item_id values."""
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 1, 2),
        _make_log(3, 1, 3),
        _make_log(4, 1, 4),
        _make_log(5, 1, 5),
    ]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=3)
    assert len(result) == 3
    assert [i.item_id for i in result] == [1, 2, 3]
