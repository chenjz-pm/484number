import concurrent.futures
import multiprocessing
from itertools import product

qhhans = [22, 484]
symbols = ['+', '-', '*', '/']
precision = 10
cpucount = 5
batch_size = 50  # 每批次处理的数据量
writer_count = 2  # 写入进程数

def eval_expr(expr):
    try:
        return expr, abs(eval(expr)), True
    except ZeroDivisionError:
        return expr, 0, False

def generate_and_evaluate_expressions(numbers, operators, target_results):
    valid_exprs = []
    for op_combo in product(operators, repeat=len(numbers)-1):
        expr = ''.join(f"{n}{op}" for n, op in zip(numbers[:-1], op_combo)) + str(numbers[-1])
        expr_str, result, valid = eval_expr(expr)
        if valid and result in target_results:
            valid_exprs.append(f"{expr_str} = {round(result, precision)}")
    return valid_exprs

def split_number(number):
    result = []
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
    dfs(0, [])
    return result

def writer_process(queue):
    """单个写入进程"""
    with open(f"qhhnum_{multiprocessing.current_process().name}.txt", "a") as f:
        while True:
            batch = queue.get()
            if batch == "STOP":
                break
            for expr in batch:
                f.write(f"{expr}\n")

def main(number):
    num_splits = split_number(str(number))
    queue = multiprocessing.Queue(batch_size)  # 设置队列大小以避免过度内存使用

    # 创建多个写入进程
    writer_pool = multiprocessing.Pool(writer_count, writer_process, (queue,))

    with concurrent.futures.ProcessPoolExecutor(max_workers=cpucount) as executor:
        futures = []
        for ns in num_splits:
            future = executor.submit(generate_and_evaluate_expressions, list(map(str, ns)), symbols, qhhans)
            futures.append(future)

        batch = []
        for future in concurrent.futures.as_completed(futures):
            valid_exprs = future.result()
            if valid_exprs:
                batch.extend(valid_exprs)
                if len(batch) >= batch_size:
                    queue.put(batch.copy())
                    batch.clear()

        if batch:  # 确保最后的数据也被写入
            queue.put(batch)

    # 发送停止信号给写入进程
    for _ in range(writer_count):
        queue.put("STOP")
    
    writer_pool.close()
    writer_pool.join()

if __name__ == "__main__":
    from time import time_ns
    time_start=time_ns()
    main(11451419198)
    print("{:.3f} ms".format((time_ns()-time_start)/10**6))
