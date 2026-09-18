"""Desktop Agent CLI: Autonomous Windows 11 Assistant."""

import sys
import os
import argparse
import logging
import time

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from safety.kill_switch import kill_switch
from safety.permissions import permissions, SafetyLevel
from agent.state import AgentState
from agent.brain import AgentBrain
from agent.executor import AgentExecutor
from agent.fast_router import fast_router
from computer.voice import voice
from config.manager import load_config

console = Console(force_terminal=True, legacy_windows=False)


def configure_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


_current_status = None


def rich_confirmation_handler(tool_name: str, arguments: dict, tier: SafetyLevel) -> bool:
    """Rich interactive confirmation prompt in terminal."""
    global _current_status
    was_running = False
    if _current_status:
        try:
            _current_status.stop()
            was_running = True
        except Exception:
            pass

    try:
        console.print()
        if tier == SafetyLevel.LEVEL_3_ALWAYS_CONFIRM:
            panel = Panel(
                f"[bold red]CRITICAL ACTION REQUESTED[/bold red]\n"
                f"[bold]Tool:[/bold] {tool_name}\n"
                f"[bold]Arguments:[/bold] {arguments}\n\n"
                f"[yellow]This is a potentially destructive action.[/yellow]",
                title="[!] SECURITY PERMISSION REQUIRED",
                border_style="red",
            )
            console.print(panel)
            confirm = console.input("[bold red]Type 'CONFIRM' to allow this action, or anything else to deny: [/bold red]").strip()
            return confirm == "CONFIRM"
        else:
            panel = Panel(
                f"[bold]Tool:[/bold] {tool_name}\n"
                f"[bold]Arguments:[/bold] {arguments}",
                title="[?] Agent Requests Permission",
                border_style="yellow",
            )
            console.print(panel)
            confirm = console.input("[bold yellow]Allow execution? [y/N]: [/bold yellow]").strip().lower()
            return confirm in ("y", "yes")
    finally:
        if was_running and _current_status:
            try:
                _current_status.start()
            except Exception:
                pass


def print_banner():
    banner_text = """[bold red]
   ____ ___ _____ _     
  / ___|_ _| ____| |    
 | |    | ||  _| | |    
 | |___ | || |___| |___ 
  \\____|___|_____|_____|
    CIEL // WISDOM KING RAPHAEL (智慧之王)
[/bold red]
[bold yellow]* Ultimate Skill: Raphael (Lord of Wisdom) // Manas: Ciel[/bold yellow]
[dim]* Sub-Skills: Thought Acceleration | Analytical Appraisal | Parallel Operation | Chant Annulment[/dim]
[dim]* Control Hierarchy: Chant Annulment (Direct API) -> UI Automation -> Vision -> Coordinates[/dim]
[dim]* Emergency Kill Switch: [bold red]Ctrl + Alt + X[/bold red] (or slam mouse to upper-left corner)[/dim]
[dim]* Voice Synthesizer: [bold green]Active[/bold green] (Raphael Sound Pack & SAPI Voice)[/dim]
"""
    console.print(banner_text)


