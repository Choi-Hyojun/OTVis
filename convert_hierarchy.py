"""Convert class hierarchies to a graph JSON format and merge annotation data."""

import os
import json
from rdflib import Graph, RDFS, OWL, BNode, URIRef

INPUT_DIR = "Ontology"
OUTPUT_DIR = "Graph"
AXIOM_DIR = "Axiom_per_entity"
DESC_DIR = "Ontology_description"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET_WITH_LABEL = [
    "swo_merged", "OntoDT"
]

def safe_qname(node, g, label_map=None):
    """Return a qname or label for *node* if available."""
    if label_map and node in label_map:
        return label_map[node]
    try:
        return g.qname(node)
    except Exception:
        return str(node)

def extract_force_graph(file_path, output_path):
    """Parse *file_path* and write a force-layout graph JSON to *output_path*."""
    g = Graph()
    if file_path.endswith((".owl", ".rdf")):
        parse_format = "xml"
    else:
        parse_format = "turtle"
    g.parse(file_path, format=parse_format)

    label_map = {}
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    use_label = base_name in TARGET_WITH_LABEL

    if use_label:
        for s, _, o in g.triples((None, RDFS.label, None)):
            if isinstance(s, URIRef):
                label_map[s] = str(o)

    nodes = set()
    links = []
    all_subjects = set()
    all_objects = set()

    for s, o in g.subject_objects(RDFS.subClassOf):
        if not (isinstance(s, URIRef) and isinstance(o, URIRef)):
            continue
        s_label = safe_qname(s, g, label_map)
        o_label = safe_qname(o, g, label_map)
        nodes.update([s_label, o_label])
        links.append({"source": s_label, "target": o_label})
        all_subjects.add(s_label)
        all_objects.add(o_label)

    true_roots = all_objects - all_subjects
    for r in true_roots:
        if r != "owl:Thing":
            links.append({"source": r, "target": "owl:Thing"})
            nodes.add("owl:Thing")

    # ------ 🔥 merge axioms and descriptions ------
    axiom_path = os.path.join(AXIOM_DIR, f"{base_name}_axiom.json")
    desc_path = os.path.join(DESC_DIR, f"{base_name}_description.json")
    class_axioms = {}
    class_descriptions = {}
    if os.path.exists(axiom_path):
        with open(axiom_path, encoding="utf-8") as f:
            axiom_data = json.load(f)
            class_axioms = axiom_data.get("classes", {})
    else:
        print(f"⚠️ No axiom file found: {axiom_path}")
    if os.path.exists(desc_path):
        with open(desc_path, encoding="utf-8") as f:
            desc_data = json.load(f)
            class_descriptions = desc_data.get("classes", {})
    else:
        print(f"⚠️ No description file found: {desc_path}")

    node_list = []
    for node in sorted(nodes):
        node_dict = {"id": node}
        # merge axioms
        if node in class_axioms:
            node_dict["axioms"] = class_axioms[node]
        # merge descriptions (include all fields as is)
        if node in class_descriptions:
            node_dict["description"] = class_descriptions[node]
        node_list.append(node_dict)

    graph_data = {
        "nodes": node_list,
        "links": links
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)
    print(f"✔️ Graph JSON saved: {output_path} (nodes={len(node_list)}, links={len(links)})")

def main():
    for fname in os.listdir(INPUT_DIR):
        if not (fname.endswith(".owl") or fname.endswith(".ttl") or fname.endswith(".rdf")):
            continue
        input_path = os.path.join(INPUT_DIR, fname)
        output_name = os.path.splitext(fname)[0] + "_graph.json"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        try:
            extract_force_graph(input_path, output_path)
        except Exception as e:
            print(f"❌ Failed to process {fname}: {e}")

if __name__ == "__main__":
    main()
