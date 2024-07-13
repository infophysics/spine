"""Construct a analysis script module class from its name."""

from spine.utils.factory import module_dict, instantiate

from . import script

# Build a dictionary of available calibration modules
ANA_DICT = {}
ANA_DICT.update(**module_dict(script))


def ana_script_factory(name, cfg, parent_path=''):
    """Instantiates an analyzer module from a configuration dictionary.

    Parameters
    ----------
    name : str
        Name of the analyzer module
    cfg : dict
        Post-processor module configuration
    parent_path : str
        Path to the parent directory of the main analysis configuration. This
        allows for the use of relative paths in the analyzers.

    Returns
    -------
    object
         Initialized analyzer object
    """
    # Provide the name to the configuration
    cfg['name'] = name

    # Instantiate the analysis script module
    return instantiate(ANA_DICT, cfg)
