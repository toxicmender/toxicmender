from analytics.pipeline import collect, analyze, visualize

def main():
    data = collect.run()
    metrics = analyze.run(data)
    visualize.run(metrics)

if __name__ == "__main__":
    main()
# The main function orchestrates the data collection, analysis, and visualization pipeline.
