__all__ = [
    'PiCustomKeysLookup'
]

from oasislmf.lookup.base import MultiprocLookupMixin
from oasislmf.lookup.interface import KeyLookupInterface
from oasislmf.utils.exceptions import OasisException


class PiCustomKeysLookup(KeyLookupInterface, MultiprocLookupMixin):


    def __init__(self, config, **kwargs):
        pass

    def process_locations(self, loc_df, **kwargs):
        raise ValueError('This is an Injected error for a custrom lookup class')
