#!/usr/bin/env python3
"""
Agent Resilience Preview: CPS 230 Testing for AI Agents
Exploring how we'll test critical agent infrastructure tomorrow.

This is a 2-hour concept demo exploring the intersection of:
- APRA CPS 230 operational resilience requirements
- AWS Agent Registry for agent discovery
- Agentic infrastructure resilience testing

NOT PRODUCTION READY. This is a preview of what's coming.
"""

import json
import datetime
from dataclasses import dataclass

@dataclass
class TestScenario:
    name: str
    failure_mode: str
    impact_seconds: int
    rto_limit: int
    passed: bool
    mitigation: str = "N/A"
    critical: bool = False


def escape_html(text: str) -> str:
    """Escape HTML entities to prevent XSS injection."""
    if not isinstance(text, str):
        text = str(text)
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;"))

# Mock: AWS Agent Registry response (simulating real discovery)
MOCK_REGISTRY = {
    "agent_id": "fraud-detection-v2-prod",
    "name": "Real-time Fraud Detection Agent",
    "description": "Analyzes transactions for anomalous patterns using LLM reasoning",
    "metadata": {
        "cps230_material": True,
        "business_service": "Payment Processing",
        "daily_volume_usd": 2400000,
        "rto_hours": 4,
        "dependencies": [
            {"name": "transaction-mcp-server", "type": "mcp", "critical": True},
            {"name": "bedrock-claude-sonnet", "type": "llm", "critical": True},
            {"name": "fraud-vector-db", "type": "database", "critical": False}
        ]
    }
}

def discover_from_registry(agent_id: str) -> dict:
    """Simulate AWS Agent Registry discovery"""
    print(f"[SEARCH] Querying AWS Agent Registry for: {agent_id}")
    # In real version: boto3 call to agent-registry API
    return MOCK_REGISTRY

def validate_agent_data(agent: dict) -> bool:
    """Validate agent dictionary has required structure."""
    if not isinstance(agent, dict):
        raise ValueError("Agent must be a dictionary")
    if "metadata" not in agent:
        raise ValueError("Agent missing 'metadata' key")
    meta = agent["metadata"]
    if not isinstance(meta, dict):
        raise ValueError("Agent metadata must be a dictionary")
    required_meta = ["daily_volume_usd", "rto_hours", "dependencies"]
    for key in required_meta:
        if key not in meta:
            raise ValueError(f"Agent metadata missing required key: {key}")
    return True


def assess_materiality(agent: dict) -> dict:
    """CPS 230: Is this a material business service?"""
    validate_agent_data(agent)
    meta = agent["metadata"]
    volume = meta.get("daily_volume_usd", 0)
    if not isinstance(volume, (int, float)):
        volume = 0
    
    # CPS 230 materiality criteria (simplified)
    material = volume > 1_000_000  # $1M+ daily = material
    
    return {
        "material": material,
        "classification": "MATERIAL" if material else "NON-MATERIAL",
        "justification": f"Handles ${volume:,.0f} daily. Disruption = customer impact + potential regulatory breach.",
        "rto_required": f"{meta['rto_hours']} hours per CPS 230 operational resilience tolerance",
        "cps230_compliance_required": material
    }

def simulate_failure_scenarios(agent: dict) -> list:
    """
    Simulate what happens when dependencies fail.
    This is NOT real chaos engineering - just scenario modeling for CPS 230.
    """
    validate_agent_data(agent)
    meta = agent["metadata"]
    deps = meta.get("dependencies", [])
    rto_hours = meta.get("rto_hours", 4)
    if not isinstance(rto_hours, (int, float)) or rto_hours <= 0:
        rto_hours = 4  # Default to 4 hours if invalid
    rto_seconds = rto_hours * 3600
    scenarios = []
    
    for dep in deps:
        # Simulated impact modeling
        if dep["type"] == "llm":
            # LLM failure = queue backup, potential RTO breach
            impact = 7200  # 2 hours
            breach = impact > rto_seconds
            mitigation = "Circuit breaker + human escalation queue"
        elif dep["type"] == "mcp":
            # MCP server down = degraded mode
            impact = 600  # 10 min
            breach = False
            mitigation = "Failover to rule-based fallback"
        else:
            # Database = minimal impact (cached)
            impact = 300  # 5 min
            breach = False
            mitigation = "Stale cache acceptable for 30 min"
        
        scenarios.append(TestScenario(
            name=f"{dep['name']}_failure",
            failure_mode=f"{dep['name']} ({dep['type']}) unavailable",
            impact_seconds=impact,
            rto_limit=rto_seconds,
            passed=not breach,
            mitigation=mitigation,
            critical=dep.get("critical", False)
        ))
    
    return scenarios

