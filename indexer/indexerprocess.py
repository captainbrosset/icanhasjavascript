import sys
import os

if sys.argv[1] == "-r":
    sys.path += [os.sep.join([sys.argv[2], "model"])]

log_file = open(os.sep.join([sys.argv[2], "logs.txt"]), "a")

try:

    from jsparser import JSFileVisitorHandler
    from visitor import EntitiesVisitor
    from model import update_file_model


    def index_file(file_name, file_content=None):
        log_file.write("Parsing " + file_name + "\n")
        if not file_content:
            file_content = open(file_name).read()

        visitor_handler = JSFileVisitorHandler(file_content)
        visitor = EntitiesVisitor()
        visitor_handler.add_visitor(visitor)
        try:
            visitor_handler.visit()
            update_file_model(file_name, visitor.functions + visitor.variables)
        except Exception as parsing_error:
            log_file.write(parsing_error.message + " " + str(parsing_error.args) + "\n")


    def get_javascript_files_in_directory(source_dir):
        fileList = []

        for root, subFolders, files in os.walk(source_dir):
            for file in files:
                if file[-3:] == ".js":
                    fileList.append(os.path.join(root, file))

        return fileList


    if __name__ == "__main__" and len(sys.argv) == 5:

        type_of_command = sys.argv[3]
        file_or_dir_name = sys.argv[4]

        if type_of_command == "-f":
            index_file(file_or_dir_name)

        elif type_of_command == "-d":
            files = get_javascript_files_in_directory(file_or_dir_name)
            for file in files:
                index_file(file)

except Exception as e:
    log_file.write(str(e) + "\n")