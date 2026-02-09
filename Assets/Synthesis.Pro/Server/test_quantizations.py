"""
Test different quantization levels for Claudine
Find the optimal balance of speed vs quality
"""

import subprocess
import time
import json
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "database" / "synthesis_private.db"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Quantizations to test (ordered by expected speed: fastest first)
QUANTIZATIONS = [
    ("qwen2.5-coder:7b-instruct-q4_0", "Q4_0", "Fastest - most aggressive"),
    ("qwen2.5-coder:7b-instruct-q4_K_S", "Q4_K_S", "Fast - small footprint"),
    ("qwen2.5-coder:7b-instruct-q4_K_M", "Q4_K_M", "BASELINE - current"),
    ("qwen2.5-coder:7b-instruct-q5_K_M", "Q5_K_M", "Balanced - better quality"),
    ("qwen2.5-coder:7b-instruct-q8_0", "Q8_0", "Highest quality - slower"),
]

TEST_PROMPT = "Explain what makes a good AI system in one paragraph."

# Quality test prompts - check if lower quant affects accuracy
QUALITY_TESTS = [
    {
        "prompt": "What is 2 + 2?",
        "expected_answer": "4",
        "test": "basic_math"
    },
    {
        "prompt": "Complete this sentence: The capital of France is",
        "expected_answer": "Paris",
        "test": "basic_knowledge"
    },
    {
        "prompt": "If a Unity GameObject is null, what happens when you try to access its transform?",
        "expected_answer": "NullReferenceException",
        "test": "domain_knowledge"
    }
]

def pull_model(model_name: str):
    """Pull model if not already available"""
    print(f"\n[PULL] Checking model: {model_name}")
    try:
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            print(f"[OK] Model ready")
            return True
        else:
            print(f"[ERROR] Pull failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_quality(model_name: str):
    """Quick quality check - does it still answer correctly?"""
    import urllib.request

    print(f"\n[QUALITY CHECK] Testing accuracy...")
    passed = 0
    total = len(QUALITY_TESTS)

    for test in QUALITY_TESTS:
        payload = {
            "model": model_name,
            "prompt": test["prompt"],
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temp for accuracy
                "num_predict": 50
            }
        }

        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                answer = data.get('response', '').strip()

                # Check if expected answer is in response
                if test["expected_answer"].lower() in answer.lower():
                    passed += 1
                    print(f"  [OK] {test['test']}")
                else:
                    print(f"  [FAIL] {test['test']} - got: {answer[:50]}")

        except Exception as e:
            print(f"  [ERROR] {test['test']}: {e}")

    accuracy = (passed / total) * 100 if total > 0 else 0
    print(f"  Accuracy: {passed}/{total} ({accuracy:.0f}%)")
    return accuracy

def benchmark_quantization(model_name: str, quant_type: str, iterations: int = 3):
    """Benchmark a specific quantization"""
    import urllib.request

    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print(f"Type: {quant_type}")
    print(f"{'='*60}")

    results = []

    for i in range(iterations):
        print(f"Run {i+1}/{iterations}...", end=" ", flush=True)

        payload = {
            "model": model_name,
            "prompt": TEST_PROMPT,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "num_predict": 100
            }
        }

        start_time = time.time()
        first_token_time = None
        tokens_generated = 0

        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req) as response:
                for line in response:
                    if line:
                        data = json.loads(line.decode('utf-8'))

                        if 'response' in data:
                            if first_token_time is None:
                                first_token_time = time.time()
                            tokens_generated += 1

                        if data.get('done', False):
                            break

            end_time = time.time()
            total_time = end_time - start_time
            time_to_first_token = first_token_time - start_time if first_token_time else 0
            tokens_per_second = tokens_generated / total_time if total_time > 0 else 0

            results.append({
                'total_time': total_time,
                'time_to_first_token': time_to_first_token,
                'tokens_per_second': tokens_per_second,
                'tokens_generated': tokens_generated
            })

            print(f"[OK] {total_time:.2f}s ({tokens_per_second:.1f} tok/s)")

        except Exception as e:
            print(f"[ERROR] {e}")
            continue

    if results:
        avg_tps = sum(r['tokens_per_second'] for r in results) / len(results)
        avg_ttft = sum(r['time_to_first_token'] for r in results) / len(results)

        print(f"\nAverage: {avg_tps:.1f} tok/s | TTFT: {avg_ttft:.3f}s")

        return {
            'avg_tokens_per_second': avg_tps,
            'avg_time_to_first_token': avg_ttft,
            'runs': len(results)
        }

    return None

