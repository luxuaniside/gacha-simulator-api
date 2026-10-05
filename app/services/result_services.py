def average_wishes_per_goal(goal_wishes_per_iteration, iterations):
    total_wishes_per_goal = {}

    for simulation in goal_wishes_per_iteration:
        previous_wishes = 0

        for goal, cumulative_wishes in simulation.items():
            wishes_for_this_goal = cumulative_wishes - previous_wishes

            total_wishes_per_goal[goal] = (
                total_wishes_per_goal.get(goal, 0)
                + wishes_for_this_goal
            )

            previous_wishes = cumulative_wishes

    return {
        goal: total / iterations
        for goal, total in total_wishes_per_goal.items()
    }

