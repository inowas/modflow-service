"""
This module is an intermediate layer between flopy version 3.2
and the inowas-modflow-configuration format.

Serialize Modflow and MT3D model into JSON format
"""
import os
import json
import flopy.modflow
import flopy.mt3d

from ...FlopyAdapter import MfPackages, MtPackages


class InowasFlopyImportAdapter:
    """
    The Flopy Import Class.
    Serialize given Modflow and MT3D models to json format and
    writes it to specified .json file
    """

    def __init__(self, model_ws, json_file, mf_namfile=None, mt_namfile=None,
                 type_="flopy_calculation", version="3.2.6", calculation_id="default",
                 author="default", project="default", model_id="default",
                 run_model=True, write_input=True):

        self.model_data = {
            "author": author,
            "project": project,
            "type": type_,
            "version": version,
            "calculation_id": calculation_id,
            "model_id": model_id,
            "write_input": write_input,
            "run_model": run_model,
            "data": {}
        }
        self._report = ''
        self.json_file = json_file
        self.mf_packages = []
        self.mt_packages = []
        self.mf_model, self.mt_model = None, None

        if mf_namfile is not None:
            self.mf_model = flopy.modflow.Modflow.load(os.path.join(model_ws, mf_namfile))
            self.model_data["data"]["mf"] = {"packages": ["MF"]}
            self.model_data["data"]["mf"]["packages"] += self.mf_model.get_package_list()
            self.model_data["data"]["mf"]["write_input"] = write_input
            self.model_data["data"]["mf"]["run_model"] = run_model
        if mt_namfile is not None:
            self.mt_model = flopy.mt3d.Mt3dms.load(os.path.join(model_ws, mt_namfile))
            self.model_data["data"]["mt"] = {"packages": ["MT"]}
            self.model_data["data"]["mt"]["packages"] += self.mt_model.get_package_list()
            self.model_data["data"]["mt"]["write_input"] = write_input
            self.model_data["data"]["mt"]["run_model"] = run_model

    @staticmethod
    def np_type_translate(obj):
        try:
            return obj.item()
        except:
            raise TypeError('Object %s is not JSON serializable and not Numpy dtype' % type(obj))

    def serialize(self):
        # Encode packages content to JSON
        for package_name in self.model_data["data"]["mf"]["packages"] + self.model_data["data"]["mt"]["packages"]:
            try:
                self.read_packages(name=package_name, data=self.model_data["data"])
                self._report += "Successfully read the package: %s \n" % package_name
            except:
                self._report += "Could not read package: %s \n" % package_name

        try:
            with open(self.json_file, 'w') as f:
                json.dump(self.model_data, f, default=self.np_type_translate)
            self._report += "Model input saved to %s \n" % self.json_file
        except:
            self._report += "Could not save input to %s \n" % self.json_file

    def read_packages(self, name, data):
        # Modflow packages
        if name == 'MF':
            data["mf"][name] = MfPackages.MfAdapter(data=None).read_package(self.mf_model)
        if name == 'DIS':
            data["mf"][name] = MfPackages.DisAdapter(data=None).read_package(self.mf_model.get_package(name))
        if name == 'BAS' or name == 'BAS6':
            data["mf"][name] = MfPackages.BasAdapter(data=None).read_package(self.mf_model.get_package(name))
        if name == 'LPF':
            data["mf"][name] = MfPackages.LpfAdapter(data=None).read_package(self.mf_model.get_package(name))
        if name == 'PCG':
            data["mf"][name] = MfPackages.PcgAdapter(data=None).read_package(self.mf_model.get_package(name))
        if name == 'OC':
            data["mf"][name] = {}
            # data["mf"][name] = MfPackages.OcAdapter(data=None).read_package(self.mf_model.get_package(name))
        if name == 'WEL':
            data["mf"][name] = MfPackages.WelAdapter(data=None).read_package(self.mf_model.get_package(name))
        if name == 'CHD':
            data["mf"][name] = MfPackages.ChdAdapter(data=None).read_package(self.mf_model.get_package(name))
        if name == 'LMT' or name == 'LMT6':
            data["mf"][name] = MfPackages.LmtAdapter(data=None).read_package(self.mf_model.get_package(name))
        if name == 'NWT':
            data["mf"][name] = MfPackages.NwtAdapter(data=None).read_package(self.mf_model.get_package(name))
        # Not checked:
        # if name == 'UPW':
        #     data["mf"][name] = MfPackages.UpwAdapter(data=None).read_package(self.mf_model.get_package(name))
        # if name == 'RIV':
        #     data["mf"][name] = MfPackages.RivAdapter(data=None).read_package(self.mf_model.get_package(name))
        # if name == 'RCH':
        #     data["mf"][name] = MfPackages.RchAdapter(data=None).read_package(self.mf_model.get_package(name))
        # if name == 'GHB':
        #     data["mf"][name] = MfPackages.GhbAdapter(data=None).read_package(self.mf_model.get_package(name))

        # MT3D packages
        if name == 'MT':
            data["mt"][name] = MtPackages.MtAdapter(data=None).read_package(self.mt_model)
        if name == 'ADV':
            data["mt"][name] = MtPackages.AdvAdapter(data=None).read_package(self.mt_model.get_package(name))
        if name == 'BTN':
            data["mt"][name] = MtPackages.BtnAdapter(data=None).read_package(self.mt_model.get_package(name))
        if name == 'DSP':
            data["mt"][name] = MtPackages.DspAdapter(data=None).read_package(self.mt_model.get_package(name))
        if name == 'GCG':
            data["mt"][name] = MtPackages.GcgAdapter(data=None).read_package(self.mt_model.get_package(name))
        if name == 'SSM':
            data["mt"][name] = MtPackages.SsmAdapter(data=None).read_package(self.mt_model.get_package(name))
        # Not checked:
        # if name == 'LKT':
        #     data["mt"][name] = MtPackages.LktAdapter(data=None).read_package(self.mt_model.get_package(name))
        # if name == 'PHC':
        #     data["mt"][name] = MtPackages.PhcAdapter(data=None).read_package(self.mt_model.get_package(name))
        # if name == 'RCT':
        #     data["mt"][name] = MtPackages.RctAdapter(data=None).read_package(self.mt_model.get_package(name))
        # if name == 'SFT':
        #     data["mt"][name] = MtPackages.SftAdapter(data=None).read_package(self.mt_model.get_package(name))
        # if name == 'TOB':
        #     data["mt"][name] = MtPackages.TobAdapter(data=None).read_package(self.mt_model.get_package(name))
        # if name == 'UZT':
        #     data["mt"][name] = MtPackages.UztAdapter(data=None).read_package(self.mt_model.get_package(name))

    @property
    def response_message(self):
        return self._report
