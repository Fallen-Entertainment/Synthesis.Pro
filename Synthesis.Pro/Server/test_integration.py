"""Quick test of RAG bridge integration"""
import json
import os
from pathlib import Path

# Create test input
test_input = {
    "command": "start_session",
    "session_id": "test_session_001",
    "output_file": "test_output.json"
}

input_file = "test_input.json"
with open(input_file, 'w') as f:
    json.dump(test_input, f)

# Run bridge
os.system(f'./python/python.exe rag_bridge.py {input_file}')

# Check output
if Path("test_output.json").exists():
    with open("test_output.json", 'r') as f:
        result = json.load(f)
    print("SUCCESS!")
    print(json.dumps(result, indent=2))
    
    # Cleanup
    os.remove(input_file)
    os.remove("test_output.json")
else:
    print("FAILED - No output file created")
