"""Converts the different BOINC result schemas to fancy TeX documents."""
import json
import os
from sympy import symbols, latex

TEMPLATES = {
    "conjecture": r"""\documentclass[preview,border=2pt]{standalone}
\usepackage{amsmath}
\usepackage{graphicx}
\begin{document}
\begin{equation*}
\resizebox{\textwidth}{!}
{%
    $ LHSEquation=\displaystyle\lim _{n\to\infty} RHSEquation $%
}
\end{equation*}
\end{document}""",
    "unknown-lhs": r"""\documentclass[preview,border=2pt]{standalone}
\usepackage{amsmath}
\usepackage{graphicx}
\begin{document}
\begin{equation*}
\resizebox{\textwidth}{!}
{%
    $ LHSEquation = RHSEquation $%
}
\end{equation*}
\end{document}""",
}

n = symbols("n")


def format_tex(
    template="conjecture",
    an_equation="",
    bn_equation="",
    lhs_equation="",
    rhs_equation="",
):
    return (
        TEMPLATES[template]
        .replace("AnEquation", an_equation)
        .replace("BnEquation", bn_equation)
        .replace("LHSEquation", lhs_equation)
        .replace("RHSEquation", rhs_equation)
    )


def generate_rhs(
    an_equation: str, bn_equation: str, steps=3, show_substitution=False
) -> str:
    def replace_n(equation: str, n):
        return (
            equation.replace("0n", rf"0\cdot {n}")
            .replace("1n", rf"1\cdot {n}")
            .replace("2n", rf"2\cdot {n}")
            .replace("3n", rf"3\cdot {n}")
            .replace("4n", rf"4\cdot {n}")
            .replace("5n", rf"5\cdot {n}")
            .replace("6n", rf"6\cdot {n}")
            .replace("7n", rf"7\cdot {n}")
            .replace("8n", rf"8\cdot {n}")
            .replace("9n", rf"9\cdot {n}")
            .replace("0 n", rf"0\cdot {n}")
            .replace("1 n", rf"1\cdot {n}")
            .replace("2 n", rf"2\cdot {n}")
            .replace("3 n", rf"3\cdot {n}")
            .replace("4 n", rf"4\cdot {n}")
            .replace("5 n", rf"5\cdot {n}")
            .replace("6 n", rf"6\cdot {n}")
            .replace("7 n", rf"7\cdot {n}")
            .replace("8 n", rf"8\cdot {n}")
            .replace("9 n", rf"9\cdot {n}")
            .replace("n", str(n))
        )

    def tex_to_expr(tex: str):
        return (
            tex.replace("0n", "0*n")
            .replace("1n", "1*n")
            .replace("2n", "2*n")
            .replace("3n", "3*n")
            .replace("4n", "4*n")
            .replace("5n", "5*n")
            .replace("6n", "6*n")
            .replace("8n", "8*n")
            .replace("9n", "9*n")
            .replace("0 n", "0*n")
            .replace("1 n", "1*n")
            .replace("2 n", "2*n")
            .replace("3 n", "3*n")
            .replace("4 n", "4*n")
            .replace("5 n", "5*n")
            .replace("6 n", "6*n")
            .replace("7 n", "7*n")
            .replace("8 n", "8*n")
            .replace("9 n", "9*n")
            .replace("0(", "0*(")
            .replace("1(", "1*(")
            .replace("2(", "2*(")
            .replace("3(", "3*(")
            .replace("4(", "4*(")
            .replace("5(", "5*(")
            .replace("6(", "6*(")
            .replace("7(", "7*(")
            .replace("8(", "8*(")
            .replace("9(", "9*(")
            .replace("^", "**")
            .replace(r"\cdot", "*")
            .replace("{", "(")
            .replace("}", ")")
        )

    def an(n):
        if show_substitution:
            return replace_n(an_equation, n)
        return eval(tex_to_expr(an_equation))

    def bn(n):
        if show_substitution:
            return replace_n(bn_equation, n)
        return eval(tex_to_expr(bn_equation))

    rhs_equation = (
        r"\cdots"
        if show_substitution
        else (rf"\ddots + \cfrac{{{bn_equation}}}{{{an_equation}}}")
    )
    for i in range(steps, 0, -1):
        rhs_equation = rf"{an(i-1)}+\cfrac{{{bn(i)}}}{{{rhs_equation}}}"

    return rhs_equation