def save_results(results_list):
    """Save all quantization test results to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for result in results_list:
        cursor.execute("""
            INSERT INTO claudine_performance
            (timestamp, model_name, quantization, tokens_per_second,
             time_to_first_token, cold_start_penalty, test_context, optimization_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            result['model_name'],
            result['quantization'],
            result['avg_tps'],
            result['avg_ttft'],
            0.0,  # No cold start in these tests (model kept warm)
            'Quantization comparison test',
            result['notes']
        ))

    conn.commit()
    conn.close()

def main():
    print("\n" + "="*60)
    print("CLAUDINE QUANTIZATION OPTIMIZATION")
    print("Testing different quantization levels for speed")
    print("="*60)

    results_list = []
    baseline_tps = None

    for model_name, quant_type, description in QUANTIZATIONS:
        print(f"\n\n{'#'*60}")
        print(f"# {quant_type}: {description}")
        print(f"{'#'*60}")

        # Pull model if needed
        if not pull_model(model_name):
            print(f"[SKIP] Could not pull {model_name}")
            continue

        # Run quality test first
        accuracy = test_quality(model_name)

        # Run speed benchmark
        result = benchmark_quantization(model_name, quant_type, iterations=3)

        if result:
            result['accuracy'] = accuracy
            # Track baseline
            if quant_type == "Q4_K_M":
                baseline_tps = result['avg_tokens_per_second']

            # Calculate improvement vs baseline
            improvement = ""
            if baseline_tps:
                percent = ((result['avg_tokens_per_second'] - baseline_tps) / baseline_tps) * 100
                improvement = f" ({percent:+.1f}% vs baseline)"

            results_list.append({
                'model_name': model_name,
                'quantization': quant_type,
                'avg_tps': result['avg_tokens_per_second'],
                'avg_ttft': result['avg_time_to_first_token'],
                'accuracy': result['accuracy'],
                'notes': f"{description}{improvement}"
            })

            print(f"\n==> Result: {result['avg_tokens_per_second']:.1f} tok/s{improvement}")

        time.sleep(2)  # Brief pause between tests

    # Print summary
    print("\n\n" + "="*60)
    print("SUMMARY - Quantization Performance")
    print("="*60)

    # Sort by speed (fastest first)
    results_list.sort(key=lambda x: x['avg_tps'], reverse=True)

    print(f"\n{'Quantization':<12} {'Speed':<12} {'TTFT':<10} {'Accuracy':<12} {'Notes'}")
    print("-" * 80)

    for r in results_list:
        print(f"{r['quantization']:<12} {r['avg_tps']:>6.1f} tok/s  {r['avg_ttft']:>6.3f}s  {r['accuracy']:>5.0f}%       {r['notes']}")

    # Save to database
    print(f"\n[SAVE] Writing results to database...")
    save_results(results_list)
    print("[OK] Results saved to claudine_performance table")

    # Recommendation - best balance of speed and accuracy
    if results_list:
        # Filter to only accurate quantizations (>= 66% correct)
        accurate_results = [r for r in results_list if r['accuracy'] >= 66]

        if accurate_results:
            best = accurate_results[0]  # Fastest among accurate ones
            print(f"\n[RECOMMEND] Best quantization: {best['quantization']}")
            print(f"            Speed: {best['avg_tps']:.1f} tok/s")
            print(f"            Accuracy: {best['accuracy']:.0f}%")
            print(f"            Model: {best['model_name']}")

            if best['quantization'] != "Q4_K_M":
                baseline = next((r for r in results_list if r['quantization'] == "Q4_K_M"), None)
                if baseline:
                    improvement = ((best['avg_tps'] - baseline['avg_tps']) / baseline['avg_tps']) * 100
                    print(f"            Improvement: {improvement:+.1f}% faster than baseline")
        else:
            print(f"\n[WARNING] No quantization passed accuracy threshold")
            print(f"          Staying with Q4_K_M baseline")

if __name__ == "__main__":
    main()
