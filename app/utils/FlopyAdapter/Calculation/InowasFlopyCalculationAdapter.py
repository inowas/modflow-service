"""
This module is an intermediate layer between flopy version 3.2
and the inowas-modflow-configuration format.

Author: Ralf Junghanns
EMail: ralf.junghanns@gmail.com
"""
from ...FlopyAdapter import MfPackages as mf
from ...FlopyAdapter import MtPackages as mt
from ...FlopyAdapter import MpPackages as mp
from ...FlopyAdapter import SwtPackages as swt

from ...FlopyAdapter import Read as read
from ...FlopyAdapter import Statistics as stat


class InowasFlopyCalculationAdapter:
    """The Flopy Class"""

    _version = None
    _uuid = None

    _model = None

    _report = ''
    _success = False

    mf_package_order = [
        'mf', 'dis', 'bas', 'bas6',
        'chd', 'evt', 'drn', 'fhb', 'ghb', 'hob', 'lak', 'rch', 'riv', 'wel',
        'lpf', 'upw', 'pcg', 'nwt', 'oc', 'lmt', 'lmt6'
    ]

    mt_package_order = [
        'mt', 'btn', 'adv', 'dsp', 'gcg', 'ssm', 'lkt',
        'phc', 'rct', 'sft', 'tob', 'uzt'
    ]

    swt_package_order = [
        # Modflow
        'swt', 'dis', 'bas', 'bas6',
        'chd', 'evt', 'drn', 'fhb', 'ghb', 'hob', 'lak', 'rch', 'riv', 'wel',
        'lpf', 'upw', 'pcg', 'nwt', 'oc', 'lmt', 'lmt6',
        # Mt3D
        'btn', 'adv', 'dsp', 'gcg', 'ssm', 'lkt', 'phc', 'rct', 'sft', 'tob', 'uzt',
        # Seawat                                         
        'vdf', 'vsc'
    ]

    mp_package_order = [
        'mp', 'bas', 'sim'
    ]

    def __init__(self, version, data, uuid):
        self._mf_data = data.get('mf')
        self._mp_data = data.get('mp')
        self._mt_data = data.get('mt')
        self._swt_data = data.get('swt')
        self._version = version
        self._uuid = uuid

        # Model calculation if Seawat is enabled
        if self._swt_data is not None:
            package_data = {
                **self._mf_data,
                **self._mt_data,
                **self._swt_data,
                'packages': self._mf_data['packages'] + self._mt_data['packages'] + self._swt_data['packages']
            }

            package_content = self.read_packages(package_data)
            self.create_model(self.swt_package_order, package_content)
            self.write_input_model(self._model)
            self._success, report = self.run_model(self._model, model_type='swt')
            self._report += report

            if 'hob' in self._mf_data['packages']:
                print('Calculate hob-statistics and write to file %s.hob.stat' % uuid)
                self.run_hob_statistics(self._model)

            return

        # Normal Modflow calculation
        if self._mf_data is not None:
            package_content = self.read_packages(self._mf_data)
            self.create_model(self.mf_package_order, package_content)
            self.write_input_model(self._model)
            self.success, report = self.run_model(self._model, model_type='mf')
            self._report += report

            if 'hob' in self._mf_data['packages']:
                print('Calculate hob-statistics and write to file %s.hob.stat' % uuid)
                self.run_hob_statistics(self._model)

            # Mt3d calculation
            if self._mt_data is not None:
                package_content = self.read_packages(self._mt_data)
                self.create_model(self.mt_package_order, package_content)
                self.write_input_model(self._model)
                self._success, report = self.run_model(self._model, model_type='mt')
                self._report += report

            # ModPath6 calculation
            if self._mp_data is not None:
                package_content = self.read_packages(self._mp_data)
                self.create_model(self.mp_package_order, package_content)
                self.write_input_model(self._model)
                self._success, report = self.run_model(self._model, model_type='mp')
                self._report += report

    @staticmethod
    def read_packages(data):
        package_content = {}
        for package in data['packages']:
            print('Read Flopy package data: %s' % package)
            package_content[package.lower()] = data[package]
        return package_content

    def create_model(self, package_order, package_content):
        for package in package_order:
            if package in package_content:
                print('Create Flopy Package: %s' % package)
                self.create_package(package, package_content[package])

    @staticmethod
    def write_input_model(model):
        print('Write input files.')
        model.write_input()

    @staticmethod
    def run_model(model, model_type) -> (bool, str):
        normal_msg = 'normal termination'
        if model_type == 'mt':
            normal_msg = 'Program completed'

        print('Run model type: %s.' % model_type)
        print('Model nam-file: %s.' % model.namefile)
        print('Model executable: %s.' % model.exe_name)
        success, report = model.run_model(report=True, silent=True, normal_msg=normal_msg)
        return success, '\n'.join(str(line) for line in report)

    @staticmethod
    def run_hob_statistics(model):
        model_ws = model.model_ws
        name = model.name

        print('Calculate hob-statistics for model %s' % name)
        stat.HobStatistics(model_ws, name).write_files()

    def check_model(self, f):
        if self._model is not None:
            self._model.check(f)

    def create_package(self, name, content):

        # Modflow packages
        if name == 'mf':
            self._model = mf.MfAdapter(content).get_package()
        if name == 'dis':
            mf.DisAdapter(content).get_package(self._model)
        if name == 'drn':
            mf.DrnAdapter(content).get_package(self._model)
        if name == 'bas' or name == 'bas6':
            mf.BasAdapter(content).get_package(self._model)
        if name == 'lpf':
            mf.LpfAdapter(content).get_package(self._model)
        if name == 'upw':
            mf.UpwAdapter(content).get_package(self._model)
        if name == 'pcg':
            mf.PcgAdapter(content).get_package(self._model)
        if name == 'nwt':
            mf.NwtAdapter(content).get_package(self._model)
        if name == 'oc':
            mf.OcAdapter(content).get_package(self._model)
        if name == 'riv':
            mf.RivAdapter(content).get_package(self._model)
        if name == 'lak':
            mf.LakAdapter(content).get_package(self._model)
        if name == 'wel':
            mf.WelAdapter(content).get_package(self._model)
        if name == 'rch':
            mf.RchAdapter(content).get_package(self._model)
        if name == 'evt':
            mf.EvtAdapter(content).get_package(self._model)
        if name == 'chd':
            mf.ChdAdapter(content).get_package(self._model)
        if name == 'fhb':
            mf.FhbAdapter(content).get_package(self._model)
        if name == 'ghb':
            mf.GhbAdapter(content).get_package(self._model)
        if name == 'hob':
            mf.HobAdapter(content).get_package(self._model)
        if name == 'lmt':
            mf.LmtAdapter(content).get_package(self._model)

        # MT3D packages
        if name == 'mt':
            self._model = mt.MtAdapter(content).get_package(self._model)
        if name == 'adv':
            mt.AdvAdapter(content).get_package(self._model)
        if name == 'btn':
            mt.BtnAdapter(content).get_package(self._model)
        if name == 'dsp':
            mt.DspAdapter(content).get_package(self._model)
        if name == 'gcg':
            mt.GcgAdapter(content).get_package(self._model)
        if name == 'lkt':
            mt.LktAdapter(content).get_package(self._model)
        if name == 'phc':
            mt.PhcAdapter(content).get_package(self._model)
        if name == 'rct':
            mt.RctAdapter(content).get_package(self._model)
        if name == 'sft':
            mt.SftAdapter(content).get_package(self._model)
        if name == 'ssm':
            mt.SsmAdapter(content).get_package(self._model)
        if name == 'tob':
            mt.TobAdapter(content).get_package(self._model)
        if name == 'uzt':
            mt.UztAdapter(content).get_package(self._model)

        # ModPath packages
        if name == 'mp':
            self._model = mp.MpAdapter(content).get_package()
        if name == 'mpbas':
            self._model = mp.BasAdapter(content).get_package(self._model)
        if name == 'mpsim':
            self._model = mp.SimAdapter(content).get_package(self._model)

        # Seawat packages
        if name == 'swt':
            self._model = swt.SwtAdapter(content).get_package()
        if name == 'vdf':
            swt.VdfAdapter(content).get_package(self._model)
        if name == 'vsc':
            swt.VscAdapter(content).get_package(self._model)

    def response(self):
        key = 'mf'
        if 'MF' in self._mf_data:
            key = 'MF'

        budgets = read.ReadBudget(self._mf_data[key]['model_ws'])
        concentrations = read.ReadConcentration(self._mf_data[key]['model_ws'])
        drawdowns = read.ReadDrawdown(self._mf_data[key]['model_ws'])
        heads = read.ReadHead(self._mf_data[key]['model_ws'])

        return {
            'budgets': budgets.read_times(),
            'concentrations': concentrations.read_times(),
            'drawdowns': drawdowns.read_times(),
            'heads': heads.read_times(),
            'number_of_layers': heads.read_number_of_layers()
        }

    def success(self):
        return self._success

    def response_message(self):
        return self._report

    def short_response_message(self):
        if len(self._report.split('\n')) < 50:
            return self._report

        first_lines = '\n'.join(self._report.split('\n')[:40])
        last_lines = '\n'.join(self._report.split('\n')[-10:])

        return first_lines + '\n\n...\n\n' + last_lines