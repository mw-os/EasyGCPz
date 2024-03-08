"""
EasyGCPz takes a significant load off of python users of GCP by
automating query generation, executing queries, and returning
query results in a number of optional accessible data structures.
EasyGCPz enables users of any skill level to unlock their querying
potential by offering multiple degrees of flexibility, while also
being robust against a wide number of common querying and usage
problems.
"""

__author__ = 'MW-OS'
__version__ = '0.1.0'
__date__ = '2024.03'

from .main import EasyGCPz as easygcpz

__all__ = ["easygcpz", '__author__', '__version__', '__date__']

# eof
