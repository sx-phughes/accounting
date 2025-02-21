from patrick_functions.TempDir import TempDir
import shutil, os
import pandas as pd

class TpIcapFile(object):
    def __init__(self, file_path: str):
        self.f_path = file_path
        with TempDir('./Temp'):
            shutil.copyfile(self.f_path, './Temp/' + self.f_path.split('/')[-1])
            text_lines = []
            
            with open('./Temp/' + self.f_path.split('/')[-1], 'r') as f:
                recording = False
                
                for line in f:
                    
                    if '<html' in line:
                        recording = True
                
                    if recording:
                        text_lines.append(line)
                    
                    if '</html>' in line:
                        recording = False
                        break
            
            new_lines = []
            
            # Need to remove the = sign line breaks
            # Set up a list of lines to skip bc these will be joined to the prior line
            i_to_skip = []
            # Iterate through each of the lines of text
            for i in range(len(text_lines)):
                
                # If the line is in the list of lines to skip, skip it
                if i in i_to_skip:
                    continue
                
                # Decide if current line is broken or not
                broken_line = self.is_broken_line(text_lines[i])
                
                # Empty list for broken lines - this can be reset each time. All joining will be done in
                # this iteration.
                
                # if the line is broken, set up a counter and a list of lines to join
                # else, list of lines to join is empty and will continue to next iteration
                if broken_line:
                    
                    lines_to_join = [text_lines[i]]
                    next_i = i + 1
                    
                    # While we have a broken line indicator, add the next line to the list,
                    # Set the current value of i to the initial i + 1
                    # Increment the next_i variable
                    # We need to determine if we need to keep chaining lines
                    # Add the second line to the list of lines to join and the i to i's to skip
                    # Redefine the broken_line for the i after that
                    # if not broken, add the end of the current chain of lines and end
                    while broken_line:
                        
                        curr_i = next_i
                        next_i += 1
                        
                        # Append the next line
                        lines_to_join.append(text_lines[curr_i])
                        i_to_skip.append(curr_i)
                        
                        # Test if next line is broken
                        broken_line = self.is_broken_line(text_lines[next_i])
                        
                        if not broken_line:
                            lines_to_join.append(text_lines[next_i])
                            i_to_skip.append(next_i)
                else:
                    lines_to_join = []
                
                # If we do have a list of lines to join:
                if len(lines_to_join) > 0:
                    
                    # Clean the lines of the \n and the final = sign
                    clean_lines = [i.replace('\n') for i in lines_to_join]
                    no_equals = [i[-1] for i in clean_lines if len(i) == 76 and i[-1] == '=']
                    
                    # Join the line
                    full_line = ''.join(no_equals)
                    
                    # Reset the value of the line to the new, full line
                    new_lines.append(full_line)
                else:
                    new_lines.append(text_lines[i])
                
            
            # After fully iterating through the lines, we need to remove the broken middles and ends. These are
            # stored in the i_to_skip collected as the lines were identified
            
            # Create a list of the values of the lines to remove - can't use indexes here as they will change
            # with each removal
            # vals_to_remove = [text_lines[i] for i in i_to_skip]
            # for val in vals_to_remove:
            #     text_lines.remove(val)
                
                
                    
            # Rejoin the full text                
            full_text = ''.join(text_lines)
            
            # Remove the stupid 3D things
            full_text = full_text.replace('3D', '')
            
            # write it to an html file
            with open('./' + 'new_html.html', 'w') as f:
                f.write(full_text)
                
    def is_broken_line(self, line: str) -> bool:
        clean_line = line.replace('\n','')
        if len(line) == 76 and line[-1] == '=':
            return True
        else:
            return False
        
                
            
            

TpIcapFile('C:/gdrive/Shared drives/accounting/Payables/2024/202410/Broker Invoices/Chapdelaine - SIMT_CHI_CE-36293U-ESO-0924.xls')