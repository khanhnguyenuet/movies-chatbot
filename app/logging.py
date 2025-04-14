#!/usr/bin/env python3

"""
Utility funtions which are used in logging.
"""
import logging
import time
from functools import wraps
import os


def init_logger(name):
    """
    Initialize logger
    Args:
        module_name (str): name of module. Default: common
        name (str): file name
    """
    logger = logging.getLogger(f"{name}")
    logger.setLevel(logging.DEBUG)

    # Create handlers
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    c_handler.setFormatter(c_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    return logger


def error_logger(logger):
    """
    Decorator for error logging.
    Args:
        logger (Optional[Logger]): logger of the specific file.
            Default is None.
    Returns:
        Decorator function.
    """
    def decorator(func):
        """
        Decorator function to wrap a function within try - except.
        Return a wrapper.
        Args:
            func (Callable): function to be called.
        Raises:
            RuntimeError: raise error and reason if error occurs
        Returns:
            Callable: wrapped function with error logging.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrap a function with try-except block and log the error. 
            Raises:
                RuntimeError: raise error and reason if error occurs.
            Returns:
                Any: output of called function. 
            """
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as error:
                logger.error(f"{func.__name__}: {error}")
                raise RuntimeError(f"{func.__name__}") from error
        return wrapper
    return decorator


def time_logger(logger=None):
    """
    Decorator function that logs the running time of a function when called.
    Args:
        logger (Optional[Logger]): The logger object to use for logging.
            If None, uses a default logger. Default is None.
    Returns:
        Decorator function.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(func):
        """
        Decorator function to wrap a function with a timer.
        Return a wrapper.
        Args:
            func (Callable): function to be called.
        Returns:
            Callable: wrapped function with a timer.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrap a function with a timer. 
            Returns:
                Any: output of called function. 
            """
            class_name = ""
            if args and hasattr(args[0], '__class__'):
                class_name = args[0].__class__.__name__ + "."
            
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(f"[{class_name}{func.__name__}] executed in {elapsed_time:.4f} seconds")
            return result
        return wrapper
    return decorator