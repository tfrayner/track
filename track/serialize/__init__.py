"""
This subpackage contains one python source file per format implemented for serialization.
"""

# Built-in modules #
import sys

# Variables #
serializers = {
    'sql': {'module': 'track.serialize.sql', 'class': 'SerializerSQL'},
}

################################################################################
def get_serializer(path, format):
    """Given a path and a format will return the appropriate serializer.

            * *path* is a string specifying the path of the track to parse.
            * *format* is a string specifying the format of the track to parse.

        Examples::

            import track.parse
            import track.serialze
            serializer = track.serialize.get_serializer('tmp/test.sql', 'sql')
            parser = track.parse.get_parser('tmp/test.bed', 'bed')
            parser(serializer)

        ``get_serializer`` returns a Serializer instance.
    """
    if not format in serializers: raise Exception("The format '" + format + "' is not supported.")
    info = serializers[format]
    # Import the objects #
    base_module    = __import__(info['module'])
    sub_module     = sys.modules[info['module']]
    class_object   = getattr(sub_module, info['class'])
    class_instance = class_object(path)
    # Return an instance #
    return class_instance

################################################################################
class Serializer(object):
    def __init__(self, path):
        self.path = path
        self.tracks = []

    def __enter__(self):
        return self

    def __exit__(self, errtype, value, traceback):
        pass

    def error(self, path, line_number, message):
        location = " '" + path + ":" + str(line_number) + "'"
        raise Exception(message % location)

    def defineFields(fields):
        self.fields = fields

    def newTrack(attributes):
        self.tracks.append({'info': attributes, 'features': []})

    def newFeature(feature):
        self.tracks[-1]['features'].append(feature)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
