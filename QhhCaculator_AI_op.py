from itertools import product
from multiprocessing import Pool, cpu_count
import functools

qhhans = [22, 484]
symbols = ['+', '-', '*', '/']
precision = 10

def eval_expr(expr):
    try:
        return expr, abs(eval(expr)), True
    except ZeroDivisionError:
        return expr, 0, False

def generate_and_evaluate_expressions(args):
    numbers, operators, target_results = args
    valid_exprs = []
    for op_combo in product(operators, repeat=len(numbers)-1):
        expr = ''.join(f"{n}{op}" for n, op in zip(numbers[:-1], op_combo)) + numbers[-1]
        expr_str, result, valid = eval_expr(expr)
        if valid and result in target_results:
            valid_exprs.append(f"{expr_str} = {result}")
    return valid_exprs

def split_number(number):
    def dfs(start, current_split):
        if start == len(number):
            result.append(tuple(current_split))
            return
        
        for end in range(start + 1, len(number) + 1):
            current_part = number[start:end]
            if current_part.startswith('0') and len(current_part) > 1:
                continue

            current_split.append(current_part)
            dfs(end, current_split)
            current_split.pop()

    result = []
    dfs(0, [])
    return result

def handle_result(result):
    with open("qhhnum.txt", "a") as f:
        for expr in result:
            f.write(f"{expr}\n")

def main(number):
    num_splits = split_number(str(number))
    with Pool(processes=cpu_count()) as pool:
        for ns in num_splits:
            args = (list(map(str, ns)), symbols, qhhans)
            pool.apply_async(generate_and_evaluate_expressions, args=(args,), callback=handle_result)
        pool.close()
        pool.join()

if __name__ == "__main__":
    main(1145141919810)
