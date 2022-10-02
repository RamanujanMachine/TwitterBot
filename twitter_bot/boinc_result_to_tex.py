"""Converts the different BOINC result schemas to fancy TeX documents."""
import json
import os
import sympy
from sympy import symbols, latex, Poly
from typing import List

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
            .replace("0 (", "0*(")
            .replace("1 (", "1*(")
            .replace("2 (", "2*(")
            .replace("3 (", "3*(")
            .replace("4 (", "4*(")
            .replace("5 (", "5*(")
            .replace("6 (", "6*(")
            .replace("7 (", "7*(")
            .replace("8 (", "8*(")
            .replace("9 (", "9*(")
            .replace("^", "**")
            .replace(r"\cdot", "*")
            .replace("{", "(")
            .replace("}", ")")
            .replace(")(", ")*(")
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


def coefficient_to_tex(coefficient: int, term: str, add_dot=True, add_parantheses=True):
    if coefficient == 0:
        return ""
    if coefficient == 1 and term != "":
        return term
    if coefficient == -1 and term != "":
        return "-" + term
    if add_parantheses:
        term = f"({term})"
    if add_dot:
        return rf"{coefficient} \cdot {term}"
    return f"{coefficient} {term}"


def plus_coefficient_to_tex(
    coefficient: int, term: str, add_dot=True, add_parantheses=True
):
    return ("+" if coefficient > 0 else "") + coefficient_to_tex(
        coefficient, term, add_dot, add_parantheses
    )


def create_consts_sum_tex(coefficients: List[int], consts: List[str]) -> str:
    assert len(coefficients) == len(consts)
    result = coefficient_to_tex(
        coefficients[0], consts[0], add_dot=False, add_parantheses=False
    )
    for i in range(1, len(coefficients)):
        result += plus_coefficient_to_tex(
            coefficients[i], consts[i], add_dot=False, add_parantheses=False
        )
    return result


def removeprefix(s: str, prefix: str) -> str:
    if s.startswith(prefix):
        s = s[len(prefix) :]
    return s


def fraction(numerator: str, denominator: str) -> str:
    numerator = removeprefix(numerator, "+")
    denominator = removeprefix(denominator, "+")
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

def handle_zeta(result_data, order):
    an_equation = coefficient_to_tex(result_data[0][0], f"n^{order} + (n + 1)^{order}")
    for i, term_deg in enumerate(range(order-2, 1, -2)):
        an_equation += plus_coefficient_to_tex(result_data[0][i+1], f"n^{term_deg} + (n + 1)^{term_deg}")
    
    if order % 2 == 1:
        an_equation += plus_coefficient_to_tex(result_data[0][-1], "2n + 1") 
        consts = [""] + [f"\\zeta ({i})" for i in range(3, order+1, 2)]
    else:
        an_equation += plus_coefficient_to_tex(result_data[0][-1], "1") 
        consts = [""] + [f"\\zeta ({i})" for i in range(2, order+1, 2)]
    print(an_equation)
    bn_equation = coefficient_to_tex(
        -(result_data[1][0] ** 2), f"n^{order*2}", add_dot=False, add_parantheses=False
    )

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
        -(result_data[1][0] ** 2), "n^{10}", add_dot=False, add_parantheses=False
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

def _general_poly_to_sympy(coefs, n):
    terms = [c*(n**deg) for deg, c in enumerate(coefs[::-1])]
    return Poly(sum(terms), n)


