# from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy.stats as stats
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ENV_MAP = {
    "cartpole": "CartPoleBulletEnv-v1",
    "pendulum": "Pendulum-v1",
    "cheetah": "HalfCheetahBulletEnv-v0",
}


def early_exit(message):
    print(message)
    exit()


def plot_combined(name, results):
    results = np.array(results)
    xs = np.arange(results.shape[1])
    ys = np.mean(results, axis=0)
    yerrs = stats.sem(results, axis=0)
    plt.fill_between(xs, ys - yerrs, ys + yerrs, alpha=0.25)
    plt.plot(xs, ys, label=name)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        default="results",
        help="Directory containing TensorFlow event files",
    )
    parser.add_argument("--env-name", required=True, help="Name of environment")
    parser.add_argument(
        "--seeds", required=True, help="Comma-separated list of seeds to plot"
    )
    args = parser.parse_args()

    if args.env_name not in ENV_MAP:
        early_exit("--env-name should be one of cartpole, pendulum, or cheetah")
    gym_env_name = ENV_MAP[args.env_name]
    
    if args.seeds.isdigit():
        seeds = [int(args.seeds)]
    else:
        seeds = [int(seed) for seed in args.seeds.split(",")]

    directory = Path(args.directory)
    if not directory.is_dir():
        early_exit(f"{directory.resolve()} is not a directory")

    all_results = {"0": [], "50": [], "200" : []}
    for seed in seeds:
        format_str = f"{gym_env_name}-0.1-1000-{{}}-seed={seed}"
        all_results["0"].append(
            np.load(directory / format_str.format("0") / "scores.npy")
        )
        all_results["50"].append(
            np.load(directory / format_str.format("50") / "scores.npy")
        )
        all_results["200"].append(
            np.load(directory / format_str.format("200") / "scores.npy")
        )
    
    plt.figure()
    plt.title(args.env_name)
    plt.xlabel("Iteration")
    for name, results in all_results.items():
        plot_combined(name, results)
    plt.legend(loc='upper left')
    plt.savefig(directory / f"results-0.1-1000-initial-{args.env_name}.png", bbox_inches="tight")
