import flopy.modflow as mf


class FhbAdapter:
    _data = None

    def __init__(self, data):
        self._data = data

    def validate(self):
        # should be implemented
        # for key in content:
        #   do something
        #   return some hints
        pass

    def is_valid(self):
        # should be implemented
        # for key in content:
        #   do something
        #   return true or false
        return True

    def merge(self):
        default = self.default()
        for key in self._data:
            default[key] = self._data[key]

        return default

    def get_package(self, _mf):
        content = self.merge()
        return mf.ModflowFhb(
            _mf,
            **content
        )

    @staticmethod
    def default():
        default = {
            "nbdtim": 1,
            "nflw": 0,
            "nhed": 0,
            "ifhbss": 0,
            "ipakcb": None,
            "nfhbx1": 0,
            "nfhbx2": 0,
            "ifhbpt": 0,
            "bdtimecnstm": 1.0,
            "bdtime": [0.0],
            "cnstm5": 1.0,
            "ds5": None,
            "cnstm7": 1.0,
            "ds7": None,
            "extension": 'fhb',
            "unitnumber": None,
            "filenames": None
        }

        return default

    @staticmethod
    def read_package(package):
        content = {
            "nbdtim": package.nbdtim,
            "nflw": package.nflw,
            "nhed": package.nhed,
            "ifhbss": package.ifhbss,
            "nfhbx1": package.nfhbx1,
            "nfhbx2": package.nfhbx2,
            "ifhbpt": package.ifhbpt,
            "bdtimecnstm": package.bdtimecnstm,
            "bdtime": package.bdtime,
            "cnstm5": package.cnstm5,
            "ds5": package.ds5,
            "cnstm7": package.cnstm7,
            "ds7": package.ds7,
            "extension": package.extension,
            "unitnumber": package.unitnumber,
            "filenames": package.filenames,
        }
        return content
