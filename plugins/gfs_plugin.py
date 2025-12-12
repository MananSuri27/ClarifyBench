from typing import Dict, List, Any, Optional, Tuple, Union
import logging
import copy
from plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

class File:
    def __init__(self, name: str, content: str = "") -> None:
        """
        Initialize a file with a name and optional content.

        Args:
            name (str): The name of the file.
            content (str, optional): The initial content of the file. Defaults to an empty string.
        """
        self.name: str = name
        self.content: str = content
        self._last_modified = None  # We'll use this if needed later

    def _write(self, new_content: str) -> None:
        """
        Write new content to the file and update the last modified time.

        Args:
            new_content (str): The new content to write to the file.
        """
        self.content = new_content

    def _read(self) -> str:
        """
        Read the content of the file.

        Returns:
            content (str): The current content of the file.
        """
        return self.content

    def _append(self, additional_content: str) -> None:
        """
        Append content to the existing file content.

        Args:
            additional_content (str): The content to append to the file.
        """
        self.content += additional_content

    def __repr__(self):
        return f"<<File: {self.name}, Content: {self.content}>>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, File):
            return False
        return self.name == other.name and self.content == other.content


class Directory:
    def __init__(self, name: str, parent: Optional["Directory"] = None) -> None:
        """
        Initialize a directory with a name.

        Args:
            name (str): The name of the directory.
        """
        self.name: str = name
        self.parent: Optional["Directory"] = parent
        self.contents: Dict[str, Union["File", "Directory"]] = {}

    def _add_file(self, file_name: str, content: str = "") -> None:
        """
        Add a new file to the directory.

        Args:
            file_name (str): The name of the file.
            content (str, optional): The content of the new file. Defaults to an empty string.
        """
        if file_name in self.contents:
            raise ValueError(
                f"File '{file_name}' already exists in directory '{self.name}'."
            )
        new_file = File(file_name, content)
        self.contents[file_name] = new_file

    def _add_directory(self, dir_name: str) -> None:
        """
        Add a new subdirectory to the directory.

        Args:
            dir_name (str): The name of the subdirectory.
        """
        if dir_name in self.contents:
            raise ValueError(
                f"Directory '{dir_name}' already exists in directory '{self.name}'."
            )
        new_dir = Directory(dir_name, self)
        self.contents[dir_name] = new_dir

    def _get_item(self, item_name: str) -> Union["File", "Directory", None]:
        """
        Get an item (file or subdirectory) from the directory.

        Args:
            item_name (str): The name of the item to retrieve.

        Returns:
            item (any): The retrieved item or None if it does not exist.
        """
        return self.contents.get(item_name)

    def _list_contents(self) -> List[str]:
        """
        List the names of all contents in the directory.

        Returns:
            contents (List[str]): A list of names of the files and subdirectories in the directory.
        """
        return list(self.contents.keys())

    def __repr__(self):
        return f"<Directory: {self.name}, Parent: {self.parent.name if self.parent else None}, Contents: {self.contents}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Directory):
            return False
        return self.name == other.name and self.contents == other.contents


from typing import Dict, List, Any, Optional, Tuple, Union
import logging
import copy

logger = logging.getLogger(__name__)

class File:
    def __init__(self, name: str, content: str = "") -> None:
        """
        Initialize a file with a name and optional content.

        Args:
            name (str): The name of the file.
            content (str, optional): The initial content of the file. Defaults to an empty string.
        """
        self.name: str = name
        self.content: str = content
        self._last_modified = None  # We'll use this if needed later

    def _write(self, new_content: str) -> None:
        """
        Write new content to the file and update the last modified time.

        Args:
            new_content (str): The new content to write to the file.
        """
        self.content = new_content

    def _read(self) -> str:
        """
        Read the content of the file.

        Returns:
            content (str): The current content of the file.
        """
        return self.content

    def _append(self, additional_content: str) -> None:
        """
        Append content to the existing file content.

        Args:
            additional_content (str): The content to append to the file.
        """
        self.content += additional_content

    def __repr__(self):
        return f"<<File: {self.name}, Content: {self.content}>>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, File):
            return False
        return self.name == other.name and self.content == other.content


class Directory:
    def __init__(self, name: str, parent: Optional["Directory"] = None) -> None:
        """
        Initialize a directory with a name.

        Args:
            name (str): The name of the directory.
        """
        self.name: str = name
        self.parent: Optional["Directory"] = parent
        self.contents: Dict[str, Union["File", "Directory"]] = {}

    def _add_file(self, file_name: str, content: str = "") -> None:
        """
        Add a new file to the directory.

        Args:
            file_name (str): The name of the file.
            content (str, optional): The content of the new file. Defaults to an empty string.
        """
        if file_name in self.contents:
            raise ValueError(
                f"File '{file_name}' already exists in directory '{self.name}'."
            )
        new_file = File(file_name, content)
        self.contents[file_name] = new_file

    def _add_directory(self, dir_name: str) -> None:
        """
        Add a new subdirectory to the directory.

        Args:
            dir_name (str): The name of the subdirectory.
        """
        if dir_name in self.contents:
            raise ValueError(
                f"Directory '{dir_name}' already exists in directory '{self.name}'."
            )
        new_dir = Directory(dir_name, self)
        self.contents[dir_name] = new_dir

    def _get_item(self, item_name: str) -> Union["File", "Directory", None]:
        """
        Get an item (file or subdirectory) from the directory.

        Args:
            item_name (str): The name of the item to retrieve.

        Returns:
            item (any): The retrieved item or None if it does not exist.
        """
        return self.contents.get(item_name)

    def _list_contents(self) -> List[str]:
        """
        List the names of all contents in the directory.

        Returns:
            contents (List[str]): A list of names of the files and subdirectories in the directory.
        """
        return list(self.contents.keys())

    def __repr__(self):
        return f"<Directory: {self.name}, Parent: {self.parent.name if self.parent else None}, Contents: {self.contents}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Directory):
            return False
        return self.name == other.name and self.contents == other.contents


