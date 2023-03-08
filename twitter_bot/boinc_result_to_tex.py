import sympy
import json
import os
from itertools import product


TEX_TEMPLATE = r"""
\documentclass[preview,border=2pt]{standalone}
\usepackage{amsmath}
\usepackage{graphicx}
\begin{document}
\begin{equation*}
\resizebox{\textwidth}{!}
{%
    $ LHSEquation=\displaystyle\lim _{n\to\infty} RHSEquation $%
}
\end{equation*}
\end{document}"""

MAX_COEFF = 10
n = sympy.var('n')
c0, c1, c2, c3, c4, c5, c6, c7, c8, c9 = sympy.var('c0:10')
sympy_coefs = sympy.var('c0:10')

"""
To detect the "best" representation we will create a sympy poly out of the result.
We will compare it to different templates. For every template of an and bn, we will 
substitute the coeffs with small integers (up to MAX_COEFF)

The templates are sorted from the most simple to the most general. There might be many
cases where a result can be written using a simple, or more general scheme. We'll prefer
the simple scheme, that is located early in JOB_NAME_TO_RESULT_SCHEMES

For now, there is no way to create "interactions" between an and bn. So each should have a template
that might match it.

Notice:
1. The first thing done is calculating the polynomial GCD between an and bn - to detect expansions. 
2. If no template is matched, we will display the canonical representation for the polynomial. 

"""

# How you want the result to be displayed
JOB_NAME_TO_RESULT_SCHEMES = {
    'AllRootsButOne': {
        # In this scheme we've set 9 out of 10 roots to have the same value
        'an': [
            c0 * (n+c1)**5 + c2 * (n+1+c3)**4 * (n+1),
            c0 * (n+c1)**4 * n + c2 * (n+1+c3)**5,
        ],
        'bn': [
            -n * (n+c0)**9
        ]
    },
    # This scheme is chosen here more as an example; There aren't that many templates which are relevant for a single batch
    'SingleHalfRoota': {
        'an': [
            # ZZZ scheme - 1 root, integer
            c0 * n**5 + c1 * (n+1+c3) * (n+1)**4,
            c0 * (n+c1) * n**4 + c2 * (n+1)**5,
            
            # ZZZ scheme - 1 root, rational
            c0 * n**5 + c1 * (n+1+c2/c3) * (n+1)**4,
            c0 * (n+c1/c2) * n**4 + c3 * (n+1)**5
        ],
        'bn': [
            # ZZZ scheme - 1 root, integer
            sympy.Mul(-1 , (n+c0) * n**9),

            # ZZZ scheme - 1 root, rational
            sympy.Mul(-1 , (c0*n+c1) * n**9),
        ], 
        #'constants': [    
        # You can override the constants in the job's json by stating them here.
        #]
    }, 
    'DEG2': {
        'an': [
            # ZZZ scheme - 2 roots, integers
            c0 * n**5 + c1 * (n+1+c2) * (n+1+c3) * (n+1)**3,
            c0 * (n+c1) * n**4 + c2 * (n+1+c3) * (n+1)**4,
            c0 * (n+c1) * (n+c2) * n**3 + c3 * (n+1)**5,
        ],
        'bn': [
            # ZZZ scheme - 2 roots, integers
            sympy.Mul(-1 , (n+c0) * (n+c1) * n**8),
        ]
    },
    'general':{
        'an': [
            c0 * n**3 + c1 * (n+1)**3 + c2 *(2*n+1),
            c0 * n**3 + c1 * (n+1)**3
        ],
        'bn': [
            -c0 * n**6
        ]
    }
}

JOB_NAME_TO_RESULT_SCHEMES['zeta5'] = JOB_NAME_TO_RESULT_SCHEMES['DEG2']
JOB_NAME_TO_RESULT_SCHEMES['PL5'] = JOB_NAME_TO_RESULT_SCHEMES['DEG2']


# How the job was created - to build a sympy expression for it  (before detection)
JOB_NAME_TO_INPUT_SCHEMES = {
    'zeta5': {
        'an': c0 * (n**5 + (n+1)**5) + c1 * (n**3 + (n+1)**3) + c2 * (2*n+1),
        'bn': - (c0**2) * n**10
    }
}


def _general_poly_to_sympy(coefs):
    terms = [c*(n**deg) for deg, c in enumerate(coefs[::-1])]
    return sum(terms)


def get_sympy_exprs(result_data, scheme_name):
    if scheme_name in JOB_NAME_TO_INPUT_SCHEMES.keys():
        an = JOB_NAME_TO_INPUT_SCHEMES[scheme_name]['an'].subs(
            zip(sympy_coefs[:len(result_data[0])], result_data[0]))
        bn = JOB_NAME_TO_INPUT_SCHEMES[scheme_name]['bn'].subs(
            zip(sympy_coefs[:len(result_data[1])], result_data[1]))
        return an, bn

    an = _general_poly_to_sympy(result_data[0])
    bn = _general_poly_to_sympy(result_data[1])

    return an, bn


