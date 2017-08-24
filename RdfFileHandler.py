import gzip
import logging
import os
from RdfHandler import RdfHandler

log = logging.getLogger('osm2rdf')

class RdfFileHandler(RdfHandler):
    def __init__(self, options):
        super(RdfFileHandler, self).__init__(options)
        self.file_counter = 0
        self.length = None
        self.output = None
        self.maxFileSize = self.options.maxFileSize * 1024 * 1024

    def finalize_object(self, obj, statements, obj_type):
        super(RdfFileHandler, self).finalize_object(obj, statements, obj_type)

        if statements:
            if self.length is None or self.length > self.maxFileSize:
                self.create_output_file()
                header = '\n'.join(['@' + p + ' .' for p in self.prefixes]) + '\n\n'
                self.output.write(header)
                self.length = len(header)

            text = self.types[obj_type] + str(id) + '\n' + ';\n'.join(statements) + '.\n\n'
            self.output.write(text)
            self.length += len(text)

    def create_output_file(self):
        self.flush()
        os.makedirs(self.options.output_dir, exist_ok=True)
        filename = os.path.join(self.options.output_dir, 'osm-{0:06}.ttl.gz'.format(self.file_counter))

        # TODO switch to 'xt'
        log.info('Exporting to {0}'.format(filename))
        self.output = gzip.open(filename, 'wt', compresslevel=5)
        self.file_counter += 1

    def flush(self):
        if self.output:
            if self.last_timestamp.year > 2000: # Not min-year
                self.output.write(
                    '\nosmroot: schema:dateModified {0} .' .format(self.format_date(self.last_timestamp)))
            self.output.flush()
            self.output = None
            log.info('{0}'.format(self.format_stats()))

    def run(self, input_file):
        if self.options.addWayLoc:
            self.apply_file(input_file, locations=True, idx=self.get_index_string())
        else:
            self.apply_file(input_file)