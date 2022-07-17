"""Converts the different BOINC result schemas to fancy LaTeX documents."""
import json
from sympy import symbols, latex

conjecture_template = r"""\documentclass[preview,border=2pt]{standalone}
\usepackage{amsmath}
\begin{document}
Using the series
\begin{equation*}
a_n=AnEquation
\end{equation*}
\begin{equation*}
b_n=BnEquation
\end{equation*}
We got the conjecture:
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


def handle_general(result_data):
    # The two first lists are in the same format, e.g. [4, 6, 102, 50] -> 50 + 102n + 6n^2 + 4n^3.
    an_bn_equations = []
    for i in range(2):
        polynomial = 0
        for index, coefficient in enumerate(result_data[i][::-1]):
            polynomial += coefficient * (n**index)
        an_bn_equations.append(latex(polynomial))
    an_equation, bn_equation = an_bn_equations

    return an_equation, bn_equation, ""


def coefficient_to_latex(coefficient: int, term: str):
    if coefficient == 0:
        return ""
    if coefficient == 1:
        return term
    return rf"{coefficient} \cdot {term}"


def plus_coefficient_to_latex(coefficient: int, term: str):
    return ("+" if coefficient > 0 else "") + coefficient_to_latex(coefficient, term)


def handle_zeta5(result_data):
    return (
        coefficient_to_latex(result_data[0][0], "(n^5 + (n + 1)^5)")
        + plus_coefficient_to_latex(result_data[0][1], "(n^3 + (n + 1)^3)")
        + plus_coefficient_to_latex(result_data[0][2], "(2n + 1)"),
        coefficient_to_latex(-(result_data[1][0] ** 2), "n^{10}"),
        "",
    )


HANDLERS = {"general": handle_general, "zeta5": handle_zeta5}

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    result_data = None
    with open(args.file, "r") as result_file:
        result_data = json.load(result_file)[0]

    result_type = args.file.split("_")[1]
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
