"""Retry decorator using tenacity for handling transient failures."""

from functools import wraps
from typing import Any, Callable, Optional, Type, Union

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    RetryError
)

from .logger import logger


def retry_on_failure(
    max_attempts: int = 3,
    min_wait: int = 4,
    max_wait: int = 10,
    exceptions: Union[Type[Exception], tuple] = Exception,
    reraise: bool = True
) -> Callable:
    """Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds
        exceptions: Exception types to retry on
        reraise: Whether to reraise the exception after all retries
        
    Returns:
        Decorated function with retry logic
        
    Example:
        @retry_on_failure(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
        def fetch_data():
            # ... code that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            reraise=reraise
        )
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"Function {func.__name__} failed, will retry. Error: {str(e)}"
                )
                raise
        
        return wrapper
    
    return decorator


def retry_with_logging(
    operation_name: str,
    max_attempts: int = 3,
    exceptions: Union[Type[Exception], tuple] = Exception
) -> Callable:
    """Decorator for retrying with detailed logging.
    
    Args:
        operation_name: Name of the operation for logging
        max_attempts: Maximum number of retry attempts
        exceptions: Exception types to retry on
        
    Returns:
        Decorated function with retry and logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            last_exception: Optional[Exception] = None
            
            while attempt < max_attempts:
                attempt += 1
                try:
                    logger.info(f"{operation_name} - Attempt {attempt}/{max_attempts}")
                    result = func(*args, **kwargs)
                    logger.info(f"{operation_name} - Succeeded on attempt {attempt}")
                    return result
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"{operation_name} - Failed on attempt {attempt}/{max_attempts}: {str(e)}"
                    )
                    
                    if attempt < max_attempts:
                        wait_time = min(4 * (2 ** (attempt - 1)), 10)
                        logger.info(f"{operation_name} - Waiting {wait_time}s before retry")
                        import time
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"{operation_name} - All {max_attempts} attempts failed"
                        )
            
            if last_exception:
                raise last_exception
            
            raise RuntimeError(f"{operation_name} failed after {max_attempts} attempts")
        
        return wrapper
    
    return decorator


