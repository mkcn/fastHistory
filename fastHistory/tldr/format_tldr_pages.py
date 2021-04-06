import os
import re

FOLDER_TLDR_PAGES = "pages/"
PAGE_EXAMPLE_DESC_CHAR = "-"


def remove_brackets_from_str(line_to_clean):
    if '[' in line_to_clean and ']' in line_to_clean:
        obi = line_to_clean.index('[')
        cbi = line_to_clean.index(']')
        if obi == cbi - 2:
            line_to_clean = line_to_clean[:obi] + line_to_clean[obi + 1] + line_to_clean[obi + 2 + 1:]
            return remove_brackets_from_str(line_to_clean)
        else:
            return line_to_clean
    else:
        return line_to_clean


for root, dirs, fnames in os.walk(FOLDER_TLDR_PAGES):
    for fname in fnames:
        read_lines = []
        modified = False

        if not fname.endswith(".md"):
            continue

        fnamein = os.path.join(root, fname)
        fnameout = os.path.join(root, fname) + ".tmp"

        print("file: %s" % fnamein)

        fin = open(fnamein, "r")
        fout = open(fnameout, "w")

        for line in fin:
            # step 0: strip
            line = line.strip()
            # step 1: remove empty line
            if line == "":
                continue

            # step 2: check if contain "[a]" flag syntax and replace it
            first_char = line[0]

            if first_char is PAGE_EXAMPLE_DESC_CHAR:
                line = remove_brackets_from_str(line)
                # step 3: remove ':' char from end of line
                last_char = line[-1]
                if last_char == ":":
                    line = line[:-1]
            read_lines.append(line + '\n')

        fin.close()
        fout.writelines(read_lines)
        fout.truncate()
        fout.close()

        os.remove(fnamein)
        os.rename(fnameout, fnamein)
