import json
import os

# Read the game file to extract BUILDING_HIERARCHY and TRANSITIONS
with open("dead_world_intro_v_omega.py", "r", encoding="utf-8") as f:
    content = f.read()

# Very basic extraction using exec in a clean dictionary
local_scope = {}
# Find where BUILDING_HIERARCHY starts
start_idx = content.find("BUILDING_HIERARCHY = {")
# Find where TRANSITIONS list ends (before get_room_context)
end_idx = content.find("def get_room_context(room_key):")

if start_idx != -1 and end_idx != -1:
    code_to_exec = content[start_idx:end_idx]
    
    # We also need to define _room_to_container so it doesn't crash during exec
    # so let's just run it
    try:
        exec(code_to_exec, {}, local_scope)
    except Exception as e:
        print("Error execing extracted code:", e)

buildings = local_scope.get("BUILDING_HIERARCHY", {})
transitions = local_scope.get("TRANSITIONS", [])

# Generate Cytoscape Elements
elements = []

# 1. Add World Node (Root)
elements.append({
    "data": {"id": "world", "label": "Dead World", "type": "world"}
})

# 2. Add Buildings
for b_key, b_data in buildings.items():
    elements.append({
        "data": {
            "id": b_key, 
            "parent": "world",
            "label": b_data.get("name", b_key),
            "type": "building"
        }
    })
    
    # 3. Add Floors
    for f_key, f_rooms in b_data.get("floors", {}).items():
        f_id = f"{b_key}_{f_key}"
        elements.append({
            "data": {
                "id": f_id,
                "parent": b_key,
                "label": f_key.capitalize(),
                "type": "floor"
            }
        })
        
        # 4. Add Rooms
        for r_key in f_rooms:
            elements.append({
                "data": {
                    "id": r_key,
                    "parent": f_id,
                    "label": r_key.replace('_', ' ').title(),
                    "type": "room"
                }
            })

# 5. Add Transitions (Edges)
for i, t in enumerate(transitions):
    # Some edges may be bi-directional or locked
    source = t.get("from")
    target = t.get("to")
    t_type = t.get("type", "passage")
    locked = t.get("locked", False)
    
    # Cytoscape needs unique edge IDs
    edge_id = f"e{i}_{source}_{target}"
    
    label = t_type
    if locked:
        label += " (LOCKED)"
        
    elements.append({
        "data": {
            "id": edge_id,
            "source": source,
            "target": target,
            "label": label,
            "type": t_type,
            "locked": locked
        },
        "classes": "locked" if locked else "unlocked"
    })

