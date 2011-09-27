"""
This module implements the parsing of BED files.

http://genome.ucsc.edu/FAQ/FAQformat.html#format1
"""

# Built-in modules #
import shlex

# Internal modules #
from track.parse import Parser
from track.common import iterate_lines

################################################################################
class ParserBED(Parser):
    format_identifier   = 'bed'
    all_fields_possible = ['start', 'end', 'name', 'score', 'strand', 'thick_start', 'thick_end',
                           'item_rgb', 'block_count', 'block_sizes', 'block_starts']

    def __call__(self):
        fields = []
        for number, line in iterate_lines(self.path):
            # Ignored lines #
            if line.startswith("browser "): continue
            # Track headers #
            if line.startswith("track "):
                try:
                    self.handler.newTrack(dict([p.split('=',1) for p in shlex.split(line[6:])]))
                except ValueError:
                    self.handler.error(self.path, number, "The track%s seems to have an invalid <track> header line")
                continue
            # Fields #
            items = line.split()
            if not fields:
                self.handler.defineFields(fields)
            # Chromosome field #
            try:
                if not item[0]:
                    self.handler.error(self.path, number, "The track%s is missing a chromosome")
            except IndexError:
                self.handler.error(self.path, number, "The track%s has no columns")
            # Start and end fields #
            try:
                items[1] = int(items[1])
                items[2] = int(items[2])
            except ValueError:
                self.handler.error(self.path, number, "The track%s has non integers as interval bounds")
            except IndexError:
                self.handler.error(self.path, number, "The track%s has less than two columns")
            if line[2] <= line[1]:
                self.handler.error(self.path, number, "The track%s has negative or null intervals")
            # All following fields are optional #
            try:
                # Name field #
                if items[3] == '.': items[3] = ''
                # Score field #
                if items[4] == '.' or items[4] == '': items[4] = 0.0
                try:
                    items[4] = float(items[4])
                except ValueError:
                    self.handler.error(self.path, number, "The track%s has non floats as score values")
                # Strand field #
                if   items[5] == '+': items[5] =  1
                elif items[5] == '-': items[5] = -1
                else:                 items[5] =  0
                # Thick starts #
                try:
                    items[6] = float(items[6])
                except ValueError:
                    self.handler.error(self.path, number, "The track%s has non integers as thick starts")
                # Thick ends #
                try:
                    items[7] = float(items[7])
                except ValueError:
                    self.handler.error(self.path, number, "The track%s has non integers as thick ends")
            # All index errors are ignored since the fields are optional #
            except IndexError:
                pass
            finally:
                self.handler.newFeature(items)
            # Return the handler tracks #
            return self.handler.tracks
