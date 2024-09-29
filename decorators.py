import time
    
def time_execution(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Start time
        result = func(*args, **kwargs)  # Execute function
        end_time = time.time()  # End time
        execution_time = round(end_time - start_time, 3)  # Round to 3 decimal places
        return result, f"{execution_time} sec"  # Append " sec" to the time
    return wrapper