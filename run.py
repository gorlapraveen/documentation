import requests, json, os, sys, base64, time, cgi
from collections import OrderedDict
import plotly.plotly as py
import plotly.exceptions
from plotly.graph_objs import *  # for exec statements
import plotly.utils as utils
from exceptions import OSError

total_examples = 0
example_count = 0
ids = {}
processed_ids = set()

### auto-generated file stuff ###
# auto_dir = 'auto-docs'  # where we keep any autogenerated content
# auto_root = 'auto-docs'
# doc_dir = os.path.join(auto_dir, 'api')  # the main page for all documentation
# image_dir = os.path.join(auto_dir, 'images')
# exceptions_dir = os.path.join(auto_dir, 'exceptions')
# test_dir = os.path.join(auto_dir, 'test_executables')
pre_book_file = 'pre-book.json'

### hard-coded file stuff ###
hard_coded_dir = 'hard-coded'
config_file = 'config.json'
model_file = 'model.json'
url_file = 'url.json'
image_file = 'image.png'
code_file = 'code.txt'

### keys that are OK to go into final pre_book save ###
leaf_keys = ["config", "is_leaf", "image", "id", "url", "path", "exception",
             "complete", "private"]
branch_keys = ["config", "is_leaf", "id", "path", "subsections",
               "has_thumbnail"]

### meta-config information ###
meta_config_info = ['languages', 'name', 'description', 'tags',
                    'relative_url', 'order', 'private']

### sign in stuff: each user has a 'un' and 'ak' ###
## users ##
# tester, julia, matlab, python, r, node, publisher
with open('users.json') as f:
    users = json.load(f)

with open('dirs.json') as f:
    dirs = json.load(f)

if os.path.exists(pre_book_file):
    with open(pre_book_file) as f:
        previous_pre_book = json.load(f)
        try:
            previously_processed_ids = set(previous_pre_book['processed_ids'])
        except KeyError:
            previously_processed_ids = set()

py.sign_in(users['tester']['un'], users['tester']['ak'])

### server stuff ###
translator_server = "https://plot.ly/translate_figure/"

### style stuff ###
lines_between_sections = 2

### define config_requirements ###
requirements = dict(
    subsection=dict(
        name=basestring,
        has_thumbnail=bool
    ),
    example=dict(
        name=basestring,
        languages=list
    )
)

### define commands to run with, can be combined with '+' (e.g., code+urls) ###
commands = ['code', 'urls', 'clean']

### define supported languages ###
languages = ['python', 'julia', 'matlab', 'r', 'node', 'ggplot', 'matplotlib']

### define extensions for executable code ###
lang_to_ext = dict(python='py',
                   julia='jl',
                   matlab='m',
                   r='r',
                   node='js',
                   ggplot='r',
                   matplotlib='py')
ext_to_lang = dict(py='python',
                   jl='julia',
                   m='matlab',
                   r='r',
                   js='node',
                   gg='ggplot',
                   mpl='matplotlib')

### define imports ###
imports = dict(
    python="import plotly.plotly as py\nfrom plotly.graph_objs import *",
    matlab="",
    r="library(plotly)",
    julia="using Plotly",
    node=""
)

