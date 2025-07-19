from pesq import pesq as _pesq

def pesq(rate, ref, deg, mode="wb", *args, **kwargs):
    """Proxy to pesq.pesq preserving the original pypesq interface."""
    return _pesq(rate, ref, deg, mode, *args, **kwargs)

__all__ = ["pesq"] 