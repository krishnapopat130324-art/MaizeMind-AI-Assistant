import networkx as nx
import json

def build_graph(arguments):
    """
    Convert extracted arguments to a NetworkX graph.
    Improved version with better visualization.
    """
    G = nx.DiGraph()
    
    # Handle string input (error case)
    if isinstance(arguments, str):
        arguments = {
            "claims": [{"id": "C1", "text": arguments[:100], "type": "main"}],
            "evidence": [],
            "relationships": []
        }
    
    # Add claim nodes
    for claim in arguments.get("claims", []):
        claim_id = claim.get("id", f"C{len(G.nodes()) + 1}")
        G.add_node(
            claim_id,
            label=claim.get("text", "Unnamed claim")[:100],
            full_text=claim.get("text", "Unnamed claim"),
            type=claim.get("type", "claim"),
            node_type="claim"
        )
    
    # Add evidence nodes
    for evidence in arguments.get("evidence", []):
        evidence_id = evidence.get("id", f"E{len(G.nodes()) + 1}")
        G.add_node(
            evidence_id,
            label=evidence.get("text", "Unnamed evidence")[:100],
            full_text=evidence.get("text", "Unnamed evidence"),
            type="evidence",
            node_type="evidence"
        )
        supports = evidence.get("supports")
        if supports and supports in G.nodes():
            G.add_edge(evidence_id, supports, relation="supports")
    
    # Add relationships
    for rel in arguments.get("relationships", []):
        source = rel.get("source")
        target = rel.get("target")
        if source and target and source in G.nodes() and target in G.nodes():
            G.add_edge(source, target, relation=rel.get("type", "supports"))
    
    # If no edges were added, try to connect nodes
    if G.number_of_edges() == 0 and G.number_of_nodes() > 1:
        nodes = list(G.nodes())
        main_node = None
        
        # Find main claim
        for node_id, data in G.nodes(data=True):
            if data.get("type") == "main":
                main_node = node_id
                break
        
        if main_node:
            for node_id in nodes:
                if node_id != main_node:
                    G.add_edge(node_id, main_node, relation="supports")
        else:
            # Connect first node to all others
            for i in range(1, len(nodes)):
                G.add_edge(nodes[i], nodes[0], relation="supports")
    
    # If no nodes, add placeholder
    if G.number_of_nodes() == 0:
        G.add_node("C1", label="No arguments found. Try again with clearer text.", 
                   full_text="No arguments found. Try again with clearer text.",
                   type="main", node_type="claim")
    
    # Convert to vis.js compatible format
    nodes_data = []
    for node_id, data in G.nodes(data=True):
        # Color coding based on type
        color = {
            "claim": "#4CAF50",        # Green
            "main": "#2196F3",         # Blue
            "supporting": "#4CAF50",   # Green
            "counter": "#F44336",      # Red
            "conclusion": "#9C27B0",   # Purple
            "evidence": "#FF9800"      # Orange
        }.get(data.get("type", "claim"), "#78909C")
        
        # Shape based on type
        shape = "box" if data.get("node_type") == "claim" else "ellipse"
        
        # Truncate label for display, keep full text for hover
        label = data.get("label", node_id)
        full_text = data.get("full_text", label)
        
        nodes_data.append({
            "id": node_id,
            "label": label,
            "title": full_text,  # Full text on hover
            "color": color,
            "shape": shape,
            "node_type": data.get("node_type", "unknown"),
            "type": data.get("type", "unknown")
        })
    
    edges_data = []
    for source, target, data in G.edges(data=True):
        relation = data.get("relation", "supports")
        # Make edges more descriptive
        label = relation
        edges_data.append({
            "from": source,
            "to": target,
            "label": label,
            "arrows": "to",
            "smooth": {
                "enabled": True,
                "type": "cubicBezier"
            },
            "color": {
                "color": "#888",
                "highlight": "#667eea"
            }
        })
    
    return {"nodes": nodes_data, "edges": edges_data}

def detect_gaps(graph_data):
    """
    Find claims that don't have supporting evidence.
    """
    if not graph_data or "nodes" not in graph_data:
        return []
    
    nodes = {n["id"]: n for n in graph_data["nodes"]}
    edges_from = {}
    
    for edge in graph_data.get("edges", []):
        edges_from.setdefault(edge["from"], []).append(edge["to"])
    
    gaps = []
    for node_id, node in nodes.items():
        # Check if this is a claim
        if node.get("node_type") == "claim" or node.get("type") in ["claim", "main", "supporting", "counter", "conclusion"]:
            # Check if this claim has any incoming support
            has_support = False
            
            # Check edges from other nodes to this claim
            for from_node, targets in edges_from.items():
                if node_id in targets:
                    # Check if the edge has a "supports" label
                    for edge in graph_data.get("edges", []):
                        if edge.get("to") == node_id and edge.get("from") == from_node:
                            if edge.get("label") == "supports":
                                has_support = True
                                break
                    if has_support:
                        break
            
            # Also check if there's evidence directly supporting this claim
            if not has_support:
                for edge in graph_data.get("edges", []):
                    if edge.get("to") == node_id and edge.get("label") == "supports":
                        from_node = nodes.get(edge["from"])
                        if from_node and from_node.get("node_type") == "evidence":
                            has_support = True
                            break
            
            # Don't flag the main claim or if it's a counter-claim
            if not has_support and node.get("id") != "C1" and node.get("type") != "counter":
                gaps.append(node)
    
    return gaps

def get_statistics(graph_data):
    """Get statistics about the argument graph"""
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    
    claim_count = sum(1 for n in nodes if n.get("node_type") == "claim" or n.get("type") in ["claim", "main", "supporting", "counter", "conclusion"])
    evidence_count = sum(1 for n in nodes if n.get("node_type") == "evidence" or n.get("type") == "evidence")
    
    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "claims": claim_count,
        "evidence": evidence_count,
        "relationships": len(edges)
    }