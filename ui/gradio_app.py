import gradio as gr
import requests
import json
import time


API_BASE = "http://localhost:8000/api/v1"


def submit_research(question: str, depth: str) -> str:
    """Submit research question and return run_id."""
    try:
        resp = requests.post(
            f"{API_BASE}/research",
            json={"question": question, "depth": depth, "output_format": "report"},
            timeout=10
        )
        data = resp.json()
        return data.get("run_id", "error")
    except Exception as e:
        return f"error: {str(e)}"


def poll_status(run_id: str) -> str:
    """Poll run status."""
    if run_id.startswith("error"):
        return run_id
    
    try:
        resp = requests.get(f"{API_BASE}/status/{run_id}", timeout=5)
        return resp.json().get("status", "unknown")
    except:
        return "error"


def get_report(run_id: str) -> str:
    """Fetch final report."""
    if not run_id or run_id.startswith("error"):
        return "No run ID available"
    
    try:
        resp = requests.get(f"{API_BASE}/report/{run_id}", timeout=10)
        if resp.status_code == 404:
            return "Report not ready yet. Check status."
        data = resp.json()
        return data.get("report_markdown", "No report available")
    except Exception as e:
        return f"Error fetching report: {str(e)}"


def stream_events(run_id: str):
    """
    Generator for SSE events.
    Yields updates for Gradio's live trace panel.
    """
    if run_id.startswith("error"):
        yield f"❌ Error starting research: {run_id}"
        return
    
    yield f"🔬 Run ID: {run_id}\n⏳ Connecting to event stream...\n"
    
    try:
        resp = requests.get(
            f"{API_BASE}/stream/{run_id}",
            stream=True,
            timeout=300
        )
        
        for line in resp.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    try:
                        event = json.loads(line[6:])
                        event_type = event.get("type", "unknown")
                        
                        if event_type == "run_started":
                            yield f"🚀 Research started: {event.get('question', '')[:80]}...\n"
                        elif event_type == "node_start":
                            yield f"▶️  {event['node']} started...\n"
                        elif event_type == "node_complete":
                            latency = event.get("latency_ms", 0)
                            yield f"✅ {event['node']} complete ({latency}ms)\n"
                        elif event_type == "declined":
                            yield f"❌ DECLINED: {event.get('reason', '')}\n"
                        elif event_type == "done":
                            quality = event.get("quality_score")
                            latency = event.get("total_latency_ms")
                            yield f"\n🎉 Pipeline complete!"
                            if quality:
                                yield f" Quality: {quality:.2f}"
                            if latency:
                                yield f" | Total: {latency}ms"
                            yield "\n"
                            break
                        elif event_type == "error":
                            yield f"\n❌ ERROR: {event.get('error_type', 'Unknown')}\n"
                            yield f"Message: {event.get('message', '')}\n"
                            if event.get('traceback'):
                                yield f"Details: {event['traceback'][:200]}...\n"
                            break
                            
                    except json.JSONDecodeError:
                        continue
                        
    except Exception as e:
        yield f"\n❌ Stream error: {str(e)}\n"


def get_history() -> str:
    """Fetch recent research history."""
    try:
        resp = requests.get(f"{API_BASE}/history?limit=10", timeout=5)
        data = resp.json()
        runs = data.get("runs", [])
        
        lines = ["## Recent Research\n"]
        for run in runs:
            status_emoji = {
                "completed": "✅",
                "failed": "❌",
                "declined": "⚠️",
                "running": "⏳"
            }.get(run.get("status", ""), "❓")
            q = run.get("question", "")[:60]
            score = run.get("quality_score")
            score_str = f" (Q: {score:.2f})" if score else ""
            lines.append(f"{status_emoji} {q}...{score_str}")
        
        return "\n".join(lines) if len(lines) > 1 else "No history yet"
    except Exception as e:
        return f"Error loading history: {str(e)}"


def create_ui():
    """Create and return the Gradio Blocks UI."""
    
    with gr.Blocks(title="InSyfy — Autonomous Research Agent") as demo:
        gr.Markdown("""
        # 🔬 InSyfy
        ### Autonomous Research & Competitive Intelligence Agent
        
        Enter a research question below. InSyfy will:
        1. Plan sub-queries
        2. Search the web in parallel
        3. Retrieve from memory
        4. Synthesize findings with citations
        5. Self-critique and retry if needed
        6. Deliver a structured report
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Input panel
                question_input = gr.Textbox(
                    label="Research Question",
                    placeholder="What are the latest advances in...",
                    lines=3
                )
                
                with gr.Row():
                    depth_selector = gr.Dropdown(
                        choices=["quick", "standard", "deep"],
                        value="standard",
                        label="Research Depth"
                    )
                    submit_btn = gr.Button("Start Research", variant="primary")
                
                # Live trace panel
                gr.Markdown("---")
                gr.Markdown("### 📡 Live Agent Trace")
                trace_output = gr.Textbox(
                    label="",
                    lines=12,
                    interactive=False,
                    autoscroll=True
                )
                
                # Report output
                gr.Markdown("---")
                gr.Markdown("### 📄 Final Report")
                report_output = gr.Markdown()
            
            with gr.Column(scale=1):
                # History panel
                gr.Markdown("### 📚 History")
                history_output = gr.Markdown()
                refresh_history_btn = gr.Button("Refresh History")
        
        # State
        run_id_state = gr.State("")
        
        # Event handlers
        def on_submit(question, depth):
            run_id = submit_research(question, depth)
            if run_id.startswith("error"):
                return run_id, f"❌ Failed to start: {run_id}\n", ""
            return run_id, f"🔬 Started run: {run_id}\n⏳ Waiting for events...\n", ""
        
        def on_stream(run_id):
            for update in stream_events(run_id):
                yield update
        
        def on_complete(run_id):
            # Wait for pipeline to finish
            for _ in range(60):  # Max 60 seconds wait
                status = poll_status(run_id)
                if status in ("completed", "failed", "declined", "error"):
                    break
                time.sleep(1)
            
            report = get_report(run_id)
            return report
        
        def on_refresh():
            return get_history()
        
        # Wire up: submit → get run_id → start streaming → get report
        submit_btn.click(
            fn=on_submit,
            inputs=[question_input, depth_selector],
            outputs=[run_id_state, trace_output, report_output]
        ).then(
            fn=on_stream,
            inputs=[run_id_state],
            outputs=[trace_output]
        ).then(
            fn=on_complete,
            inputs=[run_id_state],
            outputs=[report_output]
        )
        
        refresh_history_btn.click(
            fn=on_refresh,
            outputs=[history_output]
        )
        
        # Load history on startup
        demo.load(fn=get_history, outputs=[history_output])
    
    return demo