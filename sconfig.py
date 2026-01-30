import configparser
from collections import defaultdict
from pathlib import Path

def get_config_param(config_section, cast_to, param_name):
    try:
        return cast_to(config_section[param_name])
    except:
        return None

def parse_config(config_filename="config.ini", section="", params: list[tuple[str, type]] | None = None):
    return parse_config_with_defaults(config_filename=config_filename, section=section, params=[(item[0], item[1], None) for item in params])

def parse_config_with_fallbacks(config_filename="config.ini", section="", params: list[tuple[str, type, object]] | None = None):
    return parse_config_with_defaults(config_filename=config_filename, section=section, params=params)

def parse_config_with_overrides(config_filename="config.ini", section="", params: list[tuple[str, type, object]] | None = None):
    return parse_config_with_defaults(config_filename=config_filename, section=section, params=params, override=True)

def parse_config_with_defaults(config_filename="config.ini", section="", params: list[tuple[str, type, object]] | None = None, override=False):
    default_result = defaultdict(lambda: None, {n: default for n, _, default in params })

    if params is None or len(params) <= 0 or section == "":
        return default_result

    config = configparser.ConfigParser()

    config_path = Path(config_filename)

    if not config_path.is_file():
        return default_result
    else:
        config.read(config_filename)

        try:
            import_section = config[section]
        except:
            return default_result

        results = defaultdict()

        for parameter in params:
            param_name = parameter[0]
            param_type = parameter[1]
            param_default = parameter[2]

            config_param = get_config_param(config_section=import_section, cast_to=param_type, param_name=param_name)

            if override:
                if param_default is not None:
                    cast_variable = param_default
                else:
                    cast_variable = config_param
            else:
                if config_param is not None:
                    cast_variable = config_param
                else:
                    cast_variable = param_default

            results[param_name] = cast_variable

        return results