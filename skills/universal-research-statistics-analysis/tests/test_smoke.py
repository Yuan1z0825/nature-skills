from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'analyze_research_data.py'
EXAMPLE = ROOT / 'examples' / 'demo_independent_three_groups.csv'

def test_cli_smoke(tmp_path):
    outdir = tmp_path / 'out'
    result = subprocess.run([sys.executable, str(SCRIPT), '--input', str(EXAMPLE), '--outdir', str(outdir), '--group-col', 'Group'], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert (outdir / 'analysis_results.xlsx').exists()
    assert (outdir / 'three_line_tables.docx').exists()
    assert (outdir / 'methods_results.docx').exists()