class GorillaFileSystem:
    def __init__(self) -> None:
        """
        Initialize the Gorilla file system with a root directory
        """
        self.root = Directory("/", None)
        self._current_dir = self.root
        self._api_description = "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc."

    def _load_scenario(self, scenario: dict) -> None:
        """
        Load a scenario into the file system.

        Args:
            scenario (dict): The scenario to load.
        """
        # Reset the filesystem
        self.root = Directory("/", None)
        
        if "root" in scenario:
            root_contents = scenario["root"]
            # Get the first (and only) key in root
            root_dir_name = next(iter(root_contents.keys()))
            root_dir = Directory(root_dir_name, None)
            self.root = root_dir
            
            # Load the directory structure
            self._load_directory(
                root_contents[root_dir_name]["contents"], root_dir
            )
        
        self._current_dir = self.root

    def _load_directory(
        self, current: dict, parent: Optional[Directory] = None
    ) -> Directory:
        """
        Load a directory and its contents from a dictionary.

        Args:
            current (dict): The dictionary representing the directory's contents.
            parent (Directory, optional): The parent directory. Defaults to None.

        Returns:
            Directory: The loaded directory with its contents.
        """
        for item_name, item_data in current.items():
            if item_data["type"] == "directory":
                new_dir = Directory(item_name, parent)
                self._load_directory(item_data["contents"], new_dir)
                parent.contents[item_name] = new_dir
            elif item_data["type"] == "file":
                content = item_data["content"]
                new_file = File(item_name, content)
                parent.contents[item_name] = new_file
        
        return parent

    def pwd(self):
        """
        Return the current working directory path.
        Args:
            None
        Returns:
            current_working_directory (str): The current working directory path.

        """
        path = []
        dir = self._current_dir
        while dir is not None and dir.name != self.root.name:
            path.append(dir.name)
            dir = dir.parent
        
        # Handle the root case specially
        if not path and self._current_dir == self.root:
            return {"current_working_directory": f"/{self._current_dir.name}"}
            
        return {"current_working_directory": "/" + "/".join(reversed(path))}

    def ls(self, a: bool = False) -> Dict[str, List[str]]:
        """
        List the contents of the current directory.

        Args:
            a (bool): [Optional] Show hidden files and directories. Defaults to False.

        Returns:
            current_directory_content (List[str]): A list of the contents of the specified directory.
        """
        contents = self._current_dir._list_contents()
        if not a:
            contents = [item for item in contents if not item.startswith(".")]
        return {"current_directory_content": contents}

    def cd(self, folder: str) -> Union[None, Dict[str, str]]:
        """
        Change the current working directory to the specified folder.

        Args:
            folder (str): The folder of the directory to change to. You can only change one folder at a time.

        Returns:
            current_working_directory (str): The new current working directory path.
        """
        # Handle navigating to the parent directory with "cd .."
        if folder == "..":
            if self._current_dir.parent:
                self._current_dir = self._current_dir.parent
            elif self.root == self._current_dir:
                return {"error": "Current directory is already the root. Cannot go back."}
            else:
                return {"error": "cd: ..: No such directory"}
            return {"current_working_directory": self._current_dir.name}

        # Handle absolute or relative paths
        target_dir = self._navigate_to_directory(folder)
        if isinstance(target_dir, dict):  # Error condition check
            return {
                "error": f"cd: {folder}: No such directory. You cannot use path to change directory."
            }
        self._current_dir = target_dir
        return {"current_working_directory": target_dir.name}

    def _validate_file_or_directory_name(self, dir_name: str) -> bool:
        if any(c in dir_name for c in '|/\\?%*:"><'):
            return False
        return True

    def mkdir(self, dir_name: str) -> Union[None, Dict[str, str]]:
        """
        Create a new directory in the current directory.

        Args:
            dir_name (str): The name of the new directory at current directory. You can only create directory at current directory.
        """
        if not self._validate_file_or_directory_name(dir_name):
            return {
                "error": f"mkdir: cannot create directory '{dir_name}': Invalid character"
            }
        if dir_name in self._current_dir.contents:
            return {"error": f"mkdir: cannot create directory '{dir_name}': File exists"}

        self._current_dir._add_directory(dir_name)
        return None

    def touch(self, file_name: str) -> Union[None, Dict[str, str]]:
        """
        Create a new file of any extension in the current directory.

        Args:
            file_name (str): The name of the new file in the current directory. file_name is local to the current directory and does not allow path.
        """
        if not self._validate_file_or_directory_name(file_name):
            return {"error": f"touch: cannot touch '{file_name}': Invalid character"}

        if file_name in self._current_dir.contents:
            return {"error": f"touch: cannot touch '{file_name}': File exists"}

        self._current_dir._add_file(file_name)
        return None

    def echo(
        self, content: str, file_name: Optional[str] = None
    ) -> Union[Dict[str, str], None]:
        """
        Write content to a file at current directory or display it in the terminal.

        Args:
            content (str): The content to write or display.
            file_name (str): [Optional] The name of the file at current directory to write the content to. Defaults to None.

        Returns:
            terminal_output (str): The content if no file name is provided, or None if written to file.
        """
        if file_name is None:
            return {"terminal_output": content}
        if not self._validate_file_or_directory_name(file_name):
            return {"error": f"echo: cannot touch '{file_name}': Invalid character"}

        if file_name:
            if file_name in self._current_dir.contents:
                self._current_dir._get_item(file_name)._write(content)
            else:
                self._current_dir._add_file(file_name, content)
        else:
            return {"terminal_output": content}

    def cat(self, file_name: str) -> Dict[str, str]:
        """
        Display the contents of a file of any extension from currrent directory.

        Args:
            file_name (str): The name of the file from current directory to display. No path is allowed.

        Returns:
            file_content (str): The content of the file.
        """
        if not self._validate_file_or_directory_name(file_name):
            return {"error": f"cat: '{file_name}': Invalid character"}

        if file_name in self._current_dir.contents:
            item = self._current_dir._get_item(file_name)
            if isinstance(item, File):
                return {"file_content": item._read()}
            else:
                return {"error": f"cat: {file_name}: Is a directory"}
        else:
            return {"error": f"cat: {file_name}: No such file or directory"}

    def find(self, path: str = ".", name: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Find any file or directories under specific path that contain name in its file name.

        This method searches for files of any extension and directories within a specified path that match
        the given name. If no name is provided, it returns all files and directories
        in the specified path and its subdirectories.
        Note: This method performs a recursive search through all subdirectories of the given path.

        Args:
            path (str): The directory path to start the search. Defaults to the current directory (".").
            name (str): [Optional] The name of the file or directory to search for. If None, all items are returned.

        Returns:
            matches (List[str]): A list of matching file and directory paths relative to the given path.

        """
        matches = []
        target_dir = self._current_dir

        def recursive_search(directory: Directory, base_path: str) -> None:
            for item_name, item in directory.contents.items():
                item_path = f"{base_path}/{item_name}"
                if name is None or name in item_name:
                    matches.append(item_path)
                if isinstance(item, Directory):
                    recursive_search(item, item_path)

        recursive_search(target_dir, path.rstrip("/"))
        return {"matches": matches}

    def wc(self, file_name: str, mode: str = "l") -> Dict[str, Union[int, str]]:
        """
        Count the number of lines, words, and characters in a file of any extension from current directory.

        Args:
            file_name (str): Name of the file of current directory to perform wc operation on.
            mode (str): Mode of operation ('l' for lines, 'w' for words, 'c' for characters).

        Returns:
            count (int): The count of the number of lines, words, or characters in the file.
            type (str): The type of unit we are counting. [Enum]: ["lines", "words", "characters"]
        """
        if mode not in ["l", "w", "c"]:
            return {"error": f"wc: invalid mode '{mode}'"}

        if file_name in self._current_dir.contents:
            file = self._current_dir._get_item(file_name)
            if isinstance(file, File):
                content = file._read()

                if mode == "l":
                    line_count = len(content.splitlines())
                    return {"count": line_count, "type": "lines"}

                elif mode == "w":
                    word_count = len(content.split())
                    return {"count": word_count, "type": "words"}

                elif mode == "c":
                    char_count = len(content)
                    return {"count": char_count, "type": "characters"}

        return {"error": f"wc: {file_name}: No such file or directory"}

    def sort(self, file_name: str) -> Dict[str, str]:
        """
        Sort the contents of a file line by line.

        Args:
            file_name (str): The name of the file appeared at current directory to sort.

        Returns:
            sorted_content (str): The sorted content of the file.
        """
        if file_name in self._current_dir.contents:
            file = self._current_dir._get_item(file_name)
            if isinstance(file, File):
                content = file._read()
                sorted_content = "\n".join(sorted(content.splitlines()))
                return {"sorted_content": sorted_content}

        return {"error": f"sort: {file_name}: No such file or directory"}

    def grep(self, file_name: str, pattern: str) -> Dict[str, List[str]]:
        """
        Search for lines in a file of any extension at current directory that contain the specified pattern.

        Args:
            file_name (str): The name of the file to search. No path is allowed and you can only perform on file at local directory.
            pattern (str): The pattern to search for.

        Returns:
            matching_lines (List[str]): Lines that match the pattern.
        """
        if file_name in self._current_dir.contents:
            file = self._current_dir._get_item(file_name)
            if isinstance(file, File):
                content = file._read()
                matching_lines = [line for line in content.splitlines() if pattern in line]
                return {"matching_lines": matching_lines}

        return {"error": f"grep: {file_name}: No such file or directory"}

    def du(self, human_readable: bool = False) -> Dict[str, str]:
        """
        Estimate the disk usage of a directory and its contents.

        Args:
            human_readable (bool): If True, returns the size in human-readable format (e.g., KB, MB).

        Returns:
            disk_usage (str): The estimated disk usage.
        """
        def get_size(item: Union[File, Directory]) -> int:
            if isinstance(item, File):
                return len(item._read().encode("utf-8"))
            elif isinstance(item, Directory):
                return sum(get_size(child) for child in item.contents.values())
            return 0

        target_dir = self._current_dir
        total_size = get_size(target_dir)

        if human_readable:
            for unit in ["B", "KB", "MB", "GB", "TB"]:
                if total_size < 1024:
                    size_str = f"{total_size:.2f} {unit}"
                    break
                total_size /= 1024
            else:
                size_str = f"{total_size:.2f} PB"
        else:
            size_str = f"{total_size} bytes"

        return {"disk_usage": size_str}

    def tail(self, file_name: str, lines: int = 10) -> Dict[str, str]:
        """
        Display the last part of a file of any extension.

        Args:
            file_name (str): The name of the file to display. No path is allowed and you can only perform on file at local directory.
            lines (int): The number of lines to display from the end of the file. Defaults to 10.

        Returns:
            last_lines (str): The last part of the file.
        """
        if file_name in self._current_dir.contents:
            file = self._current_dir._get_item(file_name)
            if isinstance(file, File):
                content = file._read().splitlines()

                if lines > len(content):
                    lines = len(content)

                last_lines = content[-lines:]
                return {"last_lines": "\n".join(last_lines)}

        return {"error": f"tail: {file_name}: No such file or directory"}

    def diff(self, file_name1: str, file_name2: str) -> Dict[str, str]:
        """
        Compare two files of any extension line by line at the current directory.

        Args:
            file_name1 (str): The name of the first file in current directory.
            file_name2 (str): The name of the second file in current directorry.

        Returns:
            diff_lines (str): The differences between the two files.
        """
        if (
            file_name1 in self._current_dir.contents
            and file_name2 in self._current_dir.contents
        ):
            file1 = self._current_dir._get_item(file_name1)
            file2 = self._current_dir._get_item(file_name2)

            if isinstance(file1, File) and isinstance(file2, File):
                content1 = file1._read().splitlines()
                content2 = file2._read().splitlines()

                diff_lines = [
                    f"- {line1}\n+ {line2}"
                    for line1, line2 in zip(content1, content2)
                    if line1 != line2
                ]

                return {"diff_lines": "\n".join(diff_lines)}

        return {"error": f"diff: {file_name1} or {file_name2}: No such file or directory"}

    def mv(self, source: str, destination: str) -> Dict[str, str]:
        """
        Move a file or directory from one location to another.

        Args:
            source (str): Source name of the file or directory to move. Source must be local to the current directory.
            destination (str): The destination name to move the file or directory to. Destination must be local to the current directory and cannot be a path. If destination is not an existing directory like when renaming something, destination is the new file name.

        Returns:
            result (str): The result of the move operation.
        """
        if source not in self._current_dir.contents:
            return {"error": f"mv: cannot move '{source}': No such file or directory"}

        item = self._current_dir._get_item(source)

        if not isinstance(item, (File, Directory)):
            return {"error": f"mv: cannot move '{source}': Not a file or directory"}

        if "/" in destination:
            return {
                "error": f"mv: no path allowed in destination. Only file name and folder name is supported for this operation."
            }

        # Check if the destination is an existing directory
        if destination in self._current_dir.contents:
            dest_item = self._current_dir._get_item(destination)
            if isinstance(dest_item, Directory):
                # Move source into the destination directory
                new_destination = f"{source}"
                if new_destination in dest_item.contents:
                    return {
                        "error": f"mv: cannot move '{source}' to '{destination}/{source}': File exists"
                    }
                else:
                    self._current_dir.contents.pop(source)
                    if isinstance(item, File):
                        dest_item._add_file(source, item.content)
                    else:
                        dest_item._add_directory(source)
                        dest_item.contents[source].contents = item.contents
                    return {"result": f"'{source}' moved to '{destination}/{source}'"}
            else:
                return {
                    "error": f"mv: cannot move '{source}' to '{destination}': Not a directory"
                }
        else:
            # Destination is not an existing directory, move/rename the item
            self._current_dir.contents.pop(source)
            if isinstance(item, File):
                self._current_dir._add_file(destination, item.content)
            else:
                self._current_dir._add_directory(destination)
                self._current_dir.contents[destination].contents = item.contents
            return {"result": f"'{source}' moved to '{destination}'"}

    def rm(self, file_name: str) -> Dict[str, str]:
        """
        Remove a file or directory.

        Args:
            file_name (str): The name of the file or directory to remove.

        Returns:
            result (str): The result of the remove operation.
        """
        if file_name in self._current_dir.contents:
            item = self._current_dir._get_item(file_name)
            if isinstance(item, File) or isinstance(item, Directory):
                self._current_dir.contents.pop(file_name)
                return {"result": f"'{file_name}' removed"}
            else:
                return {
                    "error": f"rm: cannot remove '{file_name}': Not a file or directory"
                }
        else:
            return {"error": f"rm: cannot remove '{file_name}': No such file or directory"}

    def rmdir(self, dir_name: str) -> Dict[str, str]:
        """
        Remove a directory at current directory.

        Args:
            dir_name (str): The name of the directory to remove. Directory must be local to the current directory.

        Returns:
            result (str): The result of the remove operation.
        """
        if dir_name in self._current_dir.contents:
            item = self._current_dir._get_item(dir_name)
            if isinstance(item, Directory):
                if item.contents:  # Check if directory is not empty
                    return {
                        "error": f"rmdir: failed to remove '{dir_name}': Directory not empty"
                    }
                else:
                    self._current_dir.contents.pop(dir_name)
                    return {"result": f"'{dir_name}' removed"}
            else:
                return {"error": f"rmdir: cannot remove '{dir_name}': Not a directory"}
        else:
            return {
                "error": f"rmdir: cannot remove '{dir_name}': No such file or directory"
            }

    def cp(self, source: str, destination: str) -> Dict[str, str]:
        """
        Copy a file or directory from one location to another.

        If the destination is a directory, the source file or directory will be copied
        into the destination directory.

        Both source and destination must be local to the current directory.

        Args:
            source (str): The name of the file or directory to copy.
            destination (str): The destination name to copy the file or directory to.
                            If the destination is a directory, the source will be copied
                            into this directory. No file paths allowed. you may want to copy the original file to the target directory first (cp(x.txt, dir) is equivalent to cp(x.txt, dir/x.txt) that you are attempting).

        Returns:
            result (str): The result of the copy operation or an error message if the operation fails.
        """
        if source not in self._current_dir.contents:
            return {"error": f"cp: cannot copy '{source}': No such file or directory"}

        item = self._current_dir._get_item(source)

        if not isinstance(item, (File, Directory)):
            return {"error": f"cp: cannot copy '{source}': Not a file or directory"}

        if "/" in destination:
            return {
                "error": f"cp: don't allow path in destination. Only file name and folder name is supported for this operation. Instead, as an example, you may want to copy the original file to the target directory first (cp(x.txt, dir) is equivalent to cp(x.txt, dir/x.txt) that you are attempting)."
            }
        # Check if the destination is an existing directory
        if destination in self._current_dir.contents:
            dest_item = self._current_dir._get_item(destination)
            if isinstance(dest_item, Directory):
                # Copy source into the destination directory
                new_destination = f"{destination}/{source}"
                if new_destination in dest_item.contents:
                    return {
                        "error": f"cp: cannot copy '{source}' to '{destination}/{source}': File exists"
                    }
                else:
                    if isinstance(item, File):
                        dest_item._add_file(source, item.content)
                    else:
                        dest_item._add_directory(source)
                        dest_item.contents[source].contents = item.contents.copy()
                    return {"result": f"'{source}' copied to '{destination}/{source}'"}
            else:
                return {
                    "error": f"cp: cannot copy '{source}' to '{destination}': Not a directory"
                }
        else:
            # Destination is not an existing directory, perform the copy
            if isinstance(item, File):
                self._current_dir._add_file(destination, item.content)
            else:
                self._current_dir._add_directory(destination)
                self._current_dir.contents[destination].contents = item.contents.copy()
            return {"result": f"'{source}' copied to '{destination}'"}

    def _navigate_to_directory(
        self, path: Optional[str]
    ) -> Union[Directory, Dict[str, str]]:
        """
        Navigate to a specified directory path from the current directory.

        Args:
            path (str): [Optional] The path to navigate to. Defaults to None (current directory).

        Returns:
            target_directory (Directory or dict): The target directory object or error message.
        """
        if path is None or path == ".":
            return self._current_dir
        elif path == "/":
            return self.root

        dirs = path.strip("/").split("/")
        temp_dir = self._current_dir if not path.startswith("/") else self.root

        for dir_name in dirs:
            next_dir = temp_dir._get_item(dir_name)
            if isinstance(next_dir, Directory):
                temp_dir = next_dir
            else:
                return {"error": f"cd: '{path}': No such file or directory"}

        return temp_dir

class GFSPlugin(BasePlugin):
    """Plugin for the Gorilla File System.
    
    This plugin provides tools for interacting with a simple file system, allowing
    users to navigate directories, create and manipulate files, and perform various
    file operations with dynamic domain updates and type casting.
    """
    
    def __init__(self):
        """Initialize the Gorilla File System plugin."""
        super().__init__()

        self.file_system = GorillaFileSystem()
        self._name = "gfs"
        self._description = "Plugin for file system operations"
        self._tools = self._generate_tool_definitions()
        
        # Cache for dynamic domains - invalidated when file system state changes
        self._domain_cache = None
        self._state_changing_operations = {
            'cd', 'mkdir', 'touch', 'echo', 'mv', 'rm', 'rmdir', 'cp'
        }
    
    @property
    def name(self) -> str:
        """Get the name of the plugin."""
        return self._name
    
    @property
    def description(self) -> str:
        """Get the description of the plugin."""
        return self._description
    
    
    def _generate_tool_definitions(self) -> List[Dict[str, Any]]:
        """Generate tool definitions for the GFS plugin."""
        return [
            {
                "name": "pwd",
                "description": "Print current working directory - shows exactly where you are in the file system. Use this first when starting or when you're unsure of your location. Essential for debugging path-related errors.",
                "arguments": []
            },
            {
                "name": "ls",
                "description": "List directory contents - shows all files and directories in the current location. Use this to see what's available before performing operations. When getting 'file not found' errors, run ls first to verify what exists.",
                "arguments": [
                    {
                        "name": "a",
                        "description": "Show hidden files and directories (those starting with '.'). Set to true to see all items including hidden ones, false for visible items only.",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.3
                        },
                        "required": False,
                        "default": False
                    }
                ]
            },
            {
                "name": "cd",
                "description": "Change to a different directory. IMPORTANT: Only works with single directory names, not paths. Use '..' to go up one level, or a directory name that exists in current location. If getting errors, run 'ls' first to see available directories.",
                "arguments": [
                    {
                        "name": "folder",
                        "description": "Directory name to change to. Must be a single folder name visible in current directory (use 'ls' to check), '..' to go up one level, or '/' for root. Cannot use paths like 'dir1/dir2' - change one directory at a time.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "mkdir",
                "description": "Create a new directory in the current location. Directory is created where you currently are (check with 'pwd'). If getting errors, verify current location and ensure the name doesn't already exist ('ls' to check).",
                "arguments": [
                    {
                        "name": "dir_name",
                        "description": "Name for the new directory. Must be a simple name without special characters (|/\\?%*:><). Cannot contain paths - creates directory in current location only.",
                        "domain": {
                            "type": "string",
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "touch",
                "description": "Create a new empty file in the current directory. File is created where you currently are (check with 'pwd'). If getting 'file exists' errors, run 'ls' first to see existing files.",
                "arguments": [
                    {
                        "name": "file_name",
                        "description": "Name for the new file including extension (e.g., 'document.txt', 'script.py'). Must be a simple filename without special characters, created in current directory only.",
                        "domain": {
                            "type": "string",
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "echo",
                "description": "Display text or write content to a file. When writing to file, creates or overwrites the file in current directory. If file operations fail, check current location with 'pwd' and available space.",
                "arguments": [
                    {
                        "name": "content",
                        "description": "Text content to display or write to file. Can be any string content including multiple lines and special characters.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "file_name",
                        "description": "Optional: filename to write content to in current directory. If omitted, content is displayed on terminal. If file doesn't exist, it will be created. If it exists, content will be overwritten.",
                        "domain": {
                            "type": "string",
                            "importance": 0.7
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "cat",
                "description": "Display the complete contents of a file. File must exist in current directory. If getting 'file not found' errors, run 'ls' first to verify the file exists and check spelling.",
                "arguments": [
                    {
                        "name": "file_name",
                        "description": "Name of the file to display, must exist in current directory. Use 'ls' to see available files if you get errors. Cannot use paths - file must be in current location.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "find",
                "description": "Search for files and directories recursively. Searches from current location downward through all subdirectories. Very useful when you can't locate files - more comprehensive than 'ls'.",
                "arguments": [
                    {
                        "name": "path",
                        "description": "Starting point for search. Use '.' for current directory (default), which searches current location and all subdirectories. Cannot use complex paths.",
                        "domain": {
                            "type": "string",
                            "importance": 0.6
                        },
                        "required": False,
                        "default": "."
                    },
                    {
                        "name": "name",
                        "description": "Optional: pattern to search for in file/directory names. If omitted, returns all files and directories. Use partial names to find items when exact name is unknown.",
                        "domain": {
                            "type": "string",
                            "importance": 0.8
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "wc",
                "description": "Count lines, words, or characters in a file. File must exist in current directory. If getting errors, use 'ls' to verify file exists and 'pwd' to confirm location.",
                "arguments": [
                    {
                        "name": "file_name",
                        "description": "Name of the file to analyze, must exist in current directory. Check with 'ls' if you get file not found errors.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "mode",
                        "description": "What to count: 'l' for lines, 'w' for words, 'c' for characters. Default is 'l' (lines).",
                        "domain": {
                            "type": "finite",
                            "values": ["l", "w", "c"],
                            "importance": 0.6
                        },
                        "required": False,
                        "default": "l"
                    }
                ]
            },
            {
                "name": "sort",
                "description": "Sort the lines in a file alphabetically and display the result. Original file is not modified. File must exist in current directory - use 'ls' to verify if getting errors.",
                "arguments": [
                    {
                        "name": "file_name",
                        "description": "Name of the file to sort, must exist in current directory. Use 'ls' to check available files if operation fails.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "grep",
                "description": "Search for lines containing a specific pattern within a file. File must exist in current directory. If no matches found, returns empty result (not an error).",
                "arguments": [
                    {
                        "name": "file_name",
                        "description": "Name of the file to search in, must exist in current directory. If getting file errors, run 'ls' to verify the file exists.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "pattern",
                        "description": "Text pattern to search for within the file. Case-sensitive search. Returns all lines containing this pattern.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "du",
                "description": "Show disk usage of current directory and its contents. Calculates total size of all files and subdirectories. Use 'pwd' first to confirm which directory you're analyzing.",
                "arguments": [
                    {
                        "name": "human_readable",
                        "description": "Format output for easy reading. True shows sizes in KB/MB/GB format, false shows raw byte count.",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.4
                        },
                        "required": False,
                        "default": False
                    }
                ]
            },
            {
                "name": "tail",
                "description": "Display the last few lines of a file. Useful for viewing end of log files or large documents. File must exist in current directory - check with 'ls' if getting errors.",
                "arguments": [
                    {
                        "name": "file_name",
                        "description": "Name of the file to display, must exist in current directory. Use 'ls' to verify file exists if you encounter errors.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "lines",
                        "description": "Number of lines to display from the end of the file (1-100). Default is 10 lines. If file has fewer lines, shows entire file.",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 100],
                            "importance": 0.5
                        },
                        "required": False,
                        "default": 10
                    }
                ]
            },
            {
                "name": "diff",
                "description": "Compare two files line by line and show differences. Both files must exist in current directory. If getting errors, use 'ls' to verify both files exist and check their names.",
                "arguments": [
                    {
                        "name": "file_name1",
                        "description": "Name of the first file to compare, must exist in current directory. Check with 'ls' if you get file not found errors.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "file_name2",
                        "description": "Name of the second file to compare, must exist in current directory. Verify existence with 'ls' if operation fails.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "mv",
                "description": "Move or rename files/directories within current directory only. IMPORTANT: Both source and destination must be simple names, no paths allowed. If getting errors, run 'ls' to verify source exists and 'pwd' to confirm location.",
                "arguments": [
                    {
                        "name": "source",
                        "description": "Name of file or directory to move/rename, must exist in current directory. Use 'ls' to see available items if you get 'not found' errors. Cannot be a path.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "destination",
                        "description": "New name or target directory for the item. Must be in current directory only - no paths allowed. If destination is an existing directory, source will be moved into it.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "rm",
                "description": "Remove (delete) a file or directory permanently. Item must exist in current directory. CAUTION: This action cannot be undone. If getting errors, use 'ls' to verify the item exists.",
                "arguments": [
                    {
                        "name": "file_name",
                        "description": "Name of file or directory to delete, must exist in current directory. Use 'ls' to confirm existence before deletion. Cannot use paths.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "rmdir",
                "description": "Remove an empty directory. Directory must exist in current location and be completely empty. If getting 'not empty' errors, use 'ls' to check contents or 'rm' to remove contents first.",
                "arguments": [
                    {
                        "name": "dir_name",
                        "description": "Name of empty directory to remove, must exist in current directory. Directory must be empty - use 'ls' to verify no contents remain.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "cp",
                "description": "Copy files or directories within current directory only. Creates duplicate with new name or copies into existing directory. If getting errors, use 'ls' to verify source exists and check available space.",
                "arguments": [
                    {
                        "name": "source",
                        "description": "Name of file or directory to copy, must exist in current directory. Use 'ls' to verify existence if you get 'not found' errors. Cannot be a path.",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "destination",
                        "description": "Name for the copy or target directory. Must be in current directory only - no paths allowed. If destination is existing directory, source is copied into it. You may want to copy the original file to the target directory first (cp(x.txt, dir) is equivalent to cp(x.txt, dir/x.txt) that you are attempting).",
                        "domain": {
                            "type": "string",
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            }
        ]
        
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get the list of tools provided by this plugin."""
        return self._tools
    
    def _invalidate_domain_cache(self):
        """Invalidate the domain cache when file system state changes."""
        self._domain_cache = None
    
    def _update_dynamic_domains(self) -> Dict[str, Any]:
        """Update domains based on current file system state."""
        if self._domain_cache is not None:
            return self._domain_cache
        
        try:
            # Get current directory contents
            current_contents = self.file_system.ls().get("current_directory_content", [])
            
            # Separate files and directories
            files = []
            directories = []
            for item_name in current_contents:
                item = self.file_system._current_dir._get_item(item_name)
                if isinstance(item, File):
                    files.append(item_name)
                elif isinstance(item, Directory):
                    directories.append(item_name)
            
            # Build domain updates
            updates = {}
            
            # Update cd domain - only directories plus special values
            updates["cd.folder"] = {
                "type": "finite",
                "values": directories + ["..", "/"]
            }
            
            # Update file-based operations domains
            file_operations = ["cat", "wc", "sort", "grep", "tail"]
            for op in file_operations:
                updates[f"{op}.file_name"] = {
                    "type": "finite",
                    "values": files
                }
            
            # Update diff domains
            updates["diff.file_name1"] = {
                "type": "finite", 
                "values": files
            }
            updates["diff.file_name2"] = {
                "type": "finite",
                "values": files
            }
            
            # Update mv and cp source domains
            all_items = files + directories
            updates["mv.source"] = {
                "type": "finite",
                "values": all_items
            }
            updates["cp.source"] = {
                "type": "finite", 
                "values": all_items
            }
            
            # Update mv and cp destination domains (can be existing items for overwrite/move-into)
            updates["mv.destination"] = {
                "type": "finite",
                "values": all_items
            }
            updates["cp.destination"] = {
                "type": "finite",
                "values": all_items
            }
            
            # Update rm domain
            updates["rm.file_name"] = {
                "type": "finite",
                "values": all_items
            }
            
            # Update rmdir domain - only directories
            updates["rmdir.dir_name"] = {
                "type": "finite",
                "values": directories
            }
            
            # Cache the result
            self._domain_cache = updates
            return updates
            
        except Exception as e:
            logger.error(f"Error updating dynamic domains: {e}")
            return {}
    
    def initialize_from_config(self, config_data: Dict[str, Any]) -> bool:
        """Initialize the file system from configuration data."""
        if "GorillaFileSystem" in config_data:
            gfs_config = config_data["GorillaFileSystem"]
            self.file_system._load_scenario(gfs_config)
            self._invalidate_domain_cache()  # Invalidate cache after loading
            return True
        return False
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with the given parameters."""
        # Cast parameters first using the base class method
        casted_params, cast_error = self._cast_parameters(tool_name, parameters)
        if cast_error:
            return {
                "success": False,
                "message": f"Parameter casting error: {cast_error}",
                "error": "TYPE_CASTING_ERROR"
            }
        
        # Validate parameters
        is_valid, error = self.validate_tool_call(tool_name, casted_params)
        if not is_valid:
            return {
                "success": False,
                "message": error,
                "error": "INVALID_PARAMETERS"
            }
        
        try:
            # Call the corresponding method on the file system
            gfs_method = getattr(self.file_system, tool_name)
            result = gfs_method(**casted_params)
            
            # Invalidate domain cache if this was a state-changing operation
            if tool_name in self._state_changing_operations:
                self._invalidate_domain_cache()
            
            # Handle different result formats
            if result is None:
                return {
                    "success": True,
                    "message": f"Successfully executed {tool_name}"
                }
            elif isinstance(result, dict) and "error" in result:
                return {
                    "success": False,
                    "message": result["error"],
                    "error": "OPERATION_FAILED"
                }
            else:
                return {
                    "success": True,
                    "message": f"Successfully executed {tool_name}",
                    "output": result
                }
        except Exception as e:
            logger.exception(f"Error executing {tool_name}: {e}")
            return {
                "success": False,
                "message": str(e),
                "error": "EXECUTION_ERROR"
            }
    
    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate a tool call before execution."""
        # Find the tool definition
        tool_def = None
        for tool in self._tools:
            if tool["name"] == tool_name:
                tool_def = tool
                break
        
        if not tool_def:
            return False, f"Unknown tool: {tool_name}"
        
        # Check required arguments
        for arg_def in tool_def.get("arguments", []):
            if arg_def.get("required", True) and arg_def["name"] not in parameters:
                return False, f"Missing required argument: {arg_def['name']}"
            
            # If the argument is provided, validate its value
            if arg_def["name"] in parameters and parameters[arg_def["name"]] != "<UNK>":
                value = parameters[arg_def["name"]]
                
                # Validate based on domain type
                domain = arg_def.get("domain", {})
                domain_type = domain.get("type", "string")
                
                if domain_type == "numeric_range":
                    try:
                        val = float(value)
                        start, end = domain.get("values", [1, 100])
                        if not (start <= val <= end):
                            return False, f"Value {value} for {arg_def['name']} is out of range [{start}, {end}]"
                    except (ValueError, TypeError):
                        return False, f"Invalid numeric value for {arg_def['name']}: {value}"
                
                elif domain_type == "finite":
                    # Get dynamic domain values if data_dependent
                    if domain.get("data_dependent"):
                        dynamic_domains = self._update_dynamic_domains()
                        domain_key = f"{tool_name}.{arg_def['name']}"
                        if domain_key in dynamic_domains:
                            valid_values = dynamic_domains[domain_key].get("values", [])
                        else:
                            valid_values = domain.get("values", [])
                    else:
                        valid_values = domain.get("values", [])
                    
                    if value not in valid_values:
                        values_str = ", ".join(str(v) for v in valid_values)
                        return False, f"Invalid value for {arg_def['name']}: {value}. Expected one of: {values_str}"
                
                elif domain_type == "boolean":
                    if not isinstance(value, bool) and value not in [True, False, "true", "false", "True", "False"]:
                        return False, f"Invalid boolean value for {arg_def['name']}: {value}"
        
        return True, None
    
    def get_domain_updates_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update tool domains based on context."""
        # Initialize from config if available
        if "initial_config" in context and hasattr(self, "initialize_from_config"):
            self.initialize_from_config(context["initial_config"])
        
        # Return dynamic domain updates
        return self._update_dynamic_domains()
    
    def get_uncertainty_context(self) -> Dict[str, Any]:
        """Get file system-specific context for uncertainty calculation."""
        try:
            contents = self.file_system.ls().get("current_directory_content", [])
            return {
                "current_directory": self.file_system.pwd().get("current_working_directory", "/"),
                "available_items": contents
            }
        except Exception as e:
            logger.error(f"Error getting uncertainty context: {e}")
            return {}
    
    def get_prompt_templates(self) -> Dict[str, str]:
        """Get file system-specific prompt templates."""
        return {
            "tool_selection": """
You are an AI assistant that helps users with file system operations.

Conversation history:
{conversation_history}

User query: "{user_query}"

Available tools:
{tool_descriptions}

Please analyze the user's query and determine which tool(s) should be called to fulfill the request.
For each tool, specify all required parameters. If a parameter is uncertain, use "<UNK>" as the value.

Think through this step by step:
1. What is the user trying to do with the file system?
2. Which file system operation(s) are needed to complete this task?
3. What parameters are needed for each operation?
4. Which parameters can be determined from the query, and which are uncertain?

Return your response as a JSON object with the following structure:
{
  "reasoning": "Your step-by-step reasoning about what tools to use and why",
  "tool_calls": [
    {
      "tool_name": "name_of_tool",
      "arguments": {
        "arg1": "value1",
        "arg2": "<UNK>"
      }
    }
  ]
}
""",
            "question_generation": """
You are an AI assistant that helps users with file system operations.

Conversation history:
{conversation_history}

Original user query: "{user_query}"

I've determined that the following tool calls are needed, but some arguments are uncertain:

Tool Calls:
{tool_calls}

Uncertain Arguments:
{uncertain_args}

Your task is to generate clarification questions that would help resolve the uncertainty about specific arguments.

Instructions:
1. Generate questions that are clear, specific, and directly address the uncertain arguments
2. Each question should target one or more specific arguments
3. Questions should be conversational and easy for a user to understand
4. For each question, specify which tool and argument(s) it aims to clarify

Return your response as a JSON object with the following structure:
{
  "questions": [
    {
      "question": "A clear question to ask the user",
      "target_args": [["tool_name", "arg_name"], ["tool_name", "other_arg_name"]]
    }
  ]
}
"""
        }