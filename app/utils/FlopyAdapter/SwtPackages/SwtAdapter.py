import flopy.seawat as seawat


class SwtAdapter:
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

    def get_package(self):
        content = self.merge()
        return seawat.Seawat(
            **content
        )

    @staticmethod
    def default():
        return {
            "modelname": 'swttest',
            "namefile_ext": 'nam',
            "modflowmodel": None,
            "mt3dmodel": None,
            "version": 'seawat',
            "exe_name": 'swtv4',
            "structured": True,
            "listunit": 2,
            "model_ws": '.',
            "external_path": None,
            "verbose": False,
            "load": True,
            "silent": 0
        }

    @staticmethod
    def read_package(package):
        return {
            "modelname": package.modelname,
            "namefile_ext": package.namefile,
            "modflowmodel": package.modflowmodel,
            "mt3dmodel": package.mt3dmodel,
            "version": package.version,
            "exe_name": package.exe,
            "structured": package.structured,
            "listunit": package.listunit,
            "model_ws": package.model,
            "external_path": package.external,
            "verbose": package.verbose,
            "load": package.load,
            "silent": package.silent
        }
