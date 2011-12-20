import os
import subprocess

DFROTZ = '/usr/local/bin/dfrotz'

def format_output(output, load, command, save):
    """
    Yeah, it's ugly.
    Big whoop.
    Wanna fight about it?
    """
    lines = filter(lambda l: l and l != '>', output.split('\n'))
    from_line = 5
    to_line = 0
    if command or load:
        from_line += 4
    if load:
        from_line += 2
    if save:
        to_line = -1
    lines = lines[from_line:]
    if to_line:
        lines = lines[:to_line]
    try:
        where_line = lines.pop(0).replace('>', '').strip()
    except IndexError:
        # TODO: there's an off-by-1 here somewhere, investigate
        lines = filter(lambda l: l and l != '>', output.split('\n'))
        lines = lines[:to_line]
        return lines[-1].replace('>', '').strip()
    where_parts = where_line.split('    ')
    if command and not len(where_parts) > 1:
        # no where line
        lines.insert(0, where_parts[0])
        return ' '.join(lines)
    else:
        return '[%s] %s' % (where_parts[0], ' '.join(lines))

def execute(game_path, command=None, save_path=None):
    args = [DFROTZ, game_path]
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    load = save_path and os.path.exists(save_path)
    save = save_path is not None

    lines = []
    if load:
        # load previously saved game
        lines.extend([
            'restore',
            save_path,
        ])
    if command:
        lines.append(command)
    if save:
        lines.extend([
            'save',
            save_path,
        ])
        if load:
            # confirm overwrite
            lines.append('y')

    if lines:
        output, _ = proc.communicate(input='\n'.join(lines) + '\n')
    else:
        output, _ = proc.communicate()

    return format_output(output, load, command is not None, save)

