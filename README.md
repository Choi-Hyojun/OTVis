# OTVis

OTVis is a collection of utilities for visualizing the TBox structure of OWL ontologies. The provided Python scripts extract axioms and annotations into JSON files and `index.html` uses D3.js to display them as a graph.

## Directory layout
- `Ontology/` – input OWL files
- `Axiom_per_entity/` – axioms for each class/property (`*_axiom.json`)
- `Ontology_description/` – descriptions of classes and properties (`*_description.json`)
- `Graph/` – graph data used by the viewer (`*_graph.json`)
- `ontology_list.json` – list of ontology names shown on the web page
- Main scripts: `ontology_processing.py`, `description_extraction.py`, `convert_hierarchy.py`

## Python scripts

### ontology_processing.py
Collects class and property axioms from the ontology and saves them as JSON.

```python
output = {"classes": class_axioms, "properties": prop_axioms}
with open(axioms_file, "w", encoding="utf-8") as af:
    json.dump(output, af, indent=2, ensure_ascii=False)
```

### description_extraction.py
Extracts `rdfs:comment` and `oboInOwl:hasDefinition` annotations into a description file.

```python
output = {
    "classes": class_ann_dict,
    "properties": prop_ann_dict
}
base = os.path.splitext(fname)[0]
out_fname = f"{base}_description.json"
out_path = os.path.join(OUTPUT_DIR, out_fname)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
```

### convert_hierarchy.py
Reads the class hierarchy to generate a graph JSON and merges the axiom and description information.

```python
axiom_path = os.path.join(AXIOM_DIR, f"{base_name}_axiom.json")
desc_path = os.path.join(DESC_DIR, f"{base_name}_description.json")
...
node_dict = {"id": node}
if node in class_axioms:
    node_dict["axioms"] = class_axioms[node]
if node in class_descriptions:
    node_dict["description"] = class_descriptions[node]
```

## Web viewer
`index.html` displays an interactive graph with D3.js. Use the top panel to select an ontology and focus on a specific class.

```html
<div id="controls">
  <label>Select ontology: </label>
  <select id="ontology-select"></select>
  <button onclick="loadOntology()">Load</button>
  <br /><br />
  <label>Focus class: </label>
  <input type="text" id="focus-id" placeholder="e.g., owl:Thing" />
  <button onclick="focusOnNode()">Focus</button>
</div>
```

The page loads the ontology list and `loadOntology()` fetches the graph data.

```javascript
fetch("ontology_list.json")
  .then((res) => res.json())
  .then((list) => {
    const select = document.getElementById("ontology-select")
    list.forEach((name) => {
      const option = document.createElement("option")
      option.value = name
      option.textContent = name
      select.appendChild(option)
    })
  })

function loadOntology() {
  const name = document.getElementById("ontology-select").value
  const filePath = `Graph/${name}_graph.json?v=${Date.now()}`
  ...
}
```

## Usage
1. Place OWL files in `Ontology/` and add their names to `ontology_list.json` if needed.
2. Install RDFlib for Python 3.
   ```bash
   pip install rdflib
   ```
3. Run the scripts in order to generate the JSON data.
   ```bash
   python ontology_processing.py
   python description_extraction.py
   python convert_hierarchy.py
   ```
4. Start a local web server and open `index.html` in your browser.
   ```bash
   python -m http.server 8000
   ```
   Then visit `http://localhost:8000/index.html`.