### define sign in ###
sign_in = {
    'documentation': dict(
        python=
            "py.sign_in({{% if username %}}\"{{{{username}}}}\""
            "{{% else %}}'{un}'{{% endif %}}, "
            "{{% if api_key %}}\"{{{{api_key}}}}\""
            "{{% else %}}'{ak}'{{% endif %}})".format(**users['python']),
        matlab=
            "signin({{% if username %}}'{{{{username}}}}'"
            "{{% else %}}'{un}'{{% endif %}}, "
            "{{% if api_key %}}'{{{{api_key}}}}'"
            "{{% else %}}'{ak}'{{% endif %}})".format(**users['matlab']),
        r=
            "p <- plotly(username={{% if username %}}\"{{{{username}}}}\""
            "{{% else %}}'{un}'{{% endif %}}, "
            "key={{% if api_key %}}\"{{{{api_key}}}}\""
            "{{% else %}}'{ak}'{{% endif %}})".format(**users['r']),
        julia=
            "Plotly.signin({{% if username %}}\"{{{{username}}}}\""
            "{{% else %}}\"{un}\"{{% endif %}}, "
            "{{% if api_key %}}\"{{{{api_key}}}}\""
            "{{% else %}}\"{ak}\"{{% endif %}})".format(**users['julia']),
        node=
            "var plotly = require('plotly')("
            "{{% if username %}}'{{{{username}}}}'"
            "{{% else %}}'{un}'{{% endif %}},"
            "{{% if api_key %}}'{{{{api_key}}}}'"
            "{{% else %}}'{ak}'{{% endif %}});".format(**users['node']),
        ggplot=
            "p <- plotly(username={{% if username %}}\"{{{{username}}}}\""
            "{{% else %}}'{un}'{{% endif %}}, "
            "key={{% if api_key %}}\"{{{{api_key}}}}\""
            "{{% else %}}'{ak}'{{% endif %}})".format(**users['r']),
        matplotlib=
            "py.sign_in({{% if username %}}\"{{{{username}}}}\""
            "{{% else %}}'{un}'{{% endif %}}, "
            "{{% if api_key %}}\"{{{{api_key}}}}\""
            "{{% else %}}'{ak}'{{% endif %}})".format(**users['python']),
    ),
    'execution': dict(
        python="py.sign_in('{un}', '{ak}')".format(**users['tester']),
        matlab="signin('{un}', '{ak}')".format(**users['tester']),
        r="p <- plotly(username='{un}', key='{ak}')".format(**users['tester']),
        julia='using Plotly\nPlotly.signin("{un}", "{ak}")'
              ''.format(**users['tester']),
        node="var plotly = require('plotly')('{un}', '{ak}')"
             "".format(**users['tester']),
        ggplot="p <- plotly(username='{un}', key='{ak}')"
               "".format(**users['tester']),
        matplotlib="py.sign_in('{un}', '{ak}')".format(**users['tester']),
    )
}


def get_command_list():
    try:
        arg1 = sys.argv[1]
        command_list = arg1.split('+')
        for command in command_list:
            if command not in commands:
                raise Exception()
    except:
        command_list = None
    if not command_list:
        print "usage:\n"\
              "python run.py command examplename\n"\
              "python run.py command\n",\
              "python run.py command1+command2+command3 examplename\n"\
              "python run.py command1+command2+command3\n"
        print 'commands:', commands
        sys.exit(0)
    else:
        return command_list


def get_keepers():
    keepers = []
    while len(sys.argv) > 2:
        keepers += [sys.argv.pop()]
    return keepers


def clean():
    """removes ENTIRE doc_dir directory, careful!"""
    def clean_directory(directory):
        for name in os.listdir(directory):
            full_name = os.path.join(directory, name)
            if os.path.isdir(full_name):
                clean_directory(full_name)
                os.rmdir(full_name)
            else:
                os.remove(full_name)
    if os.path.exists(dirs['run']):
        clean_directory(dirs['run'])
    if os.path.exists(dirs['exceptions']):
        clean_directory(dirs['exceptions'])
    if os.path.exists(pre_book_file):
        os.remove(pre_book_file)


def write_pre_book(section_dir, keepers=None):
    """
    1. for each directory, if there are sub-directories: recurse
    2. if no sub-directories, and name in keepers, keep!
    """
    section_dict = dict()
    subsections = [child for child in os.listdir(section_dir)
                   if os.path.isdir(os.path.join(section_dir, child))]
    files = [child for child in os.listdir(section_dir)
             if not os.path.isdir(os.path.join(section_dir, child))
             and child != config_file]
    if subsections and files:
        raise Exception("found a directory that has BOTH subsections AND "
                        "files in '{}'".format(section_dir))
    elif subsections:
        subsections_dict = dict()
        for subsection_name in subsections:
            subsection_dir = os.path.join(section_dir, subsection_name)
            subsection_dict = write_pre_book(subsection_dir, keepers)
            if subsection_dict:
                subsections_dict[subsection_name] = subsection_dict
        if subsections_dict:
            section_dict['subsections'] = subsections_dict
            section_dict['is_leaf'] = False
    elif files:
        id = section_dir.split(os.path.sep)[-1]
        if id in ids:
            raise Exception(
                "identical ids found in '{}' and '{}'. Example folders must "
                "have unique names.".format(ids[id], section_dir)
            )
        else:
            ids[id] = section_dir
        if keepers:
            names = section_dir.split(os.path.sep)
            keep = any([True for keeper in keepers if keeper in names])
            if 'new' in keepers:
                if not keep and id not in previously_processed_ids:
                    keep = True
        else:
            keep = True
        if keep:
            section_dict['files'] = {f: os.path.join(section_dir, f)
                                     for f in os.listdir(section_dir)
                                     if f != config_file}
            section_dict['is_leaf'] = True
            global total_examples
            total_examples += 1
    if 'files' in section_dict or 'subsections' in section_dict:
        config_path = os.path.join(section_dir, config_file)
        config = validate_and_get_config(config_path, section_dict['is_leaf'])
        section_dict['config'] = config
        section_dict['path'] = section_dir
        section_dict['id'] = section_dir.split(os.path.sep)[-1]
        return section_dict


