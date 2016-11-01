import netCDF4 as nc
import numpy as np
from typing import Iterator

from .l1a.enums import L1AVariables


class NetCDFReader:
    """
    retrieves data from a netCDF document in blocks
    """

    @property
    def variables(self) -> Iterator[L1AVariables]:
        return iter(L1AVariables)

    @property
    def dimensions(self):
        return self._doc.dimensions

    def __init__(self, filename, chunk_size=20):
        """
        open document and set block size
        """

        self._doc = nc.Dataset(filename, 'r')
        self.cache = {}
        self.chunk_index = None
        self.chunk_size = chunk_size

        for varname in self.variables:
            name = varname.value

            var = self._doc.variables[name]
            size = list(var.shape)

            if size[0] > self.chunk_size:
                size[0] = self.chunk_size

    def get_value(self, varname: L1AVariables, index: int):
        """
        get the value of a variable at a specific index
        """
        chunk_index = index % self.chunk_size
        chunk_start = index - chunk_index

        if chunk_start != self.chunk_index:
            self._load_chunk(chunk_start)

        return self.cache[varname][chunk_index]

    def _load_chunk(self, chunk_start: int):
        """
        read a new chunk & replace the existing one
        """
        chunk_end = chunk_start + self.chunk_size

        for varname in self.variables:
            name = varname.value
            var = self._doc.variables[name]
            varlen = var.shape[0]

            if chunk_start >= varlen:
                continue

            end = min(varlen, chunk_end)
            clen = end - chunk_start

            self.cache[varname] = var[chunk_start:end].copy()

        self.chunk_index = chunk_start

    def close(self):
        self._doc.close()