def coefficient_to_tex(coefficient: int, term: str, add_dot_and_parantheses=True):
    if coefficient == 0:
        return ""
    if coefficient == 1 and term != "":
        return term
    if coefficient == -1 and term != "":
        return "-" + term
    if add_dot_and_parantheses:
        return rf"{coefficient} \cdot ({term})"
    return f"{coefficient} {term}"


def plus_coefficient_to_tex(coefficient: int, term: str, add_dot_and_parantheses=True):
    return ("+" if coefficient > 0 else "") + coefficient_to_tex(
        coefficient, term, add_dot_and_parantheses
    )


def create_consts_sum_tex(coefficients: list[int], consts: list[str]) -> str:
    assert len(coefficients) == len(consts)
    result = coefficient_to_tex(
        coefficients[0], consts[0], add_dot_and_parantheses=False
    )
    for i in range(1, len(coefficients)):
        result += plus_coefficient_to_tex(
            coefficients[i], consts[i], add_dot_and_parantheses=False
        )
    return result


def fraction(numerator: str, denominator: str) -> str:
    numerator = numerator.removeprefix("+")
    denominator = denominator.removeprefix("+")
    return rf"\cfrac{{{numerator}}}{{{denominator}}}"


def handle_general(result_data):
    # The two first lists are in the same format so they should be treated the same
    an_bn_equations = []
    for i in range(2):
        polynomial = 0
        for index, coefficient in enumerate(result_data[i][::-1]):
            polynomial += coefficient * (n**index)
        an_bn_equations.append(latex(polynomial))
    an_equation, bn_equation = an_bn_equations

    consts = ["", r"\zeta (3)", r"\zeta (2)"]
    lhs_equation = str(round(float(result_data[2]), 10))
    if result_data[3] is not None and len(result_data[3]) == 3:
        lhs_numerator = create_consts_sum_tex(result_data[3], consts)
        lhs_denominator = create_consts_sum_tex(result_data[4], consts)
        lhs_equation = fraction(lhs_numerator, lhs_denominator)

    return (
        "conjecture" if lhs_equation != "" else "unknown-lhs",
        an_equation,
        bn_equation,
        lhs_equation,
    )


def handle_zeta5(result_data):
    an_equation = (
        coefficient_to_tex(result_data[0][0], "n^5 + (n + 1)^5")
        + plus_coefficient_to_tex(result_data[0][1], "n^3 + (n + 1)^3")
        + plus_coefficient_to_tex(result_data[0][2], "2n + 1")
    )
    bn_equation = coefficient_to_tex(
        -(result_data[1][0] ** 2), "n^{10}", add_dot_and_parantheses=False
    )

    consts = ["", r"\zeta (3)", r"\zeta (5)"]

    lhs_equation = str(round(float(result_data[2]), 10))
    if result_data[3] is not None and len(result_data[3]) == 3:
        lhs_numerator = create_consts_sum_tex(result_data[3], consts)
        lhs_denominator = create_consts_sum_tex(result_data[4], consts)
        lhs_equation = fraction(lhs_numerator, lhs_denominator)

    return (
        "conjecture" if lhs_equation != "" else "unknown-lhs",
        an_equation,
        bn_equation,
        lhs_equation,
    )


HANDLERS = {"general": handle_general, "zeta5": handle_zeta5}


def filename_to_schema(filename: str):
    return os.path.basename(filename).split("_")[1]


def generate_tex_from_str(result: str, schema: str):
    result_data = json.loads(result)[0]

    if schema in HANDLERS:
        template, an_equation, bn_equation, lhs_equation = HANDLERS[schema](result_data)
        an_equation = an_equation.removeprefix("+")
        bn_equation = bn_equation.removeprefix("+")
        rhs_equation = generate_rhs(an_equation, bn_equation)
        return (
            format_tex(template, an_equation, bn_equation, lhs_equation, rhs_equation),
            template,
        )
    else:
        print(
            f"Unsupported result type '{schema}'\nThe supported types are: {', '.join(HANDLERS.keys())}"
        )
        exit(-1)


def generate_tex(result_filename: str):
    with open(result_filename, "r") as result_file:
        result_data = result_file.read()
    generate_tex_from_str(result_data, filename_to_schema(result_filename))


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    with open("result.tex", "w") as result_file:
        result_file.write(generate_tex(args.file)[0])
