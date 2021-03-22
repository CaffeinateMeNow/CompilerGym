# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""Regression tests for LlvmEnv.validate()."""
import pytest

from compiler_gym import CompilerEnvState
from compiler_gym.envs import LlvmEnv
from tests.pytest_plugins.common import skip_on_ci
from tests.test_main import main

pytest_plugins = ["tests.pytest_plugins.llvm"]


# The maximum number of times to call validate() on a state to check for an
# error.
VALIDATION_FLAKINESS = 10

# A list of CSV states that should pass validation, to be used as regression
# tests.
REGRESSION_TEST_STATES = [
    CompilerEnvState.from_csv(s)
    for s in """
benchmark://cBench-v1/rijndael,,,opt -gvn -loop-unroll -instcombine -gvn -loop-unroll -instcombine input.bc -o output.bc
benchmark://cBench-v1/rijndael,,,opt -gvn -loop-unroll -mem2reg -loop-rotate -gvn -loop-unroll -mem2reg -loop-rotate input.bc -o output.bc
benchmark://cBench-v1/rijndael,,,opt -gvn-hoist input.bc -o output.bc
benchmark://cBench-v1/rijndael,,,opt -jump-threading -sink -partial-inliner -mem2reg -inline -jump-threading -sink -partial-inliner -mem2reg -inline input.bc -o output.bc
benchmark://cBench-v1/rijndael,,,opt -mem2reg -indvars -loop-unroll -simplifycfg -mem2reg -indvars -loop-unroll -simplifycfg input.bc -o output.bc
benchmark://cBench-v1/rijndael,,,opt -mem2reg -instcombine -early-cse-memssa -loop-unroll input.bc -o output.bc
benchmark://cBench-v1/rijndael,,,opt -reg2mem -licm -reg2mem -licm -reg2mem -licm input.bc -o output.bc
benchmark://cBench-v1/rijndael,,,opt -sroa -simplifycfg -partial-inliner input.bc -o output.bc
""".strip().split(
        "\n"
    )
]
REGRESSION_TEST_STATE_NAMES = [
    f"{s.benchmark},{s.commandline}" for s in REGRESSION_TEST_STATES
]

# A list of CSV states that are known to fail validation.
KNOWN_BAD_STATES = [
    CompilerEnvState.from_csv(s)
    for s in """
""".strip().split(
        "\n"
    )
    if s
]
KNOWN_BAD_STATE_NAMES = [f"{s.benchmark},{s.commandline}" for s in KNOWN_BAD_STATES]
#
# NOTE(github.com/facebookresearch/CompilerGym/issues/103): The following
# regresison tests are deprecated after -structurizecfg was deactivated:
#
# benchmark://cBench-v1/tiff2bw,,,opt -structurizecfg input.bc -o output.bc
# benchmark://cBench-v1/tiff2rgba,,,opt -structurizecfg input.bc -o output.bc
# benchmark://cBench-v1/tiffdither,,,opt -structurizecfg input.bc -o output.bc
# benchmark://cBench-v1/tiffmedian,,,opt -structurizecfg input.bc -o output.bc


@pytest.mark.parametrize("state", KNOWN_BAD_STATES, ids=KNOWN_BAD_STATE_NAMES)
@pytest.mark.xfail(strict=True, reason="Known-bad test")
def test_validate_known_bad_trajectory(env: LlvmEnv, state):
    env.apply(state)
    for _ in range(VALIDATION_FLAKINESS):
        result = env.validate()
        if not result.okay():
            pytest.fail(f"Validation failed: {result}\n{result.json()}")


@skip_on_ci
@pytest.mark.parametrize(
    "state", REGRESSION_TEST_STATES, ids=REGRESSION_TEST_STATE_NAMES
)
def test_validate_known_good_trajectory(env: LlvmEnv, state):
    for _ in range(VALIDATION_FLAKINESS):
        result = env.validate()
        if not result.okay():
            pytest.fail(f"Validation failed: {result}\n{result.json()}")


@skip_on_ci
@pytest.mark.xfail(
    strict=True, reason="github.com/facebookresearch/CompilerGym/issues/105"
)
def test_validate_susan_b(env: LlvmEnv):
    env.reset("cBench-v1/susan")
    env.step(env.action_space["-mem2reg"])
    env.step(env.action_space["-simplifycfg"])
    env.step(env.action_space["-lcssa"])
    env.step(env.action_space["-break-crit-edges"])
    env.step(env.action_space["-newgvn"])
    env.step(env.action_space["-mem2reg"])
    env.step(env.action_space["-simplifycfg"])
    env.step(env.action_space["-lcssa"])
    env.step(env.action_space["-break-crit-edges"])
    env.step(env.action_space["-newgvn"])
    assert env.validate().okay()


if __name__ == "__main__":
    main()