def average_wishes_per_goal(
    goal_wishes_per_iteration: list[dict[str, int]],
) -> dict[str, float]:
    total_wishes_per_goal = {}
    iterations_per_goal = {}

    for simulation in goal_wishes_per_iteration:
        for goal, wishes_spent in simulation.items():
            total_wishes_per_goal[goal] = (
                total_wishes_per_goal.get(goal, 0)
                + wishes_spent
            )
            iterations_per_goal[goal] = iterations_per_goal.get(goal, 0) + 1

    return {
        goal: total / iterations_per_goal[goal]
        for goal, total in total_wishes_per_goal.items()
    }
