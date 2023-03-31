import flopy.modflow as mf


class EvtAdapter:
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
        return mf.ModflowEvt(
            _mf,
            **content
        )

    @staticmethod
    def default():
        return {
            "nevtop": 3,
            "ipakcb": None,
            "surf": 0.,
            "evtr": 1e-3,
            "exdp": 1.,
            "ievt": 1,
            "extension": 'evt',
            "unitnumber": None,
            "filenames": None,
            "external": True
        }

    @staticmethod
    def read_package(package):
        return {
            "nevtop": package.nevtop,
            "ipakcb": package.ipakcb,
            "surf": package.surf,
            "evtr": package.evtr,
            "exdp": package.exdp,
            "ievt": package.ievt,
            "extension": package.extension,
            "unitnumber": package.unitnumber,
            "filenames": package.filenames,
            "external": package.external
        }
