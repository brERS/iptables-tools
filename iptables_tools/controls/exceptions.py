class ExceptionsUtils(Exception):

    def __init__(
        self,
        method_name = None,
        command = None,
        return_message = None,
        banner_name = None,
        banner_message_plus = None,
        exception_name = None
    ):
        self.method_name = method_name
        self.command = command
        self.return_message = return_message
        self.banner_name = banner_name
        self.banner_message_plus = banner_message_plus
        self.exception_name = exception_name

        self.format_return_message()

    def __str__(self):
        return self.message

    def format_return_message(self):        
        input = self.format_input()        
        banner = self.banners()

        message = {
            'CommandCalledError': f"Command '{input}' returned {self.return_message}\n{banner}",
            'CommandPermissionError': f"Command '{input}' returned {self.return_message}\n{banner}",
            'CommandNotFound': f"Command '{input}' not found\n{banner}",
            'RunCommandError': f"Command '{input}' unselected option\n{banner}",
            'CopyFileError': f"Error copying file '{input}'\n{banner}",
            'ValueMandatoryError': f"Value '{self.return_message}' is mandatory.\n{banner}"
        }   

        self.message = message.get(self.exception_name)

    def format_input(self):
        return f"{self.method_name} {self.command}" if self.command else self.method_name

    def banners(self):
        banners = {
            'super_user': "Try running the command as super user.",
            'run_unselected_option': 'To view the available options run\niptables-tools run -h',
            'ValueMandatoryError': f'Review the configuration file default.toml:\n{self.banner_message_plus}',
        }

        if not banners.get(self.banner_name):
            return '\n'

        h = '#' * len(banners.get(self.banner_name))
        return f"{h}\n{banners.get(self.banner_name)}\n{h}"

class CommandNotFound(ExceptionsUtils):
    def __init__(
        self,
        method_name = None,
        command = None,
        return_message = None,
        banner_name = None
    ):
        super().__init__(
            method_name,
            command,
            return_message,
            banner_name,
            'CommandNotFound'
        )

class CommandCalledError(ExceptionsUtils):
    def __init__(
        self,
        method_name = None,
        command = None,
        return_message = None,
        exception_name = 'CommandCalledError'
    ):
        super().__init__(
            method_name = method_name,
            command = command,
            return_message = return_message,
            exception_name = exception_name
        )

class CommandPermissionError(ExceptionsUtils):
    def __init__(
        self,
        method_name = None,
        command = None,
        return_message = None,
        banner_name = 'super_user'
    ):
        super().__init__(
            method_name,
            command,
            return_message,
            banner_name,
            'CommandPermissionError'
        )

class RunCommandError(ExceptionsUtils):
    def __init__(
        self,
        method_name = None,
        command = None,
        return_message = None,
        banner_name = 'run_unselected_option',
        exception_name = 'RunCommandError'
    ):
        super().__init__(
            method_name = method_name,
            command = command,
            return_message = return_message,
            banner_name = banner_name,
            exception_name = exception_name
        )

class CopyFileError(ExceptionsUtils):
    def __init__(
        self,
        method_name = None,
        command = None,
        return_message = None,
        banner_name = None
    ):
        super().__init__(
            method_name,
            command,
            return_message,
            banner_name,
            'CopyFileError'
        )

class ValueMandatoryError(ExceptionsUtils):
    def __init__(
        self,
        return_message = None,
        banner_name = 'ValueMandatoryError',
        banner_message_plus = None,
        exception_name = 'ValueMandatoryError',
    ):
        super().__init__(
            return_message = return_message,
            banner_name = banner_name,
            banner_message_plus = banner_message_plus,
            exception_name = exception_name
        )