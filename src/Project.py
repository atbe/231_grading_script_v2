import re
import subprocess
import getpass

# for testing purposes only.
EDITOR="gedit"

class Project:
    """
    Used to model Project objects.

    Attributes
    -----------
    project_path : Path
        Used to indicate the path of the project folder.

    number : int
        Project number.

    py_paths : list<Path>
        List of Paths of all the .py files for a given project.

    all_file_paths : list<Path>
        List of paths of all the files for a given project.

    is-graded : bool
        Indicates whether project is graded or not.

    scoresheet_path : Path
        Path to scoresheet file.
    """

    def __init__(self, path):
        """
        Default construtor for Project object.
        """
        self.project_path = path
        self.number = int(path.name)
        self.py_paths = self.get_py_paths()
        self.all_file_paths = self.get_all_file_paths()
        self.is_graded = self.check_graded()
        self.scoresheet_path = self.get_scoresheet()

    def get_py_paths(self):
        """
        Populates py_paths with paths to all py files.

        Returns
        -------
        list<Path>
            List of paths of all the .py files in the project directory
        """
        py_paths = []
        pattern = r"^[^\.]\w+\.py"
        for path in self.project_path.iterdir():
            match = re.search(pattern, path.name)
            if match:
                # print(path.name)
                py_paths.append(path)

        return py_paths

    def get_all_file_paths(self):
        """
        Populates all_file_paths member with paths to all the files.

        Returns
        ------
        list<Path>
            List of paths of all files in the project directory except .graded.
        """
        files = []
        for path in self.project_path.iterdir():
            if path.is_file() and path.name != ".graded":
                # print("Adding {} to project files.".format(path.name))
                files.append(path)
        return files

    def check_graded(self):
        """
        Checks if a project is graded.

        Returns
        -------
        bool
            True if .graded file exists in the project directory.
        """

        return (self.project_path / ".graded").exists()

    def open_scoresheet(self):
        """
        Opens the scoresheet using EDITOR in a subprocess.
        """
        subprocess.Popen([EDITOR, str(self.scoresheet_path)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def open_files(self):
        """
        Opens all the files in the list self.all_file_paths using EDITOR in a subprocess.
        """
        # TODO: Implement checking for when project does not exist

        input("Press enter to open the files in {}.".format(EDITOR))
        for path in self.all_file_paths:
            # print("Project graded = ", project.is_graded)
            print("Opening: ", str(path))

            subprocess.Popen([EDITOR, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def get_scoresheet(self):
        """
        Grabs the scoresheet file if it exists. Behaviour is undefined atm if .graded does not exist

        Returns
        -------
        Path
            Path object pointing to score file.
        """
        score_file_paths = list(self.project_path.glob("./*.score"))
        if len(score_file_paths) < 1 or len(score_file_paths) > 1:
            # print("ERROR: Student does not have a score file.")
            # TODO: Handle missing score file
            # raise Exception
            return
        score_file_path = score_file_paths[0]

        return score_file_path

    def get_project_total_score(self):
        """
        Uses regex to pick up all __#__ patterns and sums up all the scores (except the first).
        The first number in the list is the total score (which may or may not be 0).

        Will match any number of surrounding underscores (must be at least 1 underscore).

        Returns
        -------
        int
            Total number of points summed by checking all __#__ patterns.
        list<int>
            List of all the scores found in the file.
        """
        with open(str(self.scoresheet_path), "r") as file_object_read:
            lines = file_object_read.read()
            pattern_list = (re.findall(r'_+\d+_+', lines))
            # print (pattern_list)
            points_list = list()
            for elements in pattern_list:
                points = elements.split('_')
                # print (points)
                point_position = int(len(points) / 2)
                points_list.append(int(points[point_position]))
            # print (points_list)
            # Subtract the current project score from the total incase this is a regrading
            total = sum(points_list) - points_list[0]
            # print (total)
        return total, points_list

    def write_project_score(self, total, points_list):
        """
        Writes the score to the scoresheet file.

        Parameters
        ----------
        total : int
            The total points rewarded to the student
        points_list : list<int>
            List of all the scores found from the scoresheet. FIrst item should be the current total score.
        """
        with open(str(self.scoresheet_path), 'r+') as file_object_write:
            lines = file_object_write.readlines()
            for i, line in enumerate(lines):
                if '__' in line and 'Score:' in line:
                    # print(line)
                    line = line.replace("__{:02d}__".format(points_list[0]), "__{}__".format(total))
                    # print(line)
                    lines[i] = line
            file_object_write.seek(0)
            file_object_write.writelines(lines)
        # print("TOTAL = ", total)

    def check_scoresheet(self):
        """
        Grabs total points and list of all points.
        Passes that data to write_project_score in order to write the score.

        Returns
        -------
        int
            Total number of points awarded to student.
        """
        score_total, points_list = self.get_project_total_score()
        fix_choice = "wut"
        if score_total != points_list[0] and (score_total != 0):
            while fix_choice not in "yes no":
                fix_choice = input("\nThe score and sum do not match.\nGiven Score: {}\nComputed Score: {}\nWould you like me to fix that? (Yes/No): ".format(points_list[0], score_total)).lower().strip()
            if fix_choice == "yes":
                self.write_project_score(score_total, points_list)
            else:
                return points_list[0] # The point total at the top of the file
        else:
            self.write_project_score(score_total, points_list)

        # print("Calculated score: {:02d}".format(score_total))
        return points_list[0]


    def mark_as_graded(self):
        """
        Mark the project as graded by writing a .graded file
        """
        ta_username = getpass.getuser()
        print("Graded by", ta_username)
        with open("{}/.graded".format(str(self.project_path.resolve())), "w") as scoresheet:
            scoresheet.write(ta_username)
            self.is_graded = True
