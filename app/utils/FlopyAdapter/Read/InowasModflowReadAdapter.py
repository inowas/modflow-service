import flopy as fp
import geojson
import glob
import numpy as np
import os
import rasterio.features
import sys
import utm
from flopy.discretization import StructuredGrid
from pyproj import Transformer
from ..MfPackages import WelAdapter


class InvalidArgumentException(Exception):
    pass


class InvalidModelUnitException(Exception):
    pass


class InowasModflowReadAdapter:
    _ws = None
    _mf = None

    @staticmethod
    def load(path):

        abspath = os.path.abspath(os.path.join(path))
        if not os.path.exists(abspath):
            raise FileNotFoundError('Path not found: ' + path)

        if len(glob.glob1(abspath, "*.nam")) == 0 and len(glob.glob1(abspath, "*.mfn")) == 0:
            raise FileNotFoundError('Modflow name file with ending .nam or .mfn not found')

        orig_stdout = sys.stdout
        f = open(os.path.join(abspath, 'load.log'), 'w')
        sys.stdout = f

        instance = InowasModflowReadAdapter()
        instance._ws = path

        name_file = ''
        if len(glob.glob1(abspath, "*.nam")) > 0:
            name_file = glob.glob1(abspath, "*.nam")[0]

        if len(glob.glob1(abspath, "*.mfn")) > 0:
            name_file = glob.glob1(abspath, "*.mfn")[0]

        try:
            instance._mf = fp.modflow.Modflow.load(
                os.path.join(abspath, name_file),
                check=True,
                forgive=True,
                model_ws=abspath,
                verbose=True,
            )

            sys.stdout = orig_stdout
            f.close()

            return instance

        except:
            sys.stdout = orig_stdout
            f.close()
            raise

    @staticmethod
    def load_with_crs(path, xll, yll, epsg=4326, rot=None):
        try:
            instance = InowasModflowReadAdapter.load(path)

            # Transform to UTM with WGS84 as intermediate
            tf = Transformer.from_crs(epsg, 4326, always_xy=True)
            wgs84_xll, wgs84_yll = tf.transform(xll, yll)

            # Calculate the UTM-EPSG to use with pyproj
            _, _, zone_number, _ = utm.from_latlon(wgs84_yll, wgs84_xll)
            utm_epsg = f"326{zone_number:02d}" if wgs84_yll >= 0 else f"327{zone_number:02d}"

            tf = Transformer.from_crs(4326, int(utm_epsg), always_xy=True)
            xoff, yoff = tf.transform(wgs84_xll, wgs84_yll)

            modelgrid = instance._mf.modelgrid
            updated_modelgrid = StructuredGrid(
                modelgrid.delc,
                modelgrid.delr,
                modelgrid.top,
                modelgrid.botm,
                modelgrid.idomain,
                modelgrid.lenuni,
                epsg=utm_epsg,
                xoff=xoff,
                yoff=yoff,
                angrot=rot if not None else modelgrid.angrot
            )

            instance._mf.modelgrid = updated_modelgrid
            return instance

        except:
            raise

    def __init__(self):
        pass

    @property
    def modelgrid(self):
        if not isinstance(self._mf, fp.modflow.Modflow):
            raise FileNotFoundError('Model not loaded')

        return self._mf.modelgrid

    @property
    def modeltime(self):
        if not isinstance(self._mf, fp.modflow.Modflow):
            raise FileNotFoundError('Model not loaded')

        return self._mf.modeltime

    def get_ibound(self):
        if not isinstance(self._mf, fp.modflow.Modflow):
            raise FileNotFoundError('Model not loaded')

        bas_package = None
        package_list = self._mf.get_package_list()

        if 'BAS' in package_list:
            bas_package = self._mf.get_package('BAS')

        if 'BAS6' in package_list:
            bas_package = self._mf.get_package('BAS6')

        if not isinstance(bas_package, fp.modflow.ModflowBas):
            raise Exception('Bas package could not be loaded.')

        return bas_package.ibound.array

    @staticmethod
    def wgs82ToUtm(x, y):
        easting, northing, zone_number, zone_letter = utm.from_latlon(y, x)
        return easting, northing, zone_number, zone_letter

    @staticmethod
    def utmToWgs82XY(easting, northing, zone_number, zone_letter):
        latitude, longitude = utm.to_latlon(easting, northing, zone_number, zone_letter)
        return longitude, latitude

    @staticmethod
    def transform(tf: Transformer, cell):
        return tf.transform(cell[0], cell[1])

    def get_cell_center(self, c):
        grid: StructuredGrid = self.modelgrid
        xcz = grid.xcellcenters
        ycz = grid.ycellcenters
        nx, ny = int(c[0]), int(c[1])
        return [xcz[ny][nx], ycz[ny][nx]]

    def model_geometry(self, target_epsg=4326, layer=0):

        i_bound = self.get_ibound()
        if layer >= len(i_bound):
            raise Exception('Layer with key ' + str(layer) + 'not found. Max: ' + str(len(i_bound)))

        layer = i_bound[layer]
        mask = np.array(np.ma.masked_values(layer, 1, shrink=False), dtype=bool)
        mpoly_cells = []
        for vec in rasterio.features.shapes(layer, mask=mask):
            mpoly_cells.append(geojson.Polygon(vec[0]["coordinates"]))

        mpoly_cells = mpoly_cells[0]
        mpoly_coordinates_utm = geojson.utils.map_tuples(lambda c: self.get_cell_center(c), mpoly_cells)

        tf = Transformer.from_crs(int(self.modelgrid.epsg), int(target_epsg), always_xy=True)
        mpoly_coordinates_target = geojson.utils.map_tuples(lambda c: self.transform(tf, c), mpoly_coordinates_utm)

        # noinspection PyTypeChecker
        polygon = geojson.Polygon(mpoly_coordinates_target['coordinates'])
        return polygon

    def wel_boundaries(self, target_epsg=4326):
        return WelAdapter.generate_import(self._mf, target_epsg=target_epsg)

    def model_grid_size(self):
        if not isinstance(self._mf, fp.modflow.Modflow):
            raise FileNotFoundError('Model not loaded.')

        nrow, ncol, nlay, nper = self._mf.get_nrow_ncol_nlay_nper()

        return {
            'n_x': ncol,
            'n_y': nrow
        }

    def model_stress_periods(self, start_datetime=None):
        if not isinstance(self._mf, fp.modflow.Modflow):
            raise FileNotFoundError('Model not loaded.')

        if not isinstance(self._mf.dis, fp.modflow.ModflowDis):
            raise FileNotFoundError('Dis-Package not loaded.')

        time_unit = self._mf.dis.itmuni

        if time_unit != 4:
            raise InvalidModelUnitException('The time unit is required to be in days (4)')

        from datetime import datetime, timedelta
        mt = self._mf.modeltime

        if start_datetime is None:
            start_datetime = datetime.strptime(mt.start_datetime, '%m-%d-%Y')

        if not isinstance(start_datetime, datetime):
            raise InvalidModelUnitException('DateTime has to be None or instance od datetime.')

        end_datetime = start_datetime + timedelta(days=sum(mt.perlen.tolist()))

        stressperiods = []
        for sp_idx in range(0, mt.nper):
            start_date_time = start_datetime + timedelta(days=sum(mt.perlen.tolist()[0:sp_idx]))
            stressperiods.append({
                'start_date_time': str(start_date_time.date()),
                'nstp': mt.nstp.tolist()[sp_idx],
                'tsmult': mt.tsmult.tolist()[sp_idx],
                'steady': mt.steady_state[sp_idx]
            })

        return {
            'start_date_time': str(start_datetime.date()),
            'end_date_time': str(end_datetime.date()),
            'time_unit': time_unit,
            'stressperiods': stressperiods
        }

    def model_length_unit(self):
        if not isinstance(self._mf, fp.modflow.Modflow):
            raise FileNotFoundError('Model not loaded')

        if not isinstance(self._mf.dis, fp.modflow.ModflowDis):
            raise FileNotFoundError('Dis-Package not loaded.')

        return self._mf.dis.lenuni

    def model_time_unit(self):
        if not isinstance(self._mf, fp.modflow.Modflow):
            raise FileNotFoundError('Model not loaded')

        if not isinstance(self._mf.dis, fp.modflow.ModflowDis):
            raise FileNotFoundError('Dis-Package not loaded.')

        return self._mf.dis.itmuni