# Now generate the HTML template
html_template = """<!DOCTYPE html>
<html>
<head>
    <title>Dead World Map - Hierarchical Container Architecture</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <script src="https://unpkg.com/dagre@0.7.4/dist/dagre.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/cytoscape-dagre@2.5.0/cytoscape-dagre.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #1e1e1e;
            color: #fff;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        #header {
            padding: 20px;
            background-color: #2d2d2d;
            border-bottom: 1px solid #444;
            box-shadow: 0 2px 5px rgba(0,0,0,0.5);
        }
        h1 { margin: 0 0 10px 0; font-size: 24px; color: #4CAF50; }
        p { margin: 0; color: #aaa; font-size: 14px; }
        #cy {
            flex-grow: 1;
            display: block;
        }
        .controls {
            position: absolute;
            top: 100px;
            right: 20px;
            z-index: 10;
            background: rgba(45, 45, 45, 0.9);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #555;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-bottom: 5px;
            width: 100%;
        }
        button:hover { background-color: #45a049; }
    </style>
</head>
<body>
    <div id="header">
        <h1>Dead World - Hierarchical Container Map</h1>
        <p>Architecture: World &rarr; Buildings &rarr; Floors &rarr; Rooms. All movement via transition edges.</p>
    </div>
    
    <div class="controls">
        <button id="layout-fcose">Compound Layout</button>
        <button id="layout-dagre">Hierarchical Layout</button>
        <button id="layout-circle">Circle Layout</button>
        <p style="margin-top:15px; font-size:12px;"><b>Legend:</b><br/>
        <span style="color:#d32f2f">&#9632;</span> Locked Transition<br/>
        <span style="color:#64b5f6">&#9632;</span> Open Transition</p>
    </div>

    <div id="cy"></div>
    
    <script>
        var elements = __ELEMENTS__;
        
        var cy = cytoscape({
            container: document.getElementById('cy'),
            elements: elements,
            style: [
                {
                    selector: 'node[type="room"]',
                    style: {
                        'background-color': '#4CAF50',
                        'label': 'data(label)',
                        'color': '#fff',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '12px',
                        'width': 'label',
                        'padding': '15px',
                        'shape': 'round-rectangle'
                    }
                },
                {
                    selector: 'node[type="floor"]',
                    style: {
                        'background-color': 'rgba(100, 100, 100, 0.2)',
                        'label': 'data(label)',
                        'padding': '25px',
                        'color': '#ddd',
                        'font-size': '16px',
                        'font-weight': 'bold',
                        'text-valign': 'top',
                        'text-halign': 'center',
                        'border-width': 2,
                        'border-color': '#555',
                        'border-style': 'dashed'
                    }
                },
                {
                    selector: 'node[type="building"]',
                    style: {
                        'background-color': 'rgba(50, 50, 80, 0.4)',
                        'label': 'data(label)',
                        'padding': '35px',
                        'color': '#64b5f6',
                        'font-size': '22px',
                        'font-weight': 'bold',
                        'text-valign': 'top',
                        'text-halign': 'center',
                        'border-width': 2,
                        'border-color': '#64b5f6'
                    }
                },
                {
                    selector: 'node[type="world"]',
                    style: {
                        'background-color': 'rgba(20, 20, 20, 0.8)',
                        'label': 'data(label)',
                        'padding': '50px',
                        'color': '#fff',
                        'font-size': '28px',
                        'font-weight': 'bold',
                        'text-valign': 'top',
                        'text-halign': 'center',
                        'border-width': 3,
                        'border-color': '#4CAF50'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#888',
                        'target-arrow-color': '#888',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '10px',
                        'color': '#ccc',
                        'text-outline-width': 1,
                        'text-outline-color': '#222'
                    }
                },
                {
                    selector: 'edge.locked',
                    style: {
                        'line-color': '#d32f2f',
                        'target-arrow-color': '#d32f2f',
                        'line-style': 'dashed',
                        'width': 3
                    }
                },
                {
                    selector: 'edge.unlocked',
                    style: {
                        'line-color': '#64b5f6',
                        'target-arrow-color': '#64b5f6'
                    }
                }
            ],
            layout: {
                name: 'dagre',
                rankDir: 'TB',
                padding: 50,
                spacingFactor: 1.5
            }
        });
        
        document.getElementById('layout-dagre').addEventListener('click', function(){
            cy.layout({ name: 'dagre', rankDir: 'TB', padding: 50, spacingFactor: 1.5 }).run();
        });
        document.getElementById('layout-circle').addEventListener('click', function(){
            cy.layout({ name: 'circle', padding: 50 }).run();
        });
        document.getElementById('layout-fcose').addEventListener('click', function(){
            // Fallback since fcose might require an extension, let's just use breadthfirst for compunds
            cy.layout({ name: 'breadthfirst', directed: true, padding: 50 }).run();
        });
        
        // Initial fit
        cy.ready(function() {
            cy.fit();
        });
    </script>
</body>
</html>
"""

html_output = html_template.replace("__ELEMENTS__", json.dumps(elements))

output_path = "hierarchical_map.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_output)

print(f"Generated Hierarchical Map successfully at {os.path.abspath(output_path)}")
