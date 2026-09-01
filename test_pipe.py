import sys
sys.path.insert(0, '.')

from pipe_sizing import PipeSizing

calc = PipeSizing()

results = calc.calculate_complete_piping(
    total_pipe_length_m=4992.61,
    sprinkler_count=1086,
    sprinkler_type='pendant',
    material='steel'
)

calc.print_results(results)