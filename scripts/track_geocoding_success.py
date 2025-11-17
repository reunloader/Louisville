#!/usr/bin/env python3
"""
Track geocoding success metrics over time.

This script analyzes _data/geocoded_addresses.yml and maintains a historical
log of success rates, failure patterns, and improvements.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

try:
    import yaml
except ImportError:
    print("PyYAML not found, installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', '--quiet', 'pyyaml'])
    import yaml

# Configuration
DATA_FILE = "_data/geocoded_addresses.yml"
METRICS_FILE = "_data/geocoding_success_metrics.yml"
REPORT_FILE = "geocoding_success_report.md"


def load_geocoded_addresses() -> Dict[str, any]:
    """Load geocoded addresses from cache."""
    data_file = Path(DATA_FILE)

    if not data_file.exists():
        print(f"Warning: {DATA_FILE} not found")
        return {}

    with open(data_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def load_metrics_history() -> List[Dict]:
    """Load historical metrics."""
    metrics_file = Path(METRICS_FILE)

    if not metrics_file.exists():
        return []

    with open(metrics_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
        return data.get('history', [])


def save_metrics_history(history: List[Dict]):
    """Save metrics history to file."""
    metrics_file = Path(METRICS_FILE)
    metrics_file.parent.mkdir(parents=True, exist_ok=True)

    data = {
        'history': history,
        'last_updated': datetime.now().isoformat()
    }

    with open(metrics_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"✓ Saved metrics to {METRICS_FILE}")


def analyze_addresses(addresses: Dict[str, any]) -> Dict:
    """Analyze geocoded addresses and compute metrics."""

    total = len(addresses)
    successful = sum(1 for v in addresses.values() if v is not None)
    failed = total - successful

    success_rate = (successful / total * 100) if total > 0 else 0

    # Categorize failed addresses
    failed_addresses = [addr for addr, coords in addresses.items() if coords is None]

    # Analyze failure patterns
    failure_patterns = defaultdict(int)

    for addr in failed_addresses:
        # Check for common failure patterns
        if 'near' in addr.lower() or 'at' in addr.lower():
            failure_patterns['Contains location qualifiers (near/at)'] += 1
        elif '.' in addr.split(',')[0]:  # Period in address part (likely extra text)
            failure_patterns['Contains extra sentences/context'] += 1
        elif ' and ' in addr.lower():
            failure_patterns['Intersection format'] += 1
        elif any(word in addr.lower() for word in ['bravo', 'papa', 'x-ray', 'romeo']):
            failure_patterns['Police phonetic codes'] += 1
        elif addr.split(',')[0].count(' ') <= 2:  # Very short address
            failure_patterns['Incomplete/vague address'] += 1
        else:
            failure_patterns['Other/Unknown'] += 1

    metrics = {
        'timestamp': datetime.now().isoformat(),
        'total_addresses': total,
        'successful': successful,
        'failed': failed,
        'success_rate': round(success_rate, 2),
        'failure_rate': round(100 - success_rate, 2),
        'failure_patterns': dict(failure_patterns)
    }

    return metrics


def calculate_improvements(current: Dict, previous: Dict = None) -> Dict:
    """Calculate improvements since last run."""
    if not previous:
        return {
            'new_addresses': current['total_addresses'],
            'new_successes': current['successful'],
            'new_failures': current['failed']
        }

    improvements = {
        'new_addresses': current['total_addresses'] - previous.get('total_addresses', 0),
        'new_successes': current['successful'] - previous.get('successful', 0),
        'new_failures': current['failed'] - previous.get('failed', 0),
        'success_rate_change': round(current['success_rate'] - previous.get('success_rate', 0), 2)
    }

    return improvements


def generate_report(metrics: Dict, improvements: Dict, history: List[Dict]) -> str:
    """Generate a markdown report of geocoding success."""

    report = f"""# Geocoding Success Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Current Status

| Metric | Value |
|--------|-------|
| **Total Addresses** | {metrics['total_addresses']:,} |
| **Successfully Geocoded** | {metrics['successful']:,} |
| **Failed to Geocode** | {metrics['failed']:,} |
| **Success Rate** | {metrics['success_rate']:.2f}% |
| **Failure Rate** | {metrics['failure_rate']:.2f}% |

---

## Recent Changes

