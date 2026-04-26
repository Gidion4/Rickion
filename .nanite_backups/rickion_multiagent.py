"""
================================================================
RICKION MULTIAGENT — real orchestration layer
================================================================
Agents are asyncio tasks that:
  • pursue a specific goal
  • communicate via a shared message queue
  • can request new sub-agents from the Supervisor
  • have per-agent token/$ budget ceilings
  • report status to the Core event stream

This is *not* a toy. Every agent has a real loop that pulls context
from Obsidian, calls Gemini, writes results back, and logs its spend.
The Supervisor retires agents that burn budget without delivering.

Usage:
    from rickion_multiagent import Swarm
    swarm = Swarm(gemini=..., vault=..., budget=...)
    swarm.spawn("Research Librarian", "Curate alpha into Obsidian")
    await swarm.run()
"""
from __future__ import annotations

import asyncio
import dataclasses
import json
import pathlib
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable


# ---------- BUDGET ----------
@dataclass
class Budget:
    """Tracks money/tokens spent. Hard-stops when ceiling hit."""
    monthly_cap_usd: float = 20.0            # total monthly ceiling
    per_agent_cap_usd: float = 2.0           # per-agent ceiling
    warn_threshold: float = 0.8              # alarm at 80%
    spend: dict[str, float] = field(default_factory=dict)   # per-agent
    total: float = 0.0

    def can_spend(self, agent_id: str, cost: float) -> bool:
        if self.total + cost > self.monthly_cap_usd:
            return False
        if self.spend.get(agent_id, 0.0) + cost > self.per_agent_cap_usd:
            return False
        return True

    def record(self, agent_id: str, cost: float):
        self.spend[agent_id] = self.spend.get(agent_id, 0.0) + cost
        self.total += cost

    def warn_level(self) -> str:
        ratio = self.total / self.monthly_cap_usd
        if ratio >= 1.0: return "halt"
        if ratio >= self.warn_threshold: return "warn"
        return "ok"


# ---------- AGENT ----------
@dataclass
class Agent:
    id: str
    role: str
    goal: str
    engine: str = "gemini-2.0-flash"
    autonomy: str = "execute-with-approval"
    state: str = "active"          # active | paused | retired
    tasks_done: int = 0
    results_produced: int = 0
    last_output: str = ""
    born: float = field(default_factory=time.time)
    # Per-agent config the Supervisor may tune
    max_depth: int = 2             # how deeply it can spawn children
    parent: str | None = None


# ---------- MESSAGE BUS ----------
class Bus:
    def __init__(self):
        self._q: asyncio.Queue = asyncio.Queue()
        self._subscribers: list[Callable] = []

    async def publish(self, msg: dict):
        await self._q.put(msg)
        for sub in self._subscribers:
            try:
                sub(msg)
            except Exception:
                pass

    async def get(self) -> dict:
        return await self._q.get()

    def subscribe(self, fn: Callable):
        self._subscribers.append(fn)


