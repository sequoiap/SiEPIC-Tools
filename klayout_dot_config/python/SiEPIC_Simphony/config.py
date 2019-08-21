import inspect

import simphony.core
import simphony.DeviceLibrary.ebeam as ebeam
import simphony.DeviceLibrary.ann as ann

#
#
# MODEL CONFIGURATIONS
#
#

ebeam_models = [x for x in inspect.getmembers(ebeam, inspect.isclass) if issubclass(x[1], simphony.core.base.ComponentModel)]
ann_models = [x for x in inspect.getmembers(ann, inspect.isclass) if issubclass(x[1], simphony.core.base.ComponentModel)]

all_models = {}
for model in ebeam_models:
    all_models[model[0]] = model[1]
for model in ann_models:
    all_models[model[0]] = model[1]

ebeam_component_list = [x[0] for x in ebeam_models]

selected_models = {}
for item in ebeam_component_list:
    selected_models[item] = all_models[item]

def set_model(component_type, model_name):
    selected_models[component_type] = all_models[model_name]

# # TODO: Format settings options to look prettier than it currently does
# hierarchy = {
#     "ebeam_wg_integral_1550": [
#         ebeam.ebeam_wg_integral_1550,
#         ann.ann_wg_integral,
#     ],
#     "ebeam_bdc_te1550": [
#         ebeam.ebeam_bdc_te1550,
#     ],
#     "ebeam_gc_te1550": [
#         ebeam.ebeam_gc_te1550,
#     ],
# }

#
#
# EBEAM WAVEGUIDE CONFIGURATIONS
#
#

ne = None
ng = None
nd = None
