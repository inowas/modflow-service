import flopy.modflow as mf
import geojson
import numpy as np


class WelAdapter:
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
            if key == 'stress_period_data':
                default[key] = self.to_dict(self._data[key])
                continue

            default[key] = self._data[key]
        return default

    def to_dict(self, data):
        if type(data) == list:
            spd_dict = {}
            for stress_period, record in enumerate(data):
                spd_dict[stress_period] = record
            return spd_dict
        return data

    def get_package(self, _mf):
        content = self.merge()
        return mf.ModflowWel(
            _mf,
            **content
        )

    @staticmethod
    def default():
        default = {
            "ipakcb": None,
            "stress_period_data": None,
            "dtype": None,
            "extension": 'wel',
            "options": None,
            "unitnumber": None,
            "filenames": None,
            "add_package": True,
        }

        return default

    @staticmethod
    def read_package(package):
        content = {
            "ipakcb": package.ipakcb,
            # stress period data values translated to list of lists to be json serializable
            "stress_period_data": {k: [list(i) for i in v] for k, v in package.stress_period_data.data.items()},
            # "dtype": package.dtype,
            "extension": package.extension[0],
            "unitnumber": package.unit_number[0],
            # options is None if options list is empty:
            "options": package.options if package.options else None
        }
        return content

    @staticmethod
    def generate_import(model: mf.Modflow, target_epsg=4326):
        if not isinstance(model, mf.Modflow):
            raise FileNotFoundError('Model not loaded')

        def get_cell_center(grid, c):
            xcz = grid.xcellcenters
            ycz = grid.ycellcenters
            nx, ny = int(c[0]), int(c[1])

            return xcz[ny][nx], ycz[ny][nx]

        default = 0
        try:
            wel: mf.ModflowWel = model.wel
            flux = np.array(wel.stress_period_data.array["flux"])
            flux_cells = np.argwhere(~np.isnan(flux))

            well_cells = []
            for cell in flux_cells:
                sp, l, r, c = cell
                if [l, r, c] not in well_cells:
                    well_cells.append([l, r, c])

            from pyproj import Transformer
            tf = Transformer.from_crs(int(model.modelgrid.epsg), int(target_epsg), always_xy=True)

            wel_boundaries = []
            for idx, cell in enumerate(well_cells):
                l, r, c = cell
                center_x, center_y = get_cell_center(model.modelgrid, [c, r])
                center = tf.transform(center_x, center_y)

                sp_values = []
                for spd in flux:
                    value = spd[l][r][c]
                    if ~np.isnan(value):
                        sp_values.append(value)
                        continue

                    sp_values.append(default)

                wel_boundaries.append({
                    'type': 'wel',
                    'name': 'Well ' + str(idx + 1),
                    'geometry': geojson.Point(center),
                    'layers': [l],
                    'sp_values': sp_values,
                    'cells': [[c, r]]
                })

            return wel_boundaries

        except AttributeError:
            return []
