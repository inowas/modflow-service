import flopy.seawat as seawat


class VdfAdapter:
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

    def get_package(self, _swt):
        content = self.merge()
        return seawat.SeawatVdf(
            _swt,
            **content
        )

    @staticmethod
    def default():
        default = {
            "mtdnconc": 1,
            "mfnadvfd": 1,
            "nswtcpl": 1,
            "iwtable": 1,
            "densemin": 1.0,
            "densemax": 1.025,
            "dnscrit": 0.01,
            "denseref": 1.0,
            "denseslp": 0.025,
            "drhodc": 0.01,
            "crhoref": 0,
            "firstdt": 0.001,
            "indense": 1,
            "dense": 1.0,
            "nsrhoeos": 1,
            "drhodprhd": 0.00446,
            "prhdref": 0.0,
            "extension": 'vdf',
            "unitnumber": None
        }
        return default

    @staticmethod
    def read_package(package):
        return {
            "mtdnconc": package.mtdnconc,
            "mfnadvfd": package.mfnadvfd,
            "nswtcpl": package.nswtcpl,
            "iwtable": package.iwtable,
            "densemin": package.densemin,
            "densemax": package.densemax,
            "dnscrit": package.dnscrit,
            "denseref": package.denseref,
            "denseslp": package.denseslp,
            "crhoref": package.crhoref,
            "firstdt": package.firstdt,
            "indense": package.indense,
            "dense": package.dense,
            "nsrhoeos": package.nsrhoeos,
            "drhodprhd": package.drhodprhd,
            "prhdref": package.prhdref,
            "extension": package.extension,
            "unitnumber": package.unitnumber,
            "filenames": package.filenames
        }
