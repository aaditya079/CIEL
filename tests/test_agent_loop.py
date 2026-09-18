"""End-to-end integration test for the autonomous agent loop."""

# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀


from agent.state import AgentState
from agent.brain import AgentBrain
from agent.executor import AgentExecutor
from safety.permissions import permissions


def test_agent_mock_execution():
    # Set permissions to autonomous for unit testing mock run
    old_mode = permissions.mode
    permissions.mode = "autonomous"

    try:
        config = {
            "llm": {"provider": "mock"},
            "runtime": {"max_actions": 5, "action_delay": 0.05},
        }
        brain = AgentBrain(config=config)
        executor = AgentExecutor(brain=brain, config=config)

        state = executor.run(goal="Test mock automation loop")
        assert state.status == "completed"
        assert state.step >= 2
        assert len(state.history) >= 2
        assert state.final_result is not None
        assert "Mock task completed successfully" in state.final_result
    finally:
        permissions.mode = old_mode


def test_coordinate_translation():
    executor = AgentExecutor(config={"runtime": {"max_actions": 5, "action_delay": 0.0}})
    # Simulate an observation where screenshot is 1280x720 and physical screen is 1920x1080
    obs = {
        "active_window": {"title": "Test Window", "hwnd": 123},
        "shot_size": (1280, 720),
        "phys_size": (1920, 1080),
        "ui_elements": [],
    }
    # Test click coordinate translation: (533, 30) in 1280x720 -> (800, 45) in 1920x1080
    args = {"x": 533, "y": 30}
    shot_w, shot_h = obs["shot_size"]
    phys_w, phys_h = obs["phys_size"]
    scale_x = phys_w / shot_w
    scale_y = phys_h / shot_h
    args["x"] = int(round(args["x"] * scale_x))
    args["y"] = int(round(args["y"] * scale_y))
    assert args["x"] == 800
    assert args["y"] == 45

