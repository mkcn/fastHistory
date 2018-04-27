

class DatabaseMYSQL(object):
    """
    TODO implement
    """

    def __init__(self, project_directory):
        return NotImplementedError

    def get_all_data(self, filter=None):
        return NotImplementedError

    def get_last_n_elements_with_simple_search(self, filter=None, n=50):
        return NotImplementedError

    def get_last_n_elements_with_advanced_search(self, cmd_filter=None, description_filter=None, tags_filter=None, n=50):
        return NotImplementedError

    def add_element(self, cmd, description, tags):
        """
        insert a new element in the database,
        if it already in the db just increase the counter
        if the description is different it updates it
        if there are new tags it updates the tags string

        :param cmd:             bash command
        :param description:     description
        :param tags:            array of tag
        :return:                true if the command has been store successfully
        """
        return NotImplementedError

    def update_position_element(self, cmd):
        """
        TODO
        :param cmd:
        :return:
        """
        return NotImplementedError

    def remove_element(self, cmd):
        """
        delete specific command

        :param cmd:     cmd to delete
        :return:        true is successfully deleted, false otherwise
        """
        return NotImplementedError
