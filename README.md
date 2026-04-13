# 🔮 Agent Resilience Preview

**Exploring CPS 230 operational resilience for agentic infrastructure**

> *"We're not there yet — but we will be."*

This is a 2-hour concept demonstration exploring the intersection of:
- **APRA CPS 230** operational resilience requirements
- **AWS Agent Registry** for agent discovery and governance
- **Agentic infrastructure** that will soon handle critical operations

---

## What This Is

A preview of how we might automatically assess and test AI agent resilience against prudential standards **in the near future** (12-18 months).

**Key components:**
1. **Agent Discovery** — Query AWS Agent Registry for registered agents
2. **Materiality Assessment** — Auto-classify against CPS 230 materiality criteria
3. **Failure Simulation** — Model dependency failures and RTO impact
4. **Resilience Dashboard** — Generate audit-ready CPS 230 readiness view

---

## What This Is NOT

- ❌ Production software
- ❌ Real chaos engineering (simulated only)
- ❌ APRA guidance or official interpretation
- ❌ A product you can buy

This is **exploratory code** sketching what's coming.

---

## Quick Start

```bash
# Run the demo
python demo.py

# Open the generated dashboard
open resilience_preview.html
```

---

## The Scenario

**Agent:** `fraud-detection-v2-prod`
- Handles $2.4M in daily transaction analysis
- Uses Bedrock Claude + MCP servers + vector DB
- CPS 230 RTO requirement: 4 hours

**Tested failure modes:**
- MCP server unavailability
- LLM API latency spikes  
- Vector database degradation

**Result:** Resilience score with materiality classification and RTO breach detection.

---

## The Future We're Previewing

When APRA-regulated entities have fleets of agents handling material operations:

1. **Automated CPS 230 scenario testing** — Continuous resilience validation
2. **Real-time RTO monitoring** — EventBridge-driven impact detection
3. **Audit-ready evidence** — One-click APRA examination packages
4. **Auto-materiality classification** — Transaction pattern analysis
5. **GRC platform integration** — ServiceNow, Archer, MetricStream connectors

---

## Tech Stack

- **AWS Agent Registry** — Agent discovery and catalog
- **Python** — Simulation engine
- **Static HTML** — Self-contained dashboard output
- **Bedrock AgentCore** — Runtime target (future)

---

## Why This Matters

CPS 230 became enforceable in 2025. APRA expects operational resilience testing for material business services.

But what happens when those "services" are AI agents?

Most banks don't have this figured out yet. This demo asks: *what might it look like when they do?*

---

## License

MIT — Fork it, break it, extend it. Just don't blame me if APRA asks hard questions.

---

*Built in 2 hours for a LinkedIn demo. Not investment advice. Not compliance advice. Just exploration.*
