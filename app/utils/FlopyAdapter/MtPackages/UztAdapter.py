import flopy.mt3d as mt


class UztAdapter:
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

    def get_package(self, _mt):
        content = self.merge()
        return mt.Mt3dUzt(
            _mt,
            **content
        )

    @staticmethod
    def default():
        default = {
            "icbcuz": None,
            "iet": 0,
            "iuzfbnd": None,
            "cuzinf": None,
            "cuzet": None,
            "cgwet": None,
            "extension": 'uzt',
            "unitnumber": None,
            "filenames": None,
        }
        return default

    @staticmethod
    def read_package(package):
        content = {
            "icbcuz": package.icbcuz,
            "iet": package.iet,
            "iuzfbnd": package.iuzfbnd,
            "cuzinf": package.cuzinf,
            "cuzet": package.cuzet,
            "cgwet": package.cgwet,
            "extension": package.extension,
            "unitnumber": package.unitnumber,
            "filenames": package.filenames
        }
        return content