def run_single_goal(executor: AgentExecutor, goal: str, max_actions: int = 50):
    """Execute a single goal with live terminal updates."""
    console.print(Panel(f"[bold white]{goal}[/bold white]", title="Current Task", border_style="red"))

    # Check fast-path router first (<50ms execution without LLM)
    fast_res = fast_router.route(goal)
    if fast_res and fast_res.get("handled"):
        msg = fast_res.get("message", "Action completed.")
        spoken = fast_res.get("spoken", msg)
        tool = fast_res.get("tool")
        args = fast_res.get("arguments")

        console.print(f"\n[bold green][FAST-PATH][/bold green] Tool: [bold]{tool}[/bold]({args})")
        console.print(f"[bold green][OK] TASK COMPLETED:[/bold green] {msg}\n")
        voice.play_sound("notice", block=False)
        if spoken:
            voice.speak_raphael(spoken, prefix="Report", with_chime=False)
        return

    # Multimodal vision agent execution
    voice.speak_raphael("Directive acknowledged. Commencing execution.", prefix="Notice", with_chime=True)

    kill_switch.reset()
    state = AgentState(goal=goal, max_actions=max_actions)
    state.start()

    global _current_status
    with console.status("[bold red]Raphael is observing desktop (Analytical Appraisal)...", spinner="dots") as status:
        _current_status = status
        try:
            while not state.is_finished() and state.step < state.max_actions:
                kill_switch.check()
                status.update(f"[bold red]Step {state.step + 1}: Observing & Deciding...")

                step_res = executor.step(state)

                if step_res.get("done"):
                    if step_res.get("success", True) and not step_res.get("error"):
                        compl_msg = step_res.get("message") or "Task completed."
                        console.print(f"\n[bold green][OK] TASK COMPLETED:[/bold green] {compl_msg}")
                        voice.speak_raphael(str(compl_msg), prefix="Report", with_chime=False)
                    else:
                        fail_msg = step_res.get("message") or step_res.get("error") or "Task failed."
                        console.print(f"\n[bold red][X] TASK FAILED:[/bold red] {fail_msg}")
                        voice.speak_raphael("Directive execution failed. Irregularity detected.", prefix="Notice", with_chime=False)
                    break

                # Print step summary table
                tool = step_res.get("tool")
                args = step_res.get("arguments")
                thought = step_res.get("thought", "")
                success = step_res.get("success", False)
                err = step_res.get("error")

                color = "green" if success else "red"
                status_symbol = "[OK]" if success else "[X]"

                console.print(f"\n[bold blue][Step {state.step}][/bold blue] [dim]{thought}[/dim]")
                console.print(f"  [{color}]{status_symbol} Tool:[/{color}] [bold]{tool}[/bold]({args})")
                if err:
                    console.print(f"  [red]Warning/Error:[/red] {err}")
        finally:
            _current_status = None

    if state.status == "failed":
        console.print(f"\n[bold red][X] Task Failed:[/bold red] {state.error_message}")
    elif state.status == "stopped":
        console.print(f"\n[bold red][!] Task Aborted by Kill Switch.[/bold red]")


def interactive_repl(executor: AgentExecutor, max_actions: int = 50):
    """Interactive loop for multiple user tasks."""
    console.print("\n[bold]Ready for commands. Type [cyan]'exit'[/cyan] or [cyan]'quit'[/cyan] to leave.[/bold]\n")
    while True:
        try:
            goal = console.input("[bold cyan]ciel>[/bold cyan] ").strip()
            if not goal:
                continue
            if goal.lower() in ("exit", "quit", "q"):
                console.print("[dim]Exiting CIEL. Goodbye![/dim]")
                break
            run_single_goal(executor, goal, max_actions)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Session terminated.[/dim]")
            break


def ensure_api_key(config: dict, provider: str = "gemini") -> dict:
    """Prompt for API key if missing, and persist it to config.json so the user is never asked again."""
    if provider in ("mock", "ollama"):
        return config

    placeholder_keys = {"", "your-api-key", "your-gemini-api-key", "your-openai-api-key", "your_key_here", "none"}
    llm = config.setdefault("llm", {})

    if provider == "gemini":
        current_key = (llm.get("gemini_api_key") or "").strip()
        if not current_key or current_key.lower() in placeholder_keys:
            panel = Panel(
                "[bold cyan]Google Gemini API Key Setup (One-Time)[/bold cyan]\n\n"
                "No valid Gemini API key found.\n"
                "[dim]* Get a free key at: [underline]https://aistudio.google.com/[/underline][/dim]\n"
                "[dim]* Keys start with 'AIzaSy...'[/dim]\n\n"
                "[yellow]This key will be saved to config/config.json so you are only asked once.[/yellow]",
                title="API Key Configuration",
                border_style="cyan",
            )
            console.print(panel)
            while True:
                entered = console.input("[bold green]Paste your Gemini API key: [/bold green]").strip()
                if not entered:
                    console.print("[red]API key cannot be empty. (Type 'mock' to run offline)[/red]")
                    continue
                if entered.lower() == "mock":
                    config["llm"]["provider"] = "mock"
                    return config
                if entered.lower() in placeholder_keys:
                    console.print("[red]Please paste your actual API key, not a placeholder.[/red]")
                    continue

                llm["gemini_api_key"] = entered
                from config.manager import set_api_key
                set_api_key(entered, "gemini")
                console.print("[bold green][OK] API key saved to config/config.json! You won't be asked again.[/bold green]\n")
                break

    elif provider == "openai":
        current_key = (llm.get("openai_api_key") or "").strip()
        if not current_key or current_key.lower() in placeholder_keys:
            panel = Panel(
                "[bold cyan]OpenAI API Key Setup (One-Time)[/bold cyan]\n\n"
                "No valid OpenAI API key found.\n"
                "[yellow]This key will be saved to config/config.json so you are only asked once.[/yellow]",
                title="API Key Configuration",
                border_style="cyan",
            )
            console.print(panel)
            while True:
                entered = console.input("[bold green]Paste your OpenAI API key: [/bold green]").strip()
                if not entered:
                    continue
                if entered.lower() in placeholder_keys:
                    continue
                llm["openai_api_key"] = entered
                from config.manager import set_api_key
                set_api_key(entered, "openai")
                console.print("[bold green][OK] API key saved to config/config.json! You won't be asked again.[/bold green]\n")
                break

    return config


