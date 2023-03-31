import flopy.modpath as mp


class SimAdapter:
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

    def get_package(self, _mp):
        content = self.merge()
        return mp.ModpathSim(
            _mp,
            **content
        )

    @staticmethod
    def default():
        return {
            "mp_name_file": 'mp.nam',
            "mp_list_file": 'mp.list',
            "option_flags": [1, 2, 1, 1, 1, 2, 2, 1, 2, 1, 1, 1],
            "ref_time": 0,
            "ref_time_per_stp": [0, 0, 1.0],
            "stop_time": None,
            "group_name": ['group_1'],
            "group_placement": [[1, 1, 1, 0, 1, 1]],
            "release_times": [[1, 1]],
            "group_region": [[1, 1, 1, 1, 1, 1]],
            "mask_nlay": [1],
            "mask_layer": [1],
            "mask_1lay": [1],
            "face_ct": [1],
            "ifaces": [[6, 1, 1]],
            "part_ct": [[1, 1, 1]],
            "time_ct": 1,
            "release_time_incr": 1,
            "time_pts": [1],
            "particle_cell_cnt": [[2, 2, 2]],
            "cell_bd_ct": 1,
            "bud_loc": [[1, 1, 1, 1]],
            "trace_id": 1,
            "stop_zone": 1,
            "zone": 1,
            "retard_fac": 1.0,
            "retard_fcCB": 1.0,
            "strt_file": None,
            "extension": 'mpsim'
        }

    @staticmethod
    def read_package(package):
        return {
            "mp_name_file": package.mp_name_file,
            "mp_list_file": package.mp_list_file,
            "option_flags": package.option_flags,
            "ref_time": package.ref_time,
            "ref_time_per_stp": package.ref_time_per_stp,
            "stop_time": package.stop_time,
            "group_name": package.group_name,
            "group_placement": package.group_placement,
            "release_times": package.release_times,
            "group_region": package.group_region,
            "mask_nlay": package.mask_nlay,
            "mask_layer": package.mask_layer,
            "mask_1lay": package.mask_1lay,
            "face_ct": package.face_ct,
            "ifaces": package.ifaces,
            "part_ct": package.part_ct,
            "time_ct": package.time_ct,
            "release_time_incr": package.release_time_incr,
            "time_pts": package.time_pts,
            "particle_cell_cnt": package.particle_cell_cnt,
            "cell_bd_ct": package.cell_bd_ct,
            "bud_loc": package.bud_loc,
            "trace_id": package.trace_id,
            "stop_zone": package.stop_zone,
            "zone": package.zone,
            "retard_fac": package.retard_fac,
            "retard_fcCB": package.retard_fcCB,
            "strt_file": package.strt_file,
            "extension": package.extension
        }
