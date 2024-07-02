__all__ = [
    'PiCustomKeysLookup'
]

from oasislmf.lookup.base import MultiprocLookupMixin
from oasislmf.lookup.interface import KeyLookupInterface
from oasislmf.utils.exceptions import OasisException




class UnserializableException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.file_handle = open(__file__, 'r')  # Adding a file handle makes it unserializable

#import pickle
#try:
#    raise UnserializableException("This exception cannot be serialized.")
#except UnserializableException as e:
#    print(f"Exception raised: {e}")
#    try:
#        serialized_exception = pickle.dumps(e)
#    except pickle.PicklingError as pe:
#        print(f"Serialization failed: {pe}")
#    except Exception as ex:
#        print(f"An unexpected error occurred: {ex}")


class PiCustomKeysLookup(KeyLookupInterface, MultiprocLookupMixin):


    def __init__(self, config, **kwargs):
        pass

    def process_locations(self, loc_df, **kwargs):
        #raise ValueError('This is an Injected error for a custrom lookup class')
        raise UnserializableException('This is an Injected error for a custrom lookup class - that cant be serialized?')

