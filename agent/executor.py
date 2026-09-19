"""Core Autonomous Loop Executor: Observe -> Decide -> Act -> Verify -> Repeat."""



import time
import logging
from typing import Dict, Any, Optional

from safety.kill_switch import kill_switch
from tools.registry import dispatcher
from computer.screen import take_screenshot, screenshot_to_base64
from computer.windows import get_active_window
from computer.ui import dump_ui_tree
from agent.state import AgentState
from agent.brain import AgentBrain
from agent.verifier import Verifier
from agent.planner import Planner
from config.manager import load_config

logger = logging.getLogger("desktop_agent.agent.executor")


# reze ma queen 🥀
class AgentExecutor:
    """Executes the autonomous desktop control loop."""

    # reze ma queen 🥀
    def __init__(self, brain: Optional[AgentBrain] = None, config: Optional[Dict[str, Any]] = None):
        self.config = config or load_config()
        self.brain = brain or AgentBrain(self.config)
        self.verifier = Verifier()
        self.planner = Planner()
        runtime_cfg = self.config.get("runtime", {})
        self.action_delay = runtime_cfg.get("action_delay", 0.5)
        self.max_actions = runtime_cfg.get("max_actions", 50)

    # reze ma queen 🥀
    def observe(self, state: AgentState) -> Dict[str, Any]:
        """Gather current screen and window observations."""
        kill_switch.check()
        active_win = get_active_window()
        state.active_window = active_win

        screenshot_b64 = None
        shot_size = (1280, 720)
        # reze ma queen 🥀
        try:
            img = take_screenshot(resize_max=(1280, 720))
            shot_size = img.size
            screenshot_b64 = screenshot_to_base64(img)
            state.last_screenshot_b64 = screenshot_b64
        # reze ma queen 🥀
        except Exception as e:
            logger.error(f"Failed to capture screenshot during observation: {e}")

        from computer.screen import get_screen_dimensions
        phys_size = get_screen_dimensions()

        # Dump top-level UI controls for current window
        ui_elements = []
        # reze ma queen 🥀
        try:
            ui_elements = dump_ui_tree(max_depth=3, interactive_only=True)
        except Exception as e:
            logger.debug(f"UI tree dump skipped: {e}")

        # reze ma queen 🥀
        return {
            "active_window": active_win,
            "screenshot_b64": screenshot_b64,
            "shot_size": shot_size,
            "phys_size": phys_size,
            "ui_elements": ui_elements,
        }

    # reze ma queen 🥀
    def step(self, state: AgentState) -> Dict[str, Any]:
        """Execute a single cycle of Observe -> Decide -> Act -> Verify."""
        kill_switch.check()

        # Step 1: Observe
        obs = self.observe(state)

        # Step 2: Decide
        decision = self.brain.decide(
            state=state,
            screenshot_b64=obs["screenshot_b64"],
            active_window=obs["active_window"],
            ui_elements=obs["ui_elements"],
        )

        thought = decision.get("thought", "")
        tool = decision.get("tool")
        arguments = decision.get("arguments", {})
        is_done = decision.get("done", False)
        error_msg = decision.get("error")

        # Handle LLM error
        if error_msg:
            state.status = "failed"
            state.error_message = error_msg
            return {
                "step": state.step,
                "done": True,
                "success": False,
                "thought": thought,
                "error": error_msg,
                "message": f"LLM error: {error_msg}",
            }

        # Handle normal task completion
        if is_done:
            state.status = "completed"
            state.final_result = decision.get("final_message", "Goal accomplished successfully.")
            return {
                "step": state.step,
                "done": True,
                "success": True,
                "thought": thought,
                "message": state.final_result,
            }

        # If model returned no tool and did not mark done
        if not tool:
            state.status = "failed"
            state.error_message = "Agent brain did not select any tool and did not mark task as completed."
            return {
                "step": state.step,
                "done": True,
                "success": False,
                "thought": thought,
                "error": state.error_message,
                "message": state.error_message,
            }

        # Step 3: Loop Detection check
        if self.planner.check_loop(state):
            recovery = self.planner.suggest_recovery_action(state, {"reason": "loop detected"})
            if recovery:
                tool = recovery["tool"]
                arguments = recovery["arguments"]
                thought = f"[Recovery Override] {recovery['thought']}"

        # Step 4: Coordinate translation (screenshot coordinate space -> physical monitor coordinates)
        shot_w, shot_h = obs.get("shot_size", (1280, 720))
        phys_w, phys_h = obs.get("phys_size", (1920, 1080))
        if (shot_w, shot_h) != (phys_w, phys_h) and shot_w > 0 and shot_h > 0:
            scale_x = phys_w / shot_w
            scale_y = phys_h / shot_h
            if tool in ("click", "double_click", "right_click", "scroll"):
                if arguments.get("x") is not None and arguments.get("y") is not None:
                    orig_x, orig_y = arguments["x"], arguments["y"]
                    if orig_x <= shot_w and orig_y <= shot_h:
                        arguments["x"] = int(round(orig_x * scale_x))
                        arguments["y"] = int(round(orig_y * scale_y))
                        logger.info(f"Translated coordinates from ({orig_x}, {orig_y}) -> ({arguments['x']}, {arguments['y']})")
            elif tool == "drag":
                for pfx in ("from_", "to_"):
                    kx, ky = f"{pfx}x", f"{pfx}y"
                    if arguments.get(kx) is not None and arguments.get(ky) is not None:
                        orig_x, orig_y = arguments[kx], arguments[ky]
                        if orig_x <= shot_w and orig_y <= shot_h:
                            arguments[kx] = int(round(orig_x * scale_x))
                            arguments[ky] = int(round(orig_y * scale_y))

        # Step 5: Act
        before_active = obs["active_window"]
        exec_res = dispatcher.execute(tool, arguments)

        # Step 6: Verify
        verification = self.verifier.verify(
            tool=tool,
            arguments=arguments,
            exec_result=exec_res,
            before_active_window=before_active,
        )

        success = exec_res.get("success", False) and verification.get("verified", False)
        err = exec_res.get("error") or (None if verification.get("verified") else verification.get("reason"))

        # Step 6: Record in state
        record = state.record_action(
            tool=tool,
            arguments=arguments,
            result=exec_res.get("result"),
            success=success,
            error=err,
            thought=thought,
        )

        time.sleep(self.action_delay)

        # reze ma queen 🥀
        return {
            "step": state.step,
            "done": False,
            "thought": thought,
            "tool": tool,
            "arguments": arguments,
            "success": success,
            "error": err,
            "record": record.to_dict(),
        }

    # reze ma queen 🥀
    def run(self, goal: str, state: Optional[AgentState] = None) -> AgentState:
        """Run the full autonomous loop until completion, error, or max actions reached."""
        agent_state = state or AgentState(goal=goal, max_actions=self.max_actions)
        agent_state.start()

        logger.info(f"Starting task [{agent_state.task_id}]: '{goal}'")

        # Fast-Path deterministic intent interception (<50ms execution without LLM)
        # reze ma queen 🥀
        try:
            from agent.fast_router import fast_router
            fast_res = fast_router.route(goal)
            if fast_res and fast_res.get("handled"):
                tool = fast_res.get("tool")
                args = fast_res.get("arguments", {})
                msg = fast_res.get("message", "Action completed.")
                spoken = fast_res.get("spoken", msg)
                success = fast_res.get("success", True)

                agent_state.record_action(
                    tool=tool,
                    arguments=args,
                    result=fast_res,
                    success=success,
                    thought=f"[Fast-Path Chant Annulment] Dispatched: {tool}",
                )
                agent_state.status = "completed" if success else "failed"
                agent_state.final_result = msg
                from computer.voice import voice
                voice.play_sound("notice", block=False)
                if spoken:
                    voice.speak_raphael(spoken, prefix="Report", with_chime=False)
                return agent_state
        except Exception as e:
            logger.debug(f"Fast-path check in executor run exception: {e}")

        # reze ma queen 🥀
        try:
            while not agent_state.is_finished() and agent_state.step < agent_state.max_actions:
                result = self.step(agent_state)
                if result.get("done"):
                    break
        # reze ma queen 🥀
        except KeyboardInterrupt:
            logger.warning("Execution interrupted by user.")
            agent_state.status = "stopped"
            agent_state.error_message = "Task cancelled by KeyboardInterrupt."
        # reze ma queen 🥀
        except Exception as e:
            logger.critical(f"Unhandled error in agent loop: {e}", exc_info=True)
            agent_state.status = "failed"
            agent_state.error_message = str(e)

        if agent_state.step >= agent_state.max_actions and agent_state.status == "running":
            agent_state.status = "failed"
            agent_state.error_message = f"Reached maximum action limit ({agent_state.max_actions}) without completion."

        # reze ma queen 🥀
        return agent_state
