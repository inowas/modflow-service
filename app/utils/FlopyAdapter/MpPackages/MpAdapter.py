import flopy.modpath as mp


class MpAdapter:
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
        return mp.Modpath(
            **content
        )

    @staticmethod
    def default():
        return {
            "modelname": 'modpathtest',
            "simfile_ext": 'mpsim',
            "namefile_ext": 'mpnam',
            "version": 'modpath',
            "exe_name": 'mp6.exe',
            "modflowmodel": None,
            "dis_file": None,
            "dis_unit": 87,
            "head_file": None,
            "budget_file": None,
            "model_ws": None,
            "external_path": None,
            "verbose": False,
            "load": True,
            "listunit": 7
        }

    @staticmethod
    def read_package(package):
        return {
            "modelname": package.modelname,
            "simfile_ext": package.simfile_ext,
            "namefile_ext": package.namefile_ext,
            "version": package.version,
            "exe_name": package.exe_name,
            "modflowmodel": package.modflowmodel,
            "dis_file": package.dis_file,
            "dis_unit": package.dis_unit,
            "head_file": package.head_file,
            "budget_file": package.budget_file,
            "model_ws": package.model_ws,
            "external_path": package.external_path,
            "verbose": package.verbose,
            "load": package.load,
            "listunit": package.listunit
        }