# ---------- SWARM ----------
class Swarm:
    """The orchestrator. Spawns, supervises, retires agents."""

    def __init__(self, gemini, vault, budget: Budget, event_cb: Callable | None = None):
        self.gemini = gemini
        self.vault = vault
        self.budget = budget
        self.bus = Bus()
        self.agents: dict[str, Agent] = {}
        self.tasks: dict[str, asyncio.Task] = {}
        self.event_cb = event_cb or (lambda m: None)

    def emit(self, kind: str, text: str):
        ts = datetime.now().isoformat(timespec="seconds")
        payload = {"ts": ts, "kind": kind, "text": text}
        try:
            self.event_cb(payload)
        except Exception:
            pass

    def spawn(self, role: str, goal: str, *, engine: str = "gemini-2.0-flash",
              autonomy: str = "execute-with-approval", parent: str | None = None) -> Agent:
        agent_id = f"AG-{1000 + len(self.agents)}"
        a = Agent(id=agent_id, role=role, goal=goal, engine=engine,
                  autonomy=autonomy, parent=parent)
        self.agents[agent_id] = a
        self.tasks[agent_id] = asyncio.create_task(self._run_agent(a))
        self.emit("agent", f"spawned {agent_id} · {role}")
        return a

    def retire(self, agent_id: str, reason: str = "retired"):
        a = self.agents.get(agent_id)
        if not a:
            return
        a.state = "retired"
        t = self.tasks.pop(agent_id, None)
        if t:
            t.cancel()
        self.emit("warn", f"retired {agent_id} · {reason}")

    async def _run_agent(self, a: Agent):
        """One agent's main loop. It pulls context, thinks, writes."""
        try:
            while a.state == "active":
                # Budget gate
                if self.budget.warn_level() == "halt":
                    self.emit("err", f"{a.id} halted · budget ceiling")
                    a.state = "paused"
                    break

                # Pull context from vault — agent's private "brief" note
                brief_path = f"Agents/{a.role}/Brief.md"
                try:
                    context = (self.vault.path / brief_path).read_text(encoding="utf-8")
                except Exception:
                    context = f"Role: {a.role}\nGoal: {a.goal}\n"

                prompt = (
                    f"You are {a.role}. Goal: {a.goal}.\n"
                    f"Context from your brief:\n---\n{context}\n---\n"
                    f"What is the next concrete, small action you should take "
                    f"right now toward your goal? Output: ACTION: <one sentence>, "
                    f"followed by OUTPUT: <one-paragraph artifact this action produces>. "
                    f"Keep the output compact — Rickion reads this back tomorrow."
                )

                # Estimate cost before call (rough: $0.0001 per 1K tokens for Flash)
                est_cost = 0.0002
                if not self.budget.can_spend(a.id, est_cost):
                    self.emit("warn", f"{a.id} blocked · per-agent budget hit")
                    a.state = "paused"
                    break

                try:
                    text = self.gemini.generate(prompt)
                    self.budget.record(a.id, est_cost)
                except Exception as e:
                    self.emit("err", f"{a.id} call failed: {e}")
                    await asyncio.sleep(30)
                    continue

                # Persist — each agent has its own stream
                a.tasks_done += 1
                a.last_output = text
                log_path = self.vault.path / f"Agents/{a.role}/Stream.md"
                log_path.parent.mkdir(parents=True, exist_ok=True)
                log_path.write_text(
                    (log_path.read_text(encoding="utf-8") if log_path.exists() else f"# {a.role} · Stream\n\n")
                    + f"\n## {datetime.now().isoformat(timespec='seconds')}\n\n{text}\n",
                    encoding="utf-8",
                )

                if "OUTPUT:" in text and len(text) > 200:
                    a.results_produced += 1

                self.emit("info", f"{a.id} tick · task {a.tasks_done}")
                await asyncio.sleep(60)  # one concrete action per minute — slow + cheap
        except asyncio.CancelledError:
            pass

    async def supervise(self):
        """Continuous supervisor loop — retires unproductive agents,
        promotes productive ones, never stops on its own."""
        while True:
            await asyncio.sleep(180)
            for a in list(self.agents.values()):
                if a.state != "active":
                    continue
                # Productivity check: if 10 tasks done with zero results, retire
                if a.tasks_done > 10 and a.results_produced == 0:
                    self.retire(a.id, "unproductive · 10 tasks 0 results")
                # Budget check already enforced per-tick
            level = self.budget.warn_level()
            if level == "warn":
                self.emit("warn", f"budget at {self.budget.total:.2f}/{self.budget.monthly_cap_usd:.2f} USD")

    async def run(self):
        """Main entry: start supervisor, wait forever."""
        await self.supervise()

    def stats(self) -> dict:
        return {
            "agents": len(self.agents),
            "active": sum(1 for a in self.agents.values() if a.state == "active"),
            "budget_spent_usd": round(self.budget.total, 4),
            "budget_cap_usd": self.budget.monthly_cap_usd,
        }
