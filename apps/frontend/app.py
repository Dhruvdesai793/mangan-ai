"""MANGAN-AI Streamlit client. All domain data comes from FastAPI."""
from __future__ import annotations

import json
import os
from typing import Any

import folium
import httpx
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

API_URL = os.getenv("FRONTEND_API_URL", "http://localhost:8000").rstrip("/")
SCENARIOS = {
    "Normal operations": "scenario_01_normal.json",
    "Heavy rainfall": "scenario_02_rainfall.json",
    "Equipment failure": "scenario_03_equipment_failure.json",
}

st.set_page_config(page_title="MANGAN-AI", page_icon="⛰️", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600&family=Libre+Serif:wght@700&display=swap');
:root { --forest:#2d4a2b; --sage:#7d8471; --olive:#a4ac86; --ivory:#faf9f6; --ink:#1d2a1c; }
html, body, [class*="css"], .stApp { font-family:FreeSans,'Libre Franklin',sans-serif; color:var(--ink); }
.stApp { background:linear-gradient(145deg,#faf9f6 0%,#f2f4ec 60%,#e8eddf 100%); }
h1,h2,h3,h4,h5,h6 { font-family:FreeSerif,'Libre Serif',serif !important; font-weight:700 !important; color:var(--forest) !important; }
[data-testid="stSidebar"] { background:var(--forest); }
[data-testid="stSidebar"] * { color:var(--ivory) !important; }
[data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] input[type="number"], [data-testid="stSidebar"] div[data-baseweb="input"] input { color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; background:var(--ivory) !important; caret-color:var(--forest) !important; }
[data-testid="stSidebar"] input::placeholder, [data-testid="stSidebar"] textarea::placeholder { color:var(--sage) !important; opacity:1 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] *, [data-testid="stSidebar"] [data-baseweb="select"] input { color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; }
[data-testid="stSidebar"] [data-baseweb="select"] { background:var(--ivory) !important; }
.hero { padding:1.5rem 1.7rem; border-radius:18px; color:var(--ivory); background:linear-gradient(120deg,#2d4a2b,#566b4d); box-shadow:0 12px 36px #2d4a2b24; margin-bottom:1.2rem; }
.hero h1 { color:var(--ivory) !important; margin:0; font-size:2.35rem; }.hero p { margin:.35rem 0 0; color:#e9eddc; }
.status { display:inline-block; padding:.22rem .55rem; border-radius:999px; font-size:.75rem; font-weight:600; }
.LIVE { background:#dcebd6; color:#21451f; }.DEMO { background:#efe7bd; color:#675813; }.UNAVAILABLE { background:#ecd4cf; color:#762d24; }
.model-card { background:#fffdf9; border:1px solid #dfe4d7; border-left:5px solid var(--olive); border-radius:13px; padding:1rem; min-height:205px; box-shadow:0 4px 18px #2d4a2b12; }
.model-card pre { white-space:pre-wrap; font-size:.76rem; max-height:170px; overflow:auto; }
.notice { border-radius:10px; padding:.75rem 1rem; background:#f1ead0; border:1px solid #d4c988; }
.stButton>button { border-radius:10px; background:var(--forest); color:var(--ivory); border:0; font-weight:600; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60, show_spinner=False)
def api_get(path: str) -> Any:
    with httpx.Client(timeout=30) as client:
        response = client.get(f"{API_URL}{path}")
        response.raise_for_status()
        return response.json()


def api_post(path: str, payload: dict, timeout: float = 120) -> Any:
    with httpx.Client(timeout=timeout) as client:
        response = client.post(f"{API_URL}{path}", json=payload)
        response.raise_for_status()
        return response.json()


def render_model(model_id: str, result: dict) -> None:
    status = result.get("status", "UNAVAILABLE")
    label = model_id.replace("_", " ").title()
    if model_id == "grade" and status == "LIVE": label = "Verified MOIL product-grade reference"
    if model_id == "production" and status == "LIVE": label = "Official MOIL historical production reference"
    prediction = result.get("prediction")
    with st.container(border=True):
        st.markdown(f'<span class="status {status}">{status}</span>', unsafe_allow_html=True)
        st.markdown(f"### {label}")
        st.caption(f'{result.get("model_version", "—")} · {result.get("data_source", "—")}')
        if result.get("reason"):
            st.warning(result["reason"])
        if status == "UNAVAILABLE":
            st.info("This model did not produce a result for the selected inputs.")
        elif model_id == "blast":
            score = float((prediction or {}).get("delay_risk", 0))
            st.metric("Blast delay risk", f"{score:.0%}")
            st.progress(max(0, min(1, score)))
            st.caption("Scenario estimate · review blast schedule if elevated")
        elif model_id == "equipment":
            p = prediction or {}
            a, b = st.columns(2)
            a.metric("Availability", f'{p.get("availability_pct", "—")}%')
            b.metric("Failure risk", f'{float(p.get("failure_risk", 0)):.0%}')
            if p.get("equipment_id"): st.caption(f'Focus equipment · {p["equipment_id"]}')
            if isinstance(p.get("availability_pct"), (int, float)):
                st.progress(max(0, min(1, float(p["availability_pct"]) / 100)))
        elif model_id == "grade":
            p = prediction or {}
            st.caption("Verified product reference · not an in-situ spatial prediction")
            interval = p.get("interval", ["—", "—"])
            a, b, c = st.columns(3)
            a.metric("Mn grade", f'{p.get("mn_grade_percent", "—")}%')
            b.metric("Reference interval", f'{interval[0]}–{interval[1]}%')
            c.metric("Year", str(p.get("reference_year", "—")))
            chemistry = p.get("chemistry") or {}
            with st.expander("Assay chemistry"):
                for col, (name, title) in zip(st.columns(4), [("mn_pct", "Mn"), ("fe_pct", "Fe"), ("sio2_pct", "SiO₂"), ("p_pct", "P")]):
                    col.metric(title, f'{chemistry.get(name, "—")} wt%')
        elif model_id == "production":
            p = prediction or {}
            st.caption("Official historical context · not a future forecast")
            a, b, c = st.columns(3)
            a.metric("Historical production", f'{float(p.get("historical_production_tonnes", 0)):,.0f} t')
            b.metric("Reference year", str(p.get("reference_year", "—")))
            c.metric("Average grade", str(p.get("average_grade_label", "—")))
            if p.get("a_plus_b_tonnes") is not None:
                st.metric("A+B resources/reserves reference", f'{float(p["a_plus_b_tonnes"]):,.0f} t')
        elif model_id == "prospectivity":
            score = float(prediction) if isinstance(prediction, (int, float)) else None
            if score is not None:
                st.metric("Prospectivity probability", f"{score:.1%}")
                st.progress(max(0, min(1, score)))
                if result.get("uncertainty") is not None: st.caption(f'Uncertainty proxy · ±{float(result["uncertainty"]):.1%}')
                st.caption("Relative model score; not a reserve-tonnage estimate.")
        elif model_id == "recovery":
            value = (prediction or {}).get("expected_recovery_pct")
            st.metric("Expected recovery", f"{value}%" if value is not None else "Unavailable")
            st.caption("Scenario estimate")
        elif model_id == "weather":
            p = prediction or {}
            a, b = st.columns(2)
            a.metric("Rainfall forecast", f'{p.get("rainfall_mm_forecast", "—")} mm')
            b.metric("Weather risk", str(p.get("risk", "—")))
            st.caption("Scenario estimate · confirm with live weather feed")
        else:
            st.json(prediction)


def lease_map(mine: dict, lease: dict, score_points: list[dict] | None = None) -> folium.Map:
    fmap = folium.Map(location=[mine["latitude"], mine["longitude"]], zoom_start=12, tiles="OpenStreetMap")
    if lease.get("features"):
        layer = folium.GeoJson(
            lease, name="Verified NGDR lease", style_function=lambda _f: {
                "color": "#2d4a2b", "weight": 3, "fillColor": "#a4ac86", "fillOpacity": .24,
            }, tooltip=folium.GeoJsonTooltip(fields=["official_lease_name", "site_id"], aliases=["Lease", "Site"]),
        )
        layer.add_to(fmap)
        fmap.fit_bounds(layer.get_bounds())
    folium.Marker([mine["latitude"], mine["longitude"]], tooltip=mine["mine_name"], popup=f'{mine["district"]}, {mine["state"]}', icon=folium.Icon(color="green", icon="info-sign")).add_to(fmap)
    for point in score_points or []:
        value = float(point["prospectivity"])
        color = "#2d4a2b" if value >= .7 else "#a4ac86" if value >= .4 else "#c9b77d"
        folium.CircleMarker([point["latitude"], point["longitude"]], radius=4, color=color, fill=True, fill_opacity=.65, tooltip=f"Score {value:.2f}").add_to(fmap)
    folium.LayerControl().add_to(fmap)
    return fmap


st.markdown('<section class="hero"><h1>MANGAN-AI</h1><p>Evidence-led manganese mining intelligence · MOIL reference integration</p></section>', unsafe_allow_html=True)
try:
    health, mines = api_get("/health"), api_get("/mines")
except Exception as exc:
    st.error(f"FastAPI is not reachable at {API_URL}. Start the local stack and refresh. ({exc})")
    st.stop()

with st.sidebar:
    st.header("Control room")
    st.caption(f"API · {health.get('database', 'unknown')} database · GEE {health.get('gee', 'unknown')}")
    mine_lookup = {m["mine_name"]: m for m in mines}
    selected_name = st.selectbox("Operational mine", list(mine_lookup))
    selected = mine_lookup[selected_name]
    scenario_name = st.selectbox("Operating scenario", list(SCENARIOS))
    run = st.button("Run intelligence bundle", use_container_width=True, type="primary")
    st.divider()
    st.subheader("Coordinate analysis")
    st.caption("Click the lease map or enter a coordinate to extract a buffered Earth Engine AOI.")
    coordinate = st.session_state.get("coordinate", {"latitude": selected["latitude"], "longitude": selected["longitude"]})
    target_lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=float(coordinate["latitude"]), format="%.6f", key="target_lat")
    target_lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=float(coordinate["longitude"]), format="%.6f", key="target_lon")
    target_buffer = st.number_input("AOI buffer (metres)", min_value=30, max_value=5000, value=250, step=10)
    target_name = st.text_input("Target name", value="")
    run_coordinate = st.button("Analyze selected coordinate", use_container_width=True)
    st.divider()
    st.caption("LIVE means the registered implementation executed. Grade and production are verified/historical references—not predictive models. DEMO modules remain scenario simulations.")

if run:
    with st.spinner("Building the evidence bundle…"):
        try:
            st.session_state["prediction"] = api_post("/predict/all", {"site_id": selected["site_id"], "scenario_file": SCENARIOS[scenario_name], "prospectivity_features": None})
        except Exception as exc:
            st.error(f"Prediction failed: {exc}")

overview, evidence, exploration, provenance = st.tabs(["Overview", "Model evidence", "Exploration", "Provenance"])
with overview:
    a, b, c, d = st.columns(4)
    a.metric("Mine", selected["mine_name"]); b.metric("District", selected["district"])
    c.metric("Method", selected["mining_method"]); d.metric("Status", selected["operational_status"])
    try:
        lease = api_get(f'/mines/{selected["site_id"]}/leases')
        map_event = st_folium(lease_map(selected, lease), use_container_width=True, height=480, returned_objects=["last_clicked"])
        if map_event and map_event.get("last_clicked"):
            st.session_state["coordinate"] = {"latitude": map_event["last_clicked"]["lat"], "longitude": map_event["last_clicked"]["lng"]}
            st.info(f'Coordinate selected: {map_event["last_clicked"]["lat"]:.6f}, {map_event["last_clicked"]["lng"]:.6f}. Click Analyze selected coordinate in the sidebar.')
    except Exception as exc: st.warning(f"Verified lease geometry unavailable: {exc}")
    result = st.session_state.get("prediction")
    if result:
        decision = result["decision"]
        st.subheader("Decision support")
        x, y = st.columns([1, 3]); x.metric("Risk level", decision["risk_level"])
        y.write("Primary drivers: " + (", ".join(decision["primary_drivers"]) or "No elevated drivers"))
        st.caption(f'Prospectivity feature source · {result.get("feature_source") or "not available"}')
        for action in decision["recommended_actions"]: st.info(f'{action["priority"]}: {action["action"]} — {action["reason"]}')
        if result.get("limitations"): st.markdown('<div class="notice"><b>Limitations</b><br>' + "<br>".join(result["limitations"]) + "</div>", unsafe_allow_html=True)

    coordinate_result = st.session_state.get("coordinate_prediction")
    if coordinate_result:
        st.subheader("Selected coordinate analysis")
        target = coordinate_result.get("target", {})
        prospectivity = coordinate_result.get("models", {}).get("prospectivity", {})
        score = prospectivity.get("prediction")
        a, b, c = st.columns(3)
        a.metric("Prospectivity", f"{float(score):.1%}" if isinstance(score, (int, float)) else "Unavailable")
        b.metric("Feature source", coordinate_result.get("feature_source", "—"))
        c.metric("AOI buffer", f'{target.get("buffer_m", target_buffer)} m')
        if isinstance(score, (int, float)):
            st.progress(float(score), text="Relative model score; not a reserve tonnage estimate")
        st.caption("Coordinate targets are persisted for reproducibility. Site-reference grade and production models are intentionally not inferred from arbitrary coordinates.")

if run_coordinate:
    with st.spinner("Extracting Earth Engine features for the selected coordinate…"):
        try:
            st.session_state["coordinate_prediction"] = api_post("/predict/coordinate", {"latitude": target_lat, "longitude": target_lon, "buffer_m": target_buffer, "target_name": target_name or None, "scenario_file": SCENARIOS[scenario_name]}, timeout=180)
            st.rerun()
        except Exception as exc:
            st.error(f"Coordinate analysis failed: {exc}")

with evidence:
    result = st.session_state.get("prediction")
    if not result: st.info("Run the intelligence bundle from the sidebar to populate model evidence.")
    else:
        items = list(result["models"].items())
        for start in range(0, len(items), 3):
            for column, (model_id, model_result) in zip(st.columns(3), items[start:start + 3]):
                with column: render_model(model_id, model_result)

with exploration:
    st.caption("The point layer is the existing Prospectivity v001 public/synthetic-fallback demonstration cache; it is not MOIL exploration ground truth.")
    threshold = st.slider("Minimum prospectivity", 0.0, 1.0, 0.45, .05)
    if st.button("Load prospectivity layer"):
        try:
            points = api_post("/exploration/map", {"limit": 500, "min_score": threshold})["points"]
            lease = api_get(f'/mines/{selected["site_id"]}/leases')
            st_folium(lease_map(selected, lease, points), use_container_width=True, height=530, returned_objects=[])
            if points:
                fig = go.Figure(go.Histogram(x=[p["prospectivity"] for p in points], marker_color="#2d4a2b"))
                fig.update_layout(title="Prospectivity score distribution", paper_bgcolor="#faf9f6", plot_bgcolor="#faf9f6")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as exc: st.error(f"Exploration layer failed: {exc}")

with provenance:
    st.subheader("Registry status"); st.json(api_get("/models"))
    st.subheader("Latest persisted runs")
    try: st.json(api_get(f'/mines/{selected["site_id"]}/predictions?limit=10'))
    except Exception as exc: st.caption(f"Prediction history unavailable: {exc}")
