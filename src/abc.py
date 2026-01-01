from typing import List, Union, Dict, Any, Optional, SupportsFloat
import statistics

def smart_sum(values: List[Union[SupportsFloat, Dict[str, Any], Any]], 
              key: Optional[str] = None,
              ignore_none: bool = True,
              ignore_negative: bool = False,
              ignore_zero: bool = False,
              round_result: Optional[int] = None) -> Union[float, Dict[str, float]]:
    """
    Perform smart summations on various data types with flexible filtering options.
    
    Args:
        values: List of numbers, dictionaries, or mixed objects to sum
        key: If values are dictionaries, key to extract numeric values from
        ignore_none: Whether to ignore None values (default: True)
        ignore_negative: Whether to ignore negative numbers (default: False)
        ignore_zero: Whether to ignore zero values (default: False)
        round_result: Number of decimal places to round result to (optional)
    
    Returns:
        Sum as float, or dict with detailed statistics if multiple values processed
    
    Examples:
        # Basic numeric summation
        smart_sum([1, 2, 3, 4])  # Returns: 10.0
        
        # Sum with filtering
        smart_sum([1, -2, 3, 0], ignore_negative=True, ignore_zero=True)  # Returns: 4.0
        
        # Sum dictionary values
        smart_sum([{'amount': 10}, {'amount': 20}], key='amount')  # Returns: 30.0
        
        # Mixed data types with None handling
        smart_sum([1, None, 3, 5])  # Returns: 9.0
    """
    
    def extract_value(item):
        """Extract numeric value from various data types."""
        if item is None:
            return None
        elif isinstance(item, SupportsFloat):
            return float(item)
        elif isinstance(item, dict) and key is not None:
            val = item.get(key)
            return float(val) if isinstance(val, SupportsFloat) else None
        elif hasattr(item, key) and key is not None:
            val = getattr(item, key)
            return float(val) if isinstance(val, SupportsFloat) else None
        else:
            return None
    
    # Extract and filter values
    numeric_values = []
    for item in values:
        val = extract_value(item)
        if val is None:
            if not ignore_none:
                continue
        else:
            if ignore_negative and val < 0:
                continue
            if ignore_zero and val == 0:
                continue
            numeric_values.append(val)
    
    if not numeric_values:
        return 0.0 if round_result is None else round(0.0, round_result)
    
    # Calculate sum and statistics
    total = sum(numeric_values)
    
    if round_result is not None:
        total = round(total, round_result)
    
    # Return detailed statistics for multiple values
    if len(numeric_values) > 1:
        return {
            'sum': total,
            'count': len(numeric_values),
            'mean': statistics.mean(numeric_values),
            'median': statistics.median(numeric_values),
            'min': min(numeric_values),
            'max': max(numeric_values)
        }
    else:
        return total

def weighted_sum(values: List[Dict[str, SupportsFloat]], 
                value_key: str = 'value',
                weight_key: str = 'weight') -> float:
    """
    Calculate weighted sum of dictionary values.
    
    Args:
        values: List of dictionaries containing values and weights
        value_key: Key for the value to sum (default: 'value')
        weight_key: Key for the weight (default: 'weight')
    
    Returns:
        Weighted sum as float
        
    Example:
        weighted_sum([
            {'value': 10, 'weight': 2},
            {'value': 20, 'weight': 1}
        ])  # Returns: 40.0 (10*2 + 20*1)
    """
    total = 0.0
    for item in values:
        value = item.get(value_key, 0)
        weight = item.get(weight_key, 1)
        if isinstance(value, SupportsFloat) and isinstance(weight, SupportsFloat):
            total += float(value) * float(weight)
    return total

def conditional_sum(values: List[Union[SupportsFloat, Dict[str, Any]]],
                   condition_func,
                   key: Optional[str] = None) -> float:
    """
    Sum values that meet a specific condition.
    
    Args:
        values: List of numbers or dictionaries
        condition_func: Function that takes a value and returns boolean
        key: Key to extract value from dictionaries (optional)
    
    Returns:
        Sum of values meeting condition
        
    Example:
        # Sum only even numbers
        conditional_sum([1, 2, 3, 4, 5], lambda x: x % 2 == 0)  # Returns: 6.0
        
        # Sum amounts greater than 100 from dictionaries
        conditional_sum(
            [{'amount': 50}, {'amount': 150}, {'amount': 200}],
            lambda x: x > 100,
            key='amount'
        )  # Returns: 350.0
    """
    total = 0.0
    for item in values:
        if isinstance(item, dict) and key is not None:
            val = item.get(key)
        else:
            val = item
            
        if isinstance(val, SupportsFloat) and condition_func(val):
            total += float(val)
    return total