def calculate_resilience_score(scenarios: list) -> dict:
    """CPS 230 readiness score"""
    total = len(scenarios)
    passed = sum(1 for s in scenarios if s.passed)
    critical_deps = [s for s in scenarios if getattr(s, 'critical', False)]
    critical_passed = sum(1 for s in critical_deps if s.passed)
    
    score = (passed / total) * 100 if total > 0 else 0
    
    return {
        "overall": round(score, 1),
        "status": "READY" if score >= 80 else "ACTION REQUIRED",
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "critical_deps": len(critical_deps),
        "critical_passed": critical_passed
    }

def generate_dashboard(agent: dict, materiality: dict, scenarios: list, score: dict) -> str:
    """Generate single-file HTML resilience dashboard"""
    
    # Escape all user-controlled input to prevent XSS
    agent_name = escape_html(agent.get("name", "Unknown"))
    agent_id = escape_html(agent.get("agent_id", "unknown"))
    agent_desc = escape_html(agent.get("description", ""))
    business_service = escape_html(agent.get("metadata", {}).get("business_service", "Unknown"))
    materiality_justification = escape_html(materiality.get("justification", ""))
    materiality_rto = escape_html(materiality.get("rto_required", ""))
    materiality_classification = escape_html(materiality.get("classification", "UNKNOWN"))
    
    # Build scenario rows using list + join for O(n) performance
    scenario_rows_parts = []
    for s in scenarios:
        status_class = "pass" if s.passed else "fail"
        status_icon = "[OK]" if s.passed else "[FAIL]"
        breach_text = "Yes - RTO Breach" if not s.passed else "No"
        critical_badge = "[CRITICAL]" if s.critical else ""
        
        scenario_rows_parts.append(f"""        <tr class="{status_class}">
            <td><strong>{escape_html(s.failure_mode)}</strong> {critical_badge}</td>
            <td>{s.impact_seconds/60:.0f} min</td>
            <td>{breach_text}</td>
            <td><span class="badge {status_class}">{status_icon} {status_class.upper()}</span></td>
        </tr>
        <tr class="details">
            <td colspan="4" class="mitigation">Mitigation: {escape_html(s.mitigation)}</td>
        </tr>""")
    
    scenario_rows = "\n".join(scenario_rows_parts)
    
    # Score color
    score_class = "high" if score["overall"] >= 80 else "medium" if score["overall"] >= 50 else "low"
    materiality_class = "material" if materiality.get("material", False) else "non-material"
    
    # Safe volume formatting
    daily_volume = agent.get("metadata", {}).get("daily_volume_usd", 0)
    rto_hours = agent.get("metadata", {}).get("rto_hours", 0)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Resilience Preview | CPS 230</title>
    <style>
        :root {{
            --aws-orange: #ff9900;
            --aws-dark: #232f3e;
            --pass: #1e8900;
            --fail: #d13212;
            --warn: #ff9900;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #232f3e;
            background: #f7f7f7;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .header {{
            background: var(--aws-dark);
            color: white;
            padding: 40px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #ff9900;
            font-size: 16px;
            font-weight: 500;
        }}
        
        .preview-badge {{
            display: inline-block;
            background: var(--aws-orange);
            color: var(--aws-dark);
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            margin-top: 15px;
        }}
        
        .materiality-banner {{
            background: {'#ff9900' if materiality["material"] else '#1e8900'};
            color: {'#232f3e' if materiality["material"] else 'white'};
            padding: 20px 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            font-weight: 600;
        }}
        
        .materiality-banner .label {{
            font-size: 12px;
            text-transform: uppercase;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .card {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .card h2 {{
            font-size: 20px;
            margin-bottom: 20px;
            color: var(--aws-dark);
            border-bottom: 2px solid var(--aws-orange);
            padding-bottom: 10px;
        }}
        
        .score-display {{
            text-align: center;
            padding: 30px;
        }}
        
        .score-number {{
            font-size: 72px;
            font-weight: bold;
            color: {('#1e8900' if score["overall"] >= 80 else '#ff9900' if score["overall"] >= 50 else '#d13212')};
        }}
        
        .score-status {{
            font-size: 24px;
            font-weight: 600;
            color: {('#1e8900' if score["overall"] >= 80 else '#ff9900' if score["overall"] >= 50 else '#d13212')};
            margin-top: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
        }}
        
        .stat {{
            background: #f7f7f7;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: var(--aws-dark);
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: var(--aws-dark);
            color: white;
            padding: 12px;
            text-align: left;
            font-size: 12px;
            text-transform: uppercase;
        }}
        
        td {{
            padding: 15px 12px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f7f7f7;
        }}
        
        .pass {{
            color: var(--pass);
        }}
        
        .fail {{
            color: var(--fail);
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        
        .badge.pass {{
            background: #e8f5e9;
            color: var(--pass);
        }}
        
        .badge.fail {{
            background: #ffebee;
            color: var(--fail);
        }}
        
        .details {{
            background: #fafafa;
        }}
        
        .mitigation {{
            font-size: 13px;
            color: #666;
            padding-top: 0;
        }}
        
        .info-list {{
            list-style: none;
        }}
        
        .info-list li {{
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .info-list li:last-child {{
            border-bottom: none;
        }}
        
        .label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            font-weight: 600;
        }}
        
        .value {{
            font-size: 16px;
            margin-top: 5px;
        }}
        
        .future-section {{
            background: linear-gradient(135deg, #232f3e 0%, #37475a 100%);
            color: white;
        }}
        
        .future-section h2 {{
            border-bottom-color: var(--aws-orange);
            color: white;
        }}
        
        .future-list {{
            list-style: none;
            margin-top: 15px;
        }}
        
        .future-list li {{
            padding: 10px 0;
            padding-left: 25px;
            position: relative;
        }}
        
        .future-list li::before {{
            content: "→";
            position: absolute;
            left: 0;
            color: var(--aws-orange);
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #999;
            font-size: 13px;
        }}
        
        .agent-info {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }}
        
        @media (max-width: 600px) {{
            .stats-grid, .agent-info {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Agent Resilience Preview</h1>
            <div class="subtitle">Exploring CPS 230 operational resilience for agentic infrastructure</div>
            <span class="preview-badge">2-Hour Concept Demo</span>
        </div>
        
        <div class="materiality-banner">
            <div class="label">CPS 230 Materiality Classification</div>
            <div style="font-size: 24px; margin-top: 5px;">
                {materiality_classification}: {agent_name}
            </div>
            <div style="margin-top: 10px; opacity: 0.9;">
                {materiality_justification} | {materiality_rto}
            </div>
        </div>
        
        <div class="card">
            <h2>Agent Discovery (AWS Agent Registry)</h2>
            <div class="agent-info">
                <div>
                    <div class="label">Agent ID</div>
                    <div class="value">{agent_id}</div>
                </div>
                <div>
                    <div class="label">Business Service</div>
                    <div class="value">{business_service}</div>
                </div>
                <div>
                    <div class="label">Daily Transaction Volume</div>
                    <div class="value">${daily_volume:,}</div>
                </div>
                <div>
                    <div class="label">CPS 230 RTO</div>
                    <div class="value">{rto_hours} hours</div>
                </div>
            </div>
            <div style="margin-top: 20px; padding: 15px; background: #f7f7f7; border-radius: 6px;">
                <div class="label">Description</div>
                <div class="value" style="font-size: 14px; margin-top: 8px;">{agent_desc}</div>
            </div>
        </div>
        
        <div class="card">
            <h2>CPS 230 Resilience Score</h2>
            <div class="score-display">
                <div class="score-number">{score["overall"]:.0f}</div>
                <div class="score-status">{score["status"]}</div>
                <div style="color: #666; margin-top: 10px;">
                    Based on {score["total_tests"]} failure scenario simulations
                </div>
            </div>
            <div class="stats-grid">
                <div class="stat">
                    <div class="stat-value">{score["passed"]}/{score["total_tests"]}</div>
                    <div class="stat-label">Tests Passed</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{score["critical_deps"]}</div>
                    <div class="stat-label">Critical Dependencies</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{score["critical_passed"]}</div>
                    <div class="stat-label">Critical Tests Passed</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Failure Scenario Tests</h2>
            <p style="color: #666; margin-bottom: 20px;">
                Simulated CPS 230 scenario testing against agent dependencies.
                <br><em>Note: These are modeled scenarios, not live chaos engineering.</em>
            </p>
            <table>
                <thead>
                    <tr>
                        <th>Dependency</th>
                        <th>Recovery Time</th>
                        <th>RTO Breach</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {scenario_rows}
                </tbody>
            </table>
        </div>
        
        <div class="card future-section">
            <h2>Looking Ahead</h2>
            <p style="opacity: 0.9; margin-bottom: 15px;">
                We're not there yet — but we will be. In 12-18 months, APRA-regulated entities 
                will have fleets of agents handling material operations. When that happens, 
                we'll need automated operational resilience controls.
            </p>
            <ul class="future-list">
                <li>Automated CPS 230 scenario testing for AI systems</li>
                <li>Real-time RTO monitoring with EventBridge integration</li>
                <li>Audit-ready evidence generation for APRA examinations</li>
                <li>Materiality auto-classification from transaction patterns</li>
                <li>Integration with existing GRC platforms (ServiceNow, Archer)</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            Agent Resilience Preview | APRA CPS 230 × AWS Agent Registry × Agentic Infrastructure</p>
            <p style="margin-top: 10px; font-size: 11px;">
                This is a concept demonstration exploring future operational resilience patterns. 
                Not production software. Not APRA guidance. Just a 2-hour exploration.
            </p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def main():
    print("=" * 60)
    print("AGENT RESILIENCE PREVIEW")
    print("Exploring CPS 230 operational resilience for AI agents")
    print("=" * 60)
    print()
    
    # Act 1: Discovery
    print("PHASE 1: DISCOVER FROM AWS AGENT REGISTRY")
    print("-" * 40)
    agent = discover_from_registry("fraud-detection-v2-prod")
    print(f"[OK] Found: {agent['name']}")
    print(f"  `- Daily volume: ${agent['metadata']['daily_volume_usd']:,}")
    print()
    
    # Act 2: Materiality Assessment
    print("PHASE 2: CPS 230 MATERIALITY ASSESSMENT")
    print("-" * 40)
    materiality = assess_materiality(agent)
    print(f"[OK] Classification: {materiality['classification']}")
    print(f"  `- {materiality['justification']}")
    print()
    
    # Act 3: Failure Simulation
    print("PHASE 3: FAILURE SCENARIO SIMULATION")
    print("-" * 40)
    scenarios = simulate_failure_scenarios(agent)
    for s in scenarios:
        status = "PASS" if s.passed else "FAIL"
        icon = "[OK]" if s.passed else "[XX]"
        print(f"  {icon} {s.name}: {status} ({s.impact_seconds/60:.0f}min recovery)")
    print()
    
    # Act 4: Score & Report
    print("PHASE 4: RESILIENCE SCORING")
    print("-" * 40)
    score = calculate_resilience_score(scenarios)
    print(f"[OK] Overall Score: {score['overall']}/100")
    print(f"  `- Status: {score['status']}")
    print(f"  `- Tests: {score['passed']}/{score['total_tests']} passed")
    print()
    
    # Generate output
    print("GENERATING DASHBOARD...")
    html = generate_dashboard(agent, materiality, scenarios, score)
    
    output_file = "resilience_preview.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"[DONE] Generated: {output_file}")
    print()
    print("=" * 60)
    print("Demo complete. Open resilience_preview.html in your browser.")
    print("=" * 60)

if __name__ == "__main__":
    main()