def validate_and_get_config(config_path, is_leaf):
    try:
        with open(config_path) as f:
            config = json.load(f)
    except ValueError:
        raise ValueError("invalid json in '{}'".format(config_path))
    if is_leaf:
        section_type = 'example'
    else:
        section_type = 'subsection'
    for key, val in requirements[section_type].items():
        if key not in config:
            raise KeyError(
                "missing key '{}' in config at location '{}'"
                "".format(key, config_path))
        elif not isinstance(config[key], val):
            raise ValueError(
                "wrong value type for key '{}' in config at location '{}'"
                "".format(key, config_path))
    return config


def validate_example_structure(section):
    if 'subsections' in section:
        for subsection in section['subsections'].values():
            validate_example_structure(subsection)
    elif 'files' in section:
        scripts = [filename for filename in section['files']
                   if filename.split('.')[0] == 'script']
        if len(scripts) > 1:
            raise Exception("more than one script.ext found in '{}'"
                            "".format(section['path']))
        elif scripts and model_file in section:
            raise Exception("script.ext file and model.json found in '{}'"
                            "".format(section['path']))
        elif scripts and url_file in section:
            raise Exception("script.ext file and url.json found in '{}'"
                            "".format(section['path']))
        elif model_file in section and url_file in section:
            raise Exception("model.json and url.json found in '{}'"
                            "".format(section['path']))


def process_pre_book(section, command_list):
    if section['is_leaf']:
        time.sleep(1)
        global example_count, processed_ids
        example_count += 1
        print("\t{} of {}".format(example_count, total_examples)),
        if model_file in section['files']:
            process_model_example(section, command_list)
            processed_ids.add(section['id'])
        elif any(['script' in filename for filename in section['files']]):
            process_script_example(section, command_list)
            processed_ids.add(section['id'])
        elif url_file in section['files']:
            process_url_example(section, command_list)
            processed_ids.add(section['id'])
    else:
        for subsection in section['subsections'].values():
            process_pre_book(subsection, command_list)