def handle_10deg_2roots(result_data):
    # find b_n roots
    n = sympy.var('n')
    bn_expr = _general_poly_to_sympy(result_data[1][:3], n)
    c, d = -bn_expr.root(0), -bn_expr.root(1)

    # All results should match one of these templates
    an_options = {
        Poly( n**5 + ((n+1)**3) * (n + 1 + c) * (n + 1 + d)):
            "n^5 + (n+1)^3 (n + 1 + {c})(n + 1 + {d})",
        Poly( n**4*(n + c) + ((n+1)**4) * (n + 1 + d)):
            "n^4(n + {c}) + (n+1)^4(n + 1 + {d})",
        Poly( n**4*(n + d) + ((n+1)**4) * (n + 1 + c)):
            "n^4(n + {d}) + (n+1)^4(n + 1 + {c})",
        Poly( n**3*(n + c)*(n + d) + (n+1)**5):
            "n^3(n + {c})(n + {d}) + (n+1)^5"
            }
        
    bn_tex = f'-n^8(n+{c})(n+{d})'

    an_expr = _general_poly_to_sympy(result_data[0], n)
    for an_opt, tex_template in an_options.items():
        if an_expr - an_opt == 0:
            an_tex = tex_template.format(c = c, d = d)
            break
    # No template was matched
    else:
        polys_gcd = sympy.Poly.gcd(an_expr*an_expr.subs({n:n-1}), bn_expr)
        if polys_gcd != 1:
            # Is an inflation
            an_tex = f'({latex(polys_gcd.expr)})({latex((an_expr/polys_gcd).simplify())})'
            
        else:
            # use the generic template
            an_tex = coefficient_to_tex(result_data[0][0]//2, "n^5 + (n + 1)^5")
            c, d = min(c, d), max(c, d)
            an_tex += plus_coefficient_to_tex(d, "(n+1)^4", add_parantheses=False)
            reduced_an_expr = an_expr - Poly((n**5 + (n+1)**5) + d * (n+1)**4)
            an_tex += '+' + latex(reduced_an_expr.expr)

    # lhs
    consts = [""] + [f"\\zeta ({i})" for i in range(5, 1, -1)]
    lhs_equation = str(round(float(result_data[2]), 10))
    if result_data[3] is not None and len(result_data[3]) == 3:
        lhs_numerator = create_consts_sum_tex(result_data[3], consts)
        lhs_denominator = create_consts_sum_tex(result_data[4], consts)
        lhs_equation = fraction(lhs_numerator, lhs_denominator)

    return (
        "conjecture" if lhs_equation != "" else "unknown-lhs",
        an_tex,
        bn_tex,
        lhs_equation,
    )


def handle_ofir_single_half_root(result_data):
    # Here we've gave bn a single half root. So `bn=-n^9(n+1/2)`. 
    # To use integer coefficients, we used `bn=-n^9(2n+1)` and 
    # `bn=-2n^9(2n+1)` for the latter, an expression from Ofir's scheme
    # should apply with expansion of 2. Otherwise, we have no clue :)
    n = sympy.var('n')
    
    if result_data[1][0] == -4:
        bn_tex = '-2(2n+1) \\cdot n^9'
        bn_expr = Poly(-2*(2*n+1)*n**9)
    else:
        bn_tex = '-(2n+1) \\cdot n^9'
        bn_expr = Poly(-(2*n+1)*n**9)

    an_expr = _general_poly_to_sympy(result_data[0], n)
    an_tex = ''

    if result_data[1][0] == -4 and result_data[0][0] == 4:
        # expansion of 2, maybe Ofir's case

        an_options = {
            Poly( 2 * (n**5 + (n+1+1/2)*(n+1)**4) ):
                r"2 (n^5 + (n+1+1/2) \cdot (n+1)^4)",
            Poly( 2 * ((n+1/2)*n**4 + (n+1)**5) ):
                r"2 ((n+1/2) \cdot n^4 + (n+1)^5)"
            }
            
        for an_opt, tex_template in an_options.items():
            if an_expr - an_opt == 0:
                an_tex = tex_template
                break
        
    # No template was matched
    if an_tex == '':
        # maybe expansion
        polys_gcd = sympy.Poly.gcd(an_expr*an_expr.subs({n:n-1}), bn_expr)
        if polys_gcd != 1:
            an_tex = f'({latex(polys_gcd.expr)})({latex((an_expr/polys_gcd).simplify())})'
            
        else:
            # use the generic template
            an_tex = coefficient_to_tex(result_data[0][0]//2, "n^5 + (n + 1)^5")
            reduced_an_expr = an_expr - (result_data[0][0]//2) * Poly((n**5 + (n+1)**5))
            an_tex += '+' + latex(reduced_an_expr.expr)

    

    # lhs
    consts = [""] + [f"\\zeta ({i})" for i in range(5, 1, -1)]
    lhs_equation = str(round(float(result_data[2]), 10))
    if result_data[3] is not None and len(result_data[3]) == 3:
        lhs_numerator = create_consts_sum_tex(result_data[3], consts)
        lhs_denominator = create_consts_sum_tex(result_data[4], consts)
        lhs_equation = fraction(lhs_numerator, lhs_denominator)

    return (
        "conjecture" if lhs_equation != "" else "unknown-lhs",
        an_tex,
        bn_tex,
        lhs_equation,
    )



HANDLERS = {
    "general": handle_general, 
    "zeta7": lambda x: handle_zeta(x, 7),
    "zeta5": lambda x: handle_zeta(x, 5),
    "zeta3": lambda x: handle_zeta(x, 3),
    "zeta2": lambda x: handle_zeta(x, 2),
    "DEG2": handle_10deg_2roots,
    "SingleHalfRoota": handle_ofir_single_half_root
    }


def filename_to_schema(filename: str):
    return os.path.basename(filename).split("_")[1]


def generate_tex_from_str(result: str, schema: str):
    result_data = json.loads(result)[0]

    if schema in HANDLERS:
        template, an_equation, bn_equation, lhs_equation = HANDLERS[schema](result_data)
        an_equation = removeprefix(an_equation, "+")
        bn_equation = removeprefix(bn_equation, "+")
        rhs_equation = generate_rhs(an_equation, bn_equation)
        return (
            format_tex(template, an_equation, bn_equation, lhs_equation, rhs_equation),
            template,
        )
    else:
        err_msg = f"Unsupported result type '{schema}'\nThe supported types are: {', '.join(HANDLERS.keys())}"
        print(err_msg)
        raise Exception(err_msg)


def generate_tex(result_filename: str):
    with open(result_filename, "r") as result_file:
        result_data = result_file.read()
    return generate_tex_from_str(result_data, filename_to_schema(result_filename))


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    with open("result.tex", "w") as result_file:
        result_file.write(generate_tex(args.file)[0])
