"""Converts the different BOINC result schemas to fancy TeX documents."""
import json
import os
from sympy import symbols, latex

conjecture_template = r"""\documentclass[preview,border=2pt]{standalone}
\usepackage{amsmath}
\begin{document}
\begin{center}
Using the series
\end{center}
\begin{equation*}
a_n=AnEquation
\end{equation*}
\begin{equation*}
b_n=BnEquation
\end{equation*}
\begin{center}
We got the conjecture:
\end{center}
\begin{equation*}
LHSEquation=RHSEquation
\end{equation*}
\end{document}"""

n = symbols("n")


def get_conjecture(
    an_equation: str, bn_equation: str, lhs_equation: str, rhs_equation: str
):
    return (
        conjecture_template.replace("AnEquation", an_equation)
        .replace("BnEquation", bn_equation)
        .replace("LHSEquation", lhs_equation)
        .replace("RHSEquation", rhs_equation)
    )


def generate_rhs(an_equation: str, bn_equation: str, steps=2) -> str:
    def replace_n(equation: str, n):
        return (
            equation.replace("0n", r"0\cdot n")
            .replace("1n", rf"1\cdot {n}")
            .replace("2n", rf"2\cdot {n}")
            .replace("3n", rf"3\cdot {n}")
            .replace("4n", rf"4\cdot {n}")
            .replace("5n", rf"5\cdot {n}")
            .replace("6n", rf"6\cdot {n}")
            .replace("7n", rf"7\cdot {n}")
            .replace("8n", rf"8\cdot {n}")
            .replace("9n", rf"9\cdot {n}")
            .replace("n", str(n))
        )

    def an(n):
        return replace_n(an_equation, n)

    def bn(n):
        return replace_n(bn_equation, n)

    rhs_equation = r"\cdots"
    for i in range(steps, 0, -1):
        rhs_equation = rf"\frac{{{bn(i-1)}}}{{{an(i)}+{rhs_equation}}}"

    return rhs_equation


def coefficient_to_tex(coefficient: int, term: str, add_dot=True):
    if coefficient == 0:
        return ""
    if coefficient == 1:
        return term
    dot_str = r"\cdot" if add_dot else ""
    return f"{coefficient} {dot_str} {term}"


def plus_coefficient_to_tex(coefficient: int, term: str, add_dot=True):
    return ("+" if coefficient > 0 else "") + coefficient_to_tex(
        coefficient, term, add_dot
    )


def create_consts_sum_tex(coefficients: list[int], consts: list[str]) -> str:
    assert len(coefficients) == len(consts)
    result = coefficient_to_tex(coefficients[0], consts[0], add_dot=False)
    for i in range(1, len(coefficients)):
        result += plus_coefficient_to_tex(coefficients[i], consts[i], add_dot=False)
    return result


def fraction(numerator: str, denominator: str) -> str:
    numerator.removeprefix("+")
    denominator.removeprefix("+")
    return rf"\frac{{{numerator}}}{{{denominator}}}"


def handle_general(result_data):
    assert len(result_data[3]) == 3
    assert len(result_data[4]) == 3

    # The two first lists are in the same format so they should be treated the same
    an_bn_equations = []
    for i in range(2):
        polynomial = 0
        for index, coefficient in enumerate(result_data[i][::-1]):
            polynomial += coefficient * (n**index)
        an_bn_equations.append(latex(polynomial))
    an_equation, bn_equation = an_bn_equations

    consts = ["", r"\zeta (3)", r"\zeta (2)"]
    lhs_numerator = create_consts_sum_tex(result_data[3], consts)
    lhs_denominator = create_consts_sum_tex(result_data[4], consts)
    lhs_equation = fraction(lhs_numerator, lhs_denominator)

    return an_equation, bn_equation, lhs_equation


def handle_zeta5(result_data):
    assert len(result_data[0]) == 3
    assert len(result_data[1]) == 1
    assert len(result_data[3]) == 3
    assert len(result_data[4]) == 3

    an_equation = (
        coefficient_to_tex(result_data[0][0], "(n^5 + (n + 1)^5)")
        + plus_coefficient_to_tex(result_data[0][1], "(n^3 + (n + 1)^3)")
        + plus_coefficient_to_tex(result_data[0][2], "(2n + 1)")
    )
    bn_equation = coefficient_to_tex(-(result_data[1][0] ** 2), "n^{10}")

    consts = ["", r"\zeta (3)", r"\zeta (5)"]
    lhs_numerator = create_consts_sum_tex(result_data[3], consts)
    lhs_denominator = create_consts_sum_tex(result_data[4], consts)
    lhs_equation = fraction(lhs_numerator, lhs_denominator)

    return (
        an_equation,
        bn_equation,
        lhs_equation,
    )


HANDLERS = {"general": handle_general, "zeta5": handle_zeta5}


def generate_tex(result_filename: str):
    result_data = None
    with open(result_filename, "r") as result_file:
        result_data = json.load(result_file)[0]

    result_type = os.path.basename(result_filename).split("_")[1]
    if result_type in HANDLERS:
        an_equation, bn_equation, lhs_equation = HANDLERS[result_type](result_data)
        an_equation = an_equation.removeprefix("+")
        bn_equation = bn_equation.removeprefix("+")
        rhs_equation = generate_rhs(an_equation, bn_equation)
        with open("result.tex", "w") as result_file:
            result_file.write(
                get_conjecture(an_equation, bn_equation, lhs_equation, rhs_equation)
            )
    else:
        print(
            f"Unsupported result type '{result_type}'\nThe supported types are: {', '.join(HANDLERS.keys())}"
        )
        exit(-1)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    generate_tex(args.file)