def process_model_example(example, command_list):
    """
    1. load model.json file
    2. for each language with 'model' as the *source*...
    3. translate model to language with translator
    4. if save image: save image
    5. if save code: save code
    6. if save url: save url
    """
    print "\tprocessing {} in {}".format(model_file, example['path'])
    example['type'] = 'model'
    try:
        with open(example['files'][model_file]) as f:
            model = json.load(f)
    except KeyError:
        raise KeyError(
            "{} required and could not be found in {}"
            "".format(model_file, example['path']))
    except ValueError:
        raise ValueError(
            "{} required and could not be opened in {}"
            "".format(model_file, example['path']))
    for language in example['config']['languages']:
        code = ""
        if 'init' in example['config'] and example['config']['init']:
            init_file = "init.{}".format(lang_to_ext[language])
            if init_file in example['files']:
                with open(example['files'][init_file]) as f:
                    code += f.read() + "\n"
            else:
                raise Exception(
                    "couldn't find '{}' in '{}'"
                    "".format(init_file, example['path'])
                )
        data = {'json_figure': model,
                'language': language,
                'pretty': True}
        res = requests.get(translator_server, data=json.dumps(data))
        if res.status_code == 200:
            code += res.content
            code = code.replace("<pre>", "").replace("</pre>", "")
        else:
            print "\t\tskipping '{}', bad response from plotly " \
                  "translator!".format(language)
            continue
        code = code.replace('">>>', "").replace('<<<"', "")
        code = code.replace("'>>>", "").replace("<<<'", "")
        if 'append' in example['config'] and example['config']['append']:
            append_file = "append.{}".format(lang_to_ext[language])
            if append_file in example['files']:
                with open(example['files'][append_file]) as f:
                    code += f.read() + "\n"
            else:
                raise Exception(
                    "couldn't find '{}' in '{}'"
                    "".format(append_file, example['path'])
                )
        exec_string = format_code(code, language, example, model, 'execution')
        if language == 'python':
            example['python-exec'] = exec_string
        if 'code' in command_list:
            code_string = format_code(code, language, example, model)
            code_path = save_code(
                code_string, example, language, 'documentation'
            )
            example[language] = code_path
            save_code(exec_string, example, language, 'execution')

    if 'urls' in command_list:
        if 'python-exec' in example:
            exec_locals = exec_python_string(example['python-exec'])
            if 'plot_url' in exec_locals:
                example['url'] = exec_locals['plot_url']
    mark_completeness(example)


def process_script_example(example, command_list):
    """
    1. for each language with 'model' as the *source*...
    2. load script.ext file
    3. if save image: save image
    4. if save code: save code
    5. if save url: save url
    """
    print "\tprocessing scripts in {}".format(example['path'])
    example['type'] = 'script'
    script_file = [fn for fn in example['files'] if 'script' in fn][0]
    language = ext_to_lang[script_file.split('.')[-1]]
    example['config']['languages'] = [language]
    try:
        with open(example['files'][script_file]) as f:
            script = f.read()
    except KeyError:
        raise KeyError(
            "'{}' not found in '{}'".format(script_file, example['path']))
    exec_string = ""
    for line in script.splitlines():
        if line[:6] == sign_in['execution'][language][:6]:  # TODO, better way?
            exec_string += sign_in['execution'][language]
        elif '>>>filename<<<' in line:
            exec_string += line.replace('>>>filename<<<', example['id'])
        else:
            exec_string += line
        exec_string += "\n"
    if language == 'python':
        if 'urls' in command_list:
            exec_locals = exec_python_string(exec_string)
            if 'plot_url' in exec_locals:
                example['url'] = exec_locals['plot_url']
    if 'code' in command_list:
        code_string = exec_string.replace(sign_in['execution'][language],
                                          sign_in['documentation'][language])
        code_string = cgi.escape(code_string)
        code_path = save_code(code_string, example, language, 'documentation')
        example[language] = code_path
        save_code(exec_string, example, language, 'execution')
    mark_completeness(example)
    if not example['complete']:
        save_code(exec_string, example, language, 'exception')


def process_url_example(example, command_list):
    """
    1. for each language with 'url' as the *source*...
    2. translate model to language with translator
    3. if save image: save image
    4. if save code: save code
    """
    print "\tprocessing {} in {}".format(url_file, example['path'])
    example['type'] = 'url'
    try:
        with open(example['files'][url_file]) as f:
            url = json.load(f)['url']
    except ValueError:
        raise ValueError(
            "{} required and could not be opened in {}"
            "".format(url_file, example['path']))
    except KeyError:
        raise KeyError(
            "{} required and could not be found in {}"
            "".format(url_file, example['path']))
    json_resource = "{}.json".format(url)
    res = requests.get(json_resource)
    if res.status_code == 200:
        figure_str = res.content
        figure_str = figure_str.replace("<pre>", "").replace("</pre>", "")
        figure_str = figure_str.replace("<html>", "").replace("</html>", "")
        figure = json.loads(figure_str)
        for language in example['config']['languages']:
            code = ""
            resource = "{}.{}".format(url, lang_to_ext[language])
            res = requests.get(resource)
            if res.status_code == 200:
                code += res.content
                code = code.replace("<pre>", "").replace("</pre>", "")
                code = code.replace("<html>", "").replace("</html>", "")
                exec_string = format_code(
                    code, language, example, figure, 'execution'
                )
                if language == 'python':
                    example['python-exec'] = exec_string
                if 'code' in command_list:
                    code_string = format_code(code, language, example, figure)
                    code_path = save_code(
                        code_string, example, language, 'documentation'
                    )
                    example[language] = code_path
                    save_code(exec_string, example, language, 'execution')
            else:
                print ("\t\tskipping '{}', bad response from "
                       "shareplot_as_code".format(language))
        if 'urls' in command_list:
            if 'python-exec' in example:
                exec_locals = exec_python_string(example['python-exec'])
                if 'plot_url' in exec_locals:
                    example['url'] = exec_locals['plot_url']
            else:
                print ("\t\tcouldn't find python code to process url")
    else:
        print ("\t\tskipping '{}', bad response from shareplot_as_code for "
               ".json".format(example['path']))
    mark_completeness(example)


