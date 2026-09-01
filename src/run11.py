from pipe_sizing import PipeSizing

pipe_calc = PipeSizing()

results = pipe_calc.calculate_complete_piping(
    total_flow_lpm=4595.95,      # من الحسابات الهيدروليكية
    total_pipe_length_m=4992.61, # من تحليل CAD
    material='steel'
)

pipe_calc.print_results(results)