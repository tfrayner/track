"""
This module implements the parsing of GTF files.

http://genome.ucsc.edu/FAQ/FAQformat.html#format4
"""

# Built-in modules #
import shlex

# Internal modules #
from track.parse import Parser
from track.common import iterate_lines
from track.util import strand_to_int

# Constants #
all_fields = ['source', 'feature', 'start', 'end', 'score', 'strand', 'frame']

################################################################################
class ParserGTF(Parser):
    format = 'gtf'
    def parse(self):
        # Initial variables #
        info   = {}
        declare_track = True
        # Main loop #
        for number, line in iterate_lines(self.path):
            # Ignored lines #
            if line.startswith("browser "): continue
            # Track headers #
            if line.startswith("track "):
                try:
                    info = dict([p.split('=',1) for p in shlex.split(line[6:])])
                except ValueError:
                    self.handler.error("The track%s seems to have an invalid <track> header line", self.path, number)
                declare_track = True
                continue
            # Split the lines #
            items = line.split('\t')
            if len(items) == 1: items = line.split()
            if len(items) > 8: items = items[0:8] + [' '.join(items[8:])]
            # Chromosome #
            chrom = items.pop(0)
            # Length is nine #
            if len(items) != 8:
                self.handler.error("The track%s doesn't have nine columns", self.path, number)
            # Have we started a track already ? #
            if declare_track:
                declare_track = False
                self.handler.newTrack(info, self.name)
            # Source field #
            if items[0] == '.': items[0] = ''
            # Name field #
            if items[1] == '.': items[1] = ''
            # Start and end fields #
            try:
                items[2] = int(items[2])
                # Convert Ensembl numbering to UCSC convention #
                items[3] = int(items[3]) + 1
            except ValueError:
                self.handler.error("The track%s has non integers as interval bounds", self.path, number)
            # Strand field #
            items[5] = strand_to_int(items[5])
            # Frame field #
            if items[6] == '.': items[6] = None
            else:
                try:
                    items[6] = int(items[6])
                except ValueError:
                    self.handler.error("The track%s has non integers as frame value", self.path, number)
            # The last special column #
            attr = shlex.split(items.pop())
            attr = [(attr[i],attr[i+1].strip(';')) for i in xrange(0,len(attr),2)]
            # Not using dict to preserve annotation order #
            keys, values = [x[0] for x in attr], [x[1] for x in attr]
            # GTF attribute column must have annotations starting with "gene_id" and "transcript_id" #
            assert ["gene_id", "transcript_id"] == keys[:2], "Invalid " \
                    "attribute column: %r. Valid attributes begin with " \
                    "\"gene_id\" and \"transcript_id\""
            self.handler.defineFields(all_fields + keys)
            items += values
            # Yield it #
            self.handler.newFeature(chrom, items)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