def save_code(code, example, language, mode):
    if mode == 'documentation':
        example_folder = os.path.join(dirs['run'],
                                      *example['path'].split(os.path.sep)[1:])
        code_folder = os.path.join(example_folder, language)
        code_path = os.path.join(code_folder, code_file)
    elif mode == 'execution':
        code_folder = os.path.join(dirs['run'], dirs['executables'], language)
        filename = "{}.{}".format(example['id'], lang_to_ext[language])
        code_path = os.path.join(code_folder, filename.replace("-", "_"))
    elif mode == 'exception':
        code_folder = os.path.join(dirs['exceptions'], language)
        filename = "{}.{}".format(example['id'], lang_to_ext[language])
        code_path = os.path.join(code_folder, filename.replace("-", "_"))
    else:
        raise Exception("mode: 'execution' | 'documentation' | 'exception'")
    if not os.path.exists(code_folder):
        os.makedirs(code_folder)
    with open(code_path, 'w') as f:
        f.write(code)
    return code_path


def exec_python_string(exec_string):
    """save image to directory by executing python code-string and saving"""
    try:
        exec exec_string
    except:
        print exec_string
        raise
    if 'plot_url' not in locals():
        raise Exception("'plot_url' not found in exec string!")
    return locals()


def format_code(body_string, language, example, figure, mode='documentation'):
    file_import = imports[language]
    file_sign_in = sign_in[mode][language]
    plot_call = get_plot_call(language, figure, example, mode=mode)
    sections = [file_import, file_sign_in, body_string, plot_call]
    sections = [sec for sec in sections if sec]
    code_string = ("\n" * lines_between_sections).join(sections)
    if mode == 'documentation':
        code_string = cgi.escape(code_string)
    return code_string


