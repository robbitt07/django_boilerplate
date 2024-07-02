
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Any, Dict


def call_func_with_kwargs_as_arg(func: callable, func_kwargs: Dict, *args) -> Any:
    """Wrapper Function to Handle Kwarg Dictionary in the Second Argument Spot
    
    The async `tun_in_executor` method does not allow for kwargs to be passed to 
    the function being run, only args.  This wrapper enables passing kwargs by 
    treating the kwargs as a dictionary in the second argument spot.

    Parameters
    ----------
    func : callable
        Function to be evaluated
    func_kwargs : Dict
        Kwargs to be passed to the function

    Returns
    -------
    Any
        Result of the passed function
    """
    return func(*args, **func_kwargs)


async def run_async_function(func_ls: List[callable],
                             func_args_ls: List[List[Any]],
                             max_workers: int) -> List[Any]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor, call_func_with_kwargs_as_arg, func, *func_args
            ) for func, func_args in zip(func_ls, func_args_ls)
        ]
        response_ls = []
        for response in await asyncio.gather(*tasks):
            response_ls += [response]
        return response_ls


def run_concurrent_functions(func_ls: List[callable],
                             func_args_ls: List[List[Any]] = None,
                             func_kwargs_ls: List[Dict] = None,
                             max_workers: int = 10) -> List[Any]:
    """Run Functions Concurrently

    Parameters
    ----------
    func_ls : List[callable]
        List of functions to be run concurrently
    func_args_ls : List[List[Any]]
        List of args to be passed to the functions, by default None
    func_kwargs_ls : List[Dict]
        List of kwargs to be passed to the functions, by default None
    max_workers : int, optional
        Number of functions to be run concurrently, by default 10

    Returns
    -------
    List[Any]
        List of responses of the function in the order the functions were passed
    
    Example
    -------
    You need to add event loop handling where this function is used when using on web server.
    To use inside of a Django view, you can do the following:

    def function_used_inside_view():
        func_ls = [
            call_api_1,
            call_api_2,
            call_api_3,
        ]
        func_args_ls = [
            [1, True],
            ['param_value', 4],
            [],
        ]
        func_kwargs_ls = [
            {'a': 1, 'b': 2},
            {'c': 4, 'd': 3},
            {'a': 1, 'd': 7},
        ]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result_ls = run_concurrent_functions(
            func_ls=func_ls, 
            func_args_ls=func_args_ls,
            func_kwargs_ls=func_kwargs_ls,
        )
        loop.close()
        return result_ls
    
    """
    if func_args_ls is None:
        func_args_ls = [[] for _ in func_ls]

    if func_kwargs_ls is None:
        func_kwargs_ls = [{} for _ in func_ls]

    for func_args, func_kwargs in zip(func_args_ls, func_kwargs_ls):
        func_args.insert(0, func_kwargs)

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run_async_function(
        func_ls=func_ls, func_args_ls=func_args_ls, max_workers=max_workers,
    ))
    return loop.run_until_complete(future)
