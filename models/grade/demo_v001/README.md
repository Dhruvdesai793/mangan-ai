# Mn Grade -- demo_v001 (Status: DEMO)
Simulation module, not a trained model. Returns the grade figure from the
active scenario (`scenarios/*.json`) so the dashboard has an internally
consistent number to show alongside prospectivity. Replace with a real
regression model once assay/grade ground-truth data is available -- keep the
same `predict(input) -> ModelResult` signature.