def get_plot_call(language, figure, example, mode):
    """define strings for actual plot calls

    :rtype : str
    """
    tf_dict = {
        True: dict(
            python='True',
            matlab='true',
            julia='true',
            r='TRUE',
            node='true'
        ),
        False: dict(
            python='False',
            matlab='false',
            julia='false',
            r='FALSE',
            node='false'
        )
    }
    filename = example['path'].split(os.path.sep)[-1]
    try:
        plot_options = example['config']['plot-options']
    except KeyError:
        plot_options = {}
    else:
        if 'world_readable' in plot_options and not plot_options['world_readable']:
            example['private'] = True
    if mode == 'execution':
        plot_options['auto_open'] = False
    if language == 'python':
        string = "plot_url = py.plot("
        if 'layout' in figure:
            string += 'fig, '
        else:
            string += 'data, '
        string += "filename='{}'".format(filename)
        if plot_options:
            for key, val in plot_options.items():
                try:
                    string += ", {}={}".format(key, tf_dict[val][language])
                except KeyError:
                    string += ", {}={}".format(key, val)
        return string + ")"
    elif language == 'matlab':
        string = "response = plotly(data, struct("
        if 'layout' in figure:
            string += "'layout', layout, "
        string += "'filename', '{}'".format(filename)
        string += ", 'fileopt', 'overwrite'"
        if plot_options:
            for key, val in plot_options.items():
                try:
                    string += ", '{}', '{}'".format(key, tf_dict[val][language])
                except KeyError:
                    string += ", '{}', '{}'".format(key, val)
        string += "));"
        string += "\nplot_url = response.url"
        return string
    elif language == 'julia':
        string = "response = Plotly.plot([data], ["
        if 'layout' in figure:
            string += '"layout" => layout, '
        string += '"filename" => "{}"'.format(filename)
        string += ', "fileopt" => "overwrite"'
        if plot_options:
            for key, val in plot_options.items():
                try:
                    string += ', "{}" => "{}"'.format(key,
                                                      tf_dict[val][language])
                except KeyError:
                    string += ', "{}" => "{}"'.format(key, val)
        string += "])"
        string += '\nplot_url = response["url"]'
        return string
    elif language == 'r':
        string = 'response <- p$plotly(data, kwargs=list('
        if 'layout' in figure:
            string += 'layout=layout, '
        string += 'filename="{}"'.format(filename)
        string += ', fileopt="overwrite"'
        if plot_options:
            for key, val in plot_options.items():
                try:
                    string += ', {}="{}"'.format(key, tf_dict[val][language])
                except KeyError:
                    string += ', {}="{}"'.format(key, val)
        string += "))"
        string += '\nurl <- response$url\n'
        string += 'filename <- response$filename'
        return string
    elif language == 'node':
        string = 'var graph_options = {{filename: "{}"'.format(filename)
        string += ', fileopt: "overwrite"'
        if 'layout' in figure:
            string += ', layout: layout'
        if plot_options:
            for key, val in plot_options.items():
                try:
                    string += ', {}: "{}"'.format(key, tf_dict[val][language])
                except KeyError:
                    string += ', {}: "{}"'.format(key, val)
        string += '}'
        string += "\nplotly.plot("
        if 'data' in figure and figure['data']:
            string += "data"
        else:
            string += "[]"
        string += ", graph_options, function (err, msg) {"
        string += "\n    console.log(msg);"
        string += "\n});"
        return string
    else:
        return ''


def mark_completeness(example):
    has_url = 'url' in example
    has_all_languages = all([language in example
                             for language in example['config']['languages']])
    if has_url and has_all_languages:
        example['complete'] = True
    else:
        example['complete'] = False


def trim_pre_book(section):
    section_keys = section.keys()
    if section['is_leaf']:
        for key in section_keys:
            if key not in leaf_keys and key not in languages:
                del section[key]
    else:
        for key in section_keys:
            if key not in branch_keys:
                del section[key]
        for subsection in section['subsections'].values():
            trim_pre_book(subsection)


def save_pre_book(pre_book):
    pre_book['processed_ids'] = list(set.union(processed_ids,
                                          previously_processed_ids))
    try: # todo, where do we want the pre-book-file?
        os.makedirs(dirs['run'])
    except OSError:
        pass
    if os.path.exists(pre_book_file):
        with open(pre_book_file) as f:
            old_pre_book = json.load(f)
        new_pre_book = nested_merge(old_pre_book, pre_book)
        with open(pre_book_file, 'w') as f:
            json.dump(new_pre_book, f, indent=4)
    else:
        with open(pre_book_file, 'w') as f:
            json.dump(pre_book, f, indent=4)


def nested_merge(old, update):
    """
    1. Assumes that branches are the same type!
    2. Doesn't look inside lists! Treats them as a leaf/end/terminal/etc
    """
    new = dict()
    new.update(old)
    if isinstance(update, dict):
        for key, val in update.items():
            if key not in old:
                new[key] = update[key]
            elif isinstance(val, dict):
                new[key] = nested_merge(old[key], val)
            else:
                new[key] = val
    return new


def main():
    command_list = get_command_list()  # TODO unused...
    keepers = get_keepers()
    print "\n\nrunning with commands: {}\n\n".format(command_list)
    if 'clean' in command_list:
        clean()
        command_list.pop(command_list.index('clean'))
    if command_list:
        print "compiling pre-book"
        pre_book = write_pre_book(hard_coded_dir, keepers)
        if pre_book:
            print "validating file structure in examples"
            validate_example_structure(pre_book)
            print "about to get it done."
            process_pre_book(pre_book, command_list)
            print "got it done, cleaning up!"
            trim_pre_book(pre_book)
            print "saving pre_book"
            save_pre_book(pre_book)
        else:
            print "you're filter didn't match a section OR an example. bummer!"

if __name__ == "__main__":
    main()