from app.services.result_services import average_wishes_per_goal


def test_average_wishes_per_goal_averages_recorded_iterations():
    result = average_wishes_per_goal([
        {"First goal": 12, "Second goal": 8},
        {"First goal": 18},
        {"Second goal": 4},
    ])

    assert result == {"First goal": 15, "Second goal": 6}


def test_average_wishes_per_goal_returns_empty_result_without_goals():
    assert average_wishes_per_goal([]) == {}