def match_expression(poly_expr, options):
    """
    This functions finds the best way to write poly_expr.

    We will go through all of the options given by order. 
    For every option, we will substitute different numbers as coefficients and compare it to 
    poly_expr. 
    """
    for option in options:
        free_vars = list(option.free_symbols)
        free_vars.remove(n)
        # Try different numbers and see what works ¯\_(ツ)_/¯
        for subs in product(*[range(1, MAX_COEFF) for _ in free_vars]):
            suggested_expr = option.subs(zip(free_vars, subs))
            if sympy.Poly(suggested_expr - poly_expr, n) == 0:
                print(f'Match for {poly_expr}:')
                print(suggested_expr)
                return suggested_expr

    # No match 
    print('no match for ')
    print(poly_expr)
    return poly_expr 


def match_result(result_data, scheme):
    """
    This function tries to detect the best way to write the entire result
    It will reduce the GCD of an and bn, and then look for the best expression for each.
    Returns the sympy expressions, and the latex expression for them
    """
    an_expr, bn_expr = get_sympy_exprs(result_data, scheme)
    gcd = sympy.gcd(an_expr, bn_expr)

    if scheme not in JOB_NAME_TO_RESULT_SCHEMES:
        print(f'The scheme {scheme} has no polynomials templates. Using canonical representation.')
        return an_expr, sympy.latex(an_expr), bn_expr, sympy.latex(bn_expr)

    # If the expansion is only by a number (not by a function of n) then the templates 
    # for the same scheme will still work. If not, then we should use another scheme to define
    # the result. 
    if gcd == 1:
        an_matched = match_expression(an_expr, JOB_NAME_TO_RESULT_SCHEMES[scheme]['an'])
        bn_matched = match_expression(bn_expr, JOB_NAME_TO_RESULT_SCHEMES[scheme]['bn'])

        return an_matched, sympy.latex(an_matched), bn_matched, sympy.latex(bn_matched)

    elif gcd.is_constant():
        an_matched = match_expression(an_expr/gcd, JOB_NAME_TO_RESULT_SCHEMES[scheme]['an'])
        bn_matched = match_expression(bn_expr/gcd, JOB_NAME_TO_RESULT_SCHEMES[scheme]['bn'])

        return gcd * an_matched, f'({gcd}) \\cdot ({sympy.latex(an_matched)})', \
            gcd * bn_matched, f'({gcd}) \\cdot ({sympy.latex(bn_matched)})'

    # expansion :(
    return an_expr, f'({gcd}) \\cdot ({sympy.latex((an_expr/gcd).simplify())})', \
        bn_expr, f'({gcd}) \\cdot ({sympy.latex((bn_expr/gcd).simplify())})'


def create_rhs_tex(an_expr, an_tex, bn_expr, bn_tex):
    an = lambda i: int(an_expr.subs(n, i))
    bn = lambda i: int(bn_expr.subs(n, i))

    return f"""
    {an(0)} + \\cfrac{{ {bn(1)} }}
        {{ {an(1)} + \\cfrac{{ {bn(2)} }}
            {{ \\ddots + \\cfrac{{ {bn_tex} }}
                {{ {an_tex} }} }} }}
    """


def create_lhs_tex(result, scheme):
    """
    TODO - use optional 'constants' key under JOB_NAME_TO_RESULT_SCHEMES to re-run PSLQ on the server
    with more accurate constants. For now, only decimal approximation
    """
    return f'{result[2][:10]}...'


def filename_to_scheme(filename):
    return os.path.basename(filename).split("_")[1]


def generate_tex_from_str(result, scheme):
    result_data = json.loads(result)[0]

    if scheme in HANDLERS:
        template, an_equation, bn_equation, lhs_equation = HANDLERS[scheme](result_data)
        an_equation = removeprefix(an_equation, "+")
        bn_equation = removeprefix(bn_equation, "+")
        rhs_equation = generate_rhs(an_equation, bn_equation)
        return (
            format_tex(template, an_equation, bn_equation, lhs_equation, rhs_equation),
            template,
        )
    else:
        err_msg = f"Unsupported result type '{scheme}'\nThe supported types are: {', '.join(HANDLERS.keys())}"
        print(err_msg)
        raise Exception(err_msg)

def generate_tex_from_data(result_filename, result_data):
    scheme = filename_to_scheme(result_filename)

    an_expr, an_tex, bn_expr, bn_tex = match_result(result_data, scheme)
    rhs_tex = create_rhs_tex(an_expr, an_tex, bn_expr, bn_tex)
    lhs_tex = create_lhs_tex(result_data, scheme)

    tex = TEX_TEMPLATE.replace('RHSEquation', rhs_tex)
    tex = tex.replace('LHSEquation', lhs_tex)
    print(tex)
    return [tex,]

def generate_tex(result_filename):
    with open(result_filename, "r") as result_file:
        result_data = json.load(result_file)[0]
    
    return generate_tex_from_data(result_filename, result_data)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    with open("result.tex", "w") as result_file:
        result_file.write(generate_tex(args.file))