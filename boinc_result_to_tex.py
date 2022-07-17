"""Converts the different BOINC result schemas to fancy LaTeX documents."""
import json
from sympy import symbols

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


def handle_general(result_data):
    # The two first lists are in the same format, e.g. [4, 6, 102, 50] -> 50 + 102n + 6n^2 + 4n^3.
    an_bn_equations = []
    for i in range(2):
        polynomial = 0
        for index, coefficient in enumerate(result_data[i][::-1]):
            polynomial += coefficient * (n**index)
        an_bn_equations.append(str(polynomial).replace("**", "^"))
    an_equation, bn_equation = an_bn_equations

    return an_equation, bn_equation, "", ""


def handle_zeta5(result_data):
    print(result_data)
    return "", "", "", ""


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
        an_equation, bn_equation, lhs_equation, rhs_equation = HANDLERS[result_type](
            result_data
        )
        with open("result.tex", "w") as result_file:
            result_file.write(
                get_conjecture(an_equation, bn_equation, lhs_equation, rhs_equation)
            )
    else:
        print(
            f"Unsupported result type '{result_type}'\nThe supported types are: {', '.join(HANDLERS.keys())}"
        )
        exit(-1)