def main():
    parser = argparse.ArgumentParser(description="CIEL: Autonomous Windows 11 Desktop Agent")
    parser.add_argument("goal", nargs="*", help="Task goal to execute (e.g. open spotify and play harvey)")
    parser.add_argument("--set-key", help="Save an API key permanently to config.json and exit")
    parser.add_argument("--serve", action="store_true", help="Start the local FastAPI server on port 8000")
    parser.add_argument("--port", type=int, default=8000, help="Port for local server")
    parser.add_argument("--mode", choices=["strict", "balanced", "autonomous"], default="balanced", help="Safety permission mode")
    parser.add_argument("--provider", choices=["gemini", "openai", "ollama", "mock"], help="Override LLM provider")
    parser.add_argument("--hud", action="store_true", help="Launch local HUD web dashboard in browser")
    parser.add_argument("--max-actions", type=int, default=50, help="Maximum actions before automatic abort")
    parser.add_argument("--voice", action="store_true", default=None, help="Enable voice speech feedback")
    parser.add_argument("--no-voice", action="store_true", help="Disable voice speech feedback")
    parser.add_argument("--log-level", default="WARNING", help="Logging level (DEBUG, INFO, WARNING, ERROR)")

    args = parser.parse_args()

    # If --set-key was provided, save and exit
    if args.set_key:
        prov = args.provider or "gemini"
        set_api_key(args.set_key, prov)
        console.print(f"[bold green]API key for {prov} saved successfully to config.json.[/bold green]")
        return

    configure_logging(args.log_level)
    print_banner()

    # Apply configuration
    config = load_config()
    if args.provider:
        config.setdefault("llm", {})["provider"] = args.provider
    current_provider = config.get("llm", {}).get("provider", "gemini")

    # Check if voice feedback is enabled
    if args.voice is not None:
        voice.enabled = args.voice
    else:
        voice.enabled = config.get("voice_feedback", True)

    # One-time API key prompt if missing
    config = ensure_api_key(config, current_provider)

    permissions.mode = args.mode
    permissions.set_confirmation_handler(rich_confirmation_handler)

    # Start emergency kill switch listener (Ctrl+Alt+X)
    kill_switch.start_listener()

    # Start global summon hotkey listener (Ctrl+Alt+C)
    from agent.hotkey_listener import hotkey_listener
    hotkey_listener.start(callback=lambda: (voice.play_sound("notice", block=False), voice.speak_raphael("Wisdom King Raphael is listening. How may I assist you, Master?", prefix="Notice", with_chime=False)))

    if args.serve or args.hud:
        if args.hud:
            import webbrowser
            import threading
            threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{args.port}/hud")).start()
        console.print(f"[bold red]Starting CIEL Wisdom King Raphael HUD on http://localhost:{args.port}/hud ...[/bold red]")
        try:
            import uvicorn
            uvicorn.run("server.api:app", host="0.0.0.0", port=args.port, reload=False)
        except (ImportError, ModuleNotFoundError) as err:
            console.print(f"[yellow]Uvicorn/FastAPI not fully available ({err}). Falling back to Native Standalone Server...[/yellow]")
            from server.standalone_server import run_standalone_server
            run_standalone_server(port=args.port)
        finally:
            kill_switch.stop_listener()
            hotkey_listener.stop()
            voice.stop()
        return

    brain = AgentBrain(config=config)
    executor = AgentExecutor(brain=brain, config=config)

    raw_goal = " ".join(args.goal).strip() if isinstance(args.goal, list) else str(args.goal or "").strip()
    goal = raw_goal if raw_goal else None

    try:
        if goal:
            run_single_goal(executor, goal, args.max_actions)
        else:
            interactive_repl(executor, args.max_actions)
    finally:
        kill_switch.stop_listener()
        hotkey_listener.stop()
        voice.stop()


if __name__ == "__main__":
    main()
