import argparse
import logging

from dataclasses import dataclass
from keycodes import modifier_codes, key_codes, shifted_key_codes

@dataclass
class KeyStroke:
    raw: int
    
    def __post_init__(self) -> None:
        self.key_code = self.raw[0]
        self.modifier = self.raw[1]

@dataclass
class DuckyLine:
    keystrokes: list

    def __post_init__(self) -> None:
        decoded = "" # What can I say, I love string builders
        # Let's deal with 
        if len(self.keystrokes) == 1 and not self.keystrokes[0].key_code == 0x00:
            logging.debug(f"Modifier with a single keypress found (Raw Data {self.keystrokes[0]})")
            keystroke = self.keystrokes[0]
            if keystroke.modifier == 0x01 or keystroke.modifier == 0x10:
                decoded += "CTRL "
            elif keystroke.modifier == 0x08 or keystroke.modifier == 0x80:
                decoded += "GUI "
            elif keystroke.modifier == 0x02 or keystroke.modifier == 0x20:
                decoded += "SHIFT "
            elif keystroke.modifier == 0x04 or keystroke.modifier == 0x40:
                decoded += "ALT "
            elif keystroke.modifier == 0x05 or keystroke.modifier == 0x50:
                decoded += "CTRL-ALT "
            elif keystroke.modifier == 0x03 or keystroke.modifier == 0x30:
                decoded += "CTRL-SHIFT "
            elif keystroke.modifier == 0x00 and not keystroke.key_code == 0x28:
                decoded += "STRING "
        elif self.keystrokes[0].modifier == 0x00 or self.keystrokes[0].modifier == 0x02:
            logging.debug(f"Building Multicharacter String")
            decoded += "STRING "
        elif self.keystrokes[0].key_code == 0x00:
            logging.debug("Delay Detected")
            decoded += "DELAY "
            decoded += str(sum([int(_.modifier) for _ in self.keystrokes]))
        for keystroke in self.keystrokes:
            if decoded.startswith("STRING ") and keystroke.key_code == 0x2c: # Make Spaces Pretty
                decoded += " "
            elif keystroke.modifier == 0x02:
                decoded += shifted_key_codes[keystroke.key_code]
            elif decoded.startswith("DELAY "):
                pass
            else:
                decoded += key_codes[keystroke.key_code]
        self.decoded_line = decoded

    def __repr__(self) -> str:
        return self.decoded_line

    def __str__(self) -> str:
        return self.decoded_line


@dataclass
class DuckyScript:
    keystrokes: list

    def __post_init__(self) -> None:
        lines = []
        current_position = 0
        current_line = []
        # We are going to iterate over all the Halfwords (represented by Keystrokes) from the input file
        while current_position < len(self.keystrokes):
            current_keystroke = self.keystrokes[current_position]
            # Let us handle 'regular' keystrokes
            if current_keystroke.key_code >= 0x04: # Checking for likely valid keystrokes
                # We need to snag raw ENTERs right away
                if current_keystroke.key_code == 0x28 and current_keystroke.modifier == 0x00:
                    current_line.append(current_keystroke)
                    lines.append(DuckyLine(current_line))
                    current_line = []
                elif current_keystroke.modifier == 0x00 or current_keystroke.modifier == 0x02: # Checking for Upper and Lowercase Letters
                    current_line.append(current_keystroke)
                    if not current_position == len(self.keystrokes) - 1: # Make sure we are not at EOF
                        next_keystroke = self.keystrokes[current_position+1]
                        # If the next character doesn't look like it is part of a multi halfword string, go ahead and decode the line
                        if not (next_keystroke.key_code >= 0x04 and (next_keystroke.modifier == 0x00 or next_keystroke.modifier == 0x02) and not next_keystroke.key_code == 0x28):
                            lines.append(DuckyLine(current_line))
                            current_line = []
                    else: 
                        # This captures if there is a SHIFT and a Single input at the end of the file
                        lines.append(DuckyLine(current_line))
                        current_line = []
                elif current_keystroke.modifier in modifier_codes: # Looking for MOD + Keystroke Inputs
                    current_line.append(current_keystroke)
                    lines.append(DuckyLine(current_line))
                    current_line = []
            # Let us handle delays
            elif current_keystroke.key_code == 0x00: 
                current_line.append(current_keystroke)
                if not current_position == len(self.keystrokes) - 1: # Make sure we are not at EOF
                    next_keystroke = self.keystrokes[current_position+1]
                    if not next_keystroke.key_code == 0x00:
                        logging.debug(f'Captured full delay, sending to DuckyLine, sending {current_line}')
                        lines.append(DuckyLine(current_line))
                        current_line = []
            current_position += 1
        self.decoded_lines = lines

    def analyze(self):
        analysis = """\n\nMallard Analysis and Commentary
================================\n"""
        for decoded_line in self.decoded_lines:
            original_line = str(decoded_line)
            decoded_line_str = str(decoded_line).lower()
            if "gui space" in decoded_line_str:
                analysis += f"Spotlight opened ({original_line}) - Possible Mac Attack\n"
            if "gui r" in decoded_line_str:
                analysis += f"Run opened ({original_line}) - Possible Windows Attack\n"
            if "powershell" in decoded_line_str:
                analysis += f"Powershell invoked ({original_line}) - Possible Windows Attack\n"
            if "net user /add" in decoded_line_str:
                analysis += f"User Added ({original_line}) - Possible Windows Attack\n"
            if "net localgroup administrators" in decoded_line_str:
                analysis += f"User Added to administrators group ({original_line}) - Possible Windows Attack\n"
            if "nc " in decoded_line_str or "netcat " in decoded_line_str or "ncat " in decoded_line_str:
                analysis += f"Netcat invoked ({original_line})\n"
        return analysis


    def __str__(self):
        return "\n".join([str(_) for _ in self.decoded_lines])

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', type=str, default='inject.bin', help="The file to decode, default: inject.bin")
    parser.add_argument('--no_analyze', '-A', action='store_true', help="Include this switch to turn off analysis of the duckyfile")
    parser.add_argument('--output_file', '-o', type=str, help="File to save decoded ducky script to.  Default will print duckyfile to screen.")
    parser.add_argument('--analysis_file', type=str, help="Location to output analysis. Default will print analysis to screen.")
    parser.add_argument('--debug', action='store_true', help='Enable Debug Logging.')
    args = parser.parse_args()
    logging.basicConfig(level=logging.ERROR if not args.debug else logging.DEBUG)
    logging.debug('Debug Logging Enabled')
    with open(args.file, 'rb') as inject_file:
        inject_file_bytes = inject_file.read()
    logging.debug(f'Filesize {len(inject_file_bytes)}B')
    keystrokes = []
    while (keystroke := inject_file_bytes[0:2]):
        keystrokes.append(KeyStroke(keystroke))
        inject_file_bytes = inject_file_bytes[2:]
    d = DuckyScript(keystrokes)
    print(d)
    if not args.no_analyze:
        print(d.analyze())

        
if __name__ == '__main__':
    main()