"""

    if improvements['new_addresses'] > 0:
        report += f"- **{improvements['new_addresses']}** new addresses processed\n"
        report += f"- **{improvements['new_successes']}** successfully geocoded\n"
        report += f"- **{improvements['new_failures']}** failed to geocode\n"

        if 'success_rate_change' in improvements and improvements['success_rate_change'] != 0:
            change_symbol = "📈" if improvements['success_rate_change'] > 0 else "📉"
            report += f"- Success rate changed by **{improvements['success_rate_change']:+.2f}%** {change_symbol}\n"
    else:
        report += "*No new addresses since last run*\n"

    report += "\n---\n\n"

    # Failure patterns
    if metrics['failure_patterns']:
        report += "## Failure Pattern Analysis\n\n"
        report += "| Pattern | Count | % of Failures |\n"
        report += "|---------|-------|---------------|\n"

        total_failures = sum(metrics['failure_patterns'].values())
        for pattern, count in sorted(metrics['failure_patterns'].items(),
                                     key=lambda x: x[1], reverse=True):
            percentage = (count / total_failures * 100) if total_failures > 0 else 0
            report += f"| {pattern} | {count} | {percentage:.1f}% |\n"

        report += "\n---\n\n"

    # Historical trend
    if len(history) > 1:
        report += "## Historical Trend\n\n"
        report += "| Date | Total | Successful | Success Rate |\n"
        report += "|------|-------|-----------|-------------|\n"

        # Show last 10 entries
        for entry in history[-10:]:
            date = entry.get('timestamp', '')[:10]  # Just the date part
            total = entry.get('total_addresses', 0)
            successful = entry.get('successful', 0)
            rate = entry.get('success_rate', 0)
            report += f"| {date} | {total:,} | {successful:,} | {rate:.2f}% |\n"

        report += "\n---\n\n"

    # Recommendations
    report += "## Recommendations\n\n"

    if metrics['failed'] > 0:
        report += "### To Improve Success Rate:\n\n"

        if metrics['failure_patterns'].get('Contains location qualifiers (near/at)', 0) > 0:
            report += "1. **Location qualifiers**: Consider pre-processing addresses to remove 'near' and 'at' phrases\n"

        if metrics['failure_patterns'].get('Intersection format', 0) > 0:
            report += "2. **Intersections**: Review intersection parsing logic and try alternative formats\n"

        if metrics['failure_patterns'].get('Contains extra sentences/context', 0) > 0:
            report += "3. **Extra context**: Improve cleaning logic to remove sentences after the address\n"

        if metrics['failure_patterns'].get('Incomplete/vague address', 0) > 0:
            report += "4. **Incomplete addresses**: Review extraction patterns to capture more complete addresses\n"

        report += "\n"
    else:
        report += "🎉 **Perfect success rate!** All addresses are geocoded successfully.\n\n"

    report += "---\n\n"
    report += "*This report is automatically generated by `scripts/track_geocoding_success.py`*\n"

    return report


def main():
    """Main function to track geocoding success."""
    print("=" * 70)
    print("Geocoding Success Tracker")
    print("=" * 70)

    # Load current data
    print("\n1. Loading geocoded addresses...")
    addresses = load_geocoded_addresses()
    print(f"   Found {len(addresses)} total addresses")

    # Load metrics history
    print("\n2. Loading metrics history...")
    history = load_metrics_history()
    print(f"   Found {len(history)} historical entries")

    # Analyze current state
    print("\n3. Analyzing current geocoding status...")
    current_metrics = analyze_addresses(addresses)

    # Calculate improvements
    previous_metrics = history[-1] if history else None
    improvements = calculate_improvements(current_metrics, previous_metrics)

    # Add to history
    history.append(current_metrics)

    # Save updated history
    print("\n4. Saving metrics...")
    save_metrics_history(history)

    # Generate report
    print("\n5. Generating report...")
    report = generate_report(current_metrics, improvements, history)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"   ✓ Saved report to {REPORT_FILE}")

    # Print summary to console
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Addresses:     {current_metrics['total_addresses']:,}")
    print(f"Successfully Geocoded: {current_metrics['successful']:,}")
    print(f"Failed:              {current_metrics['failed']:,}")
    print(f"Success Rate:        {current_metrics['success_rate']:.2f}%")

    if improvements['new_addresses'] > 0:
        print(f"\nNew this run:        +{improvements['new_addresses']} addresses")
        print(f"  Successes:         +{improvements['new_successes']}")
        print(f"  Failures:          +{improvements['new_failures']}")
        if 'success_rate_change' in improvements:
            print(f"  Rate change:       {improvements['success_rate_change']:+.2f}%")

    